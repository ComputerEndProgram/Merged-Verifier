import logging
import os
from typing import Optional

import discord
from discord.ext import commands

from bot.config.settings import Settings
from bot.core.bot_base import BaseBot
from bot.core.store import _support_ticket_text

log = logging.getLogger("veil_bot")


class VeilSecurityBot(BaseBot):
    """Veil Security bot - OPS level based verification."""

    def __init__(self, settings: Settings):
        super().__init__(settings, "veil_security")

    def _build_nickname(self, player_data) -> str:
        if player_data.alliance_tag:
            nick = f"[{player_data.server}] {player_data.alliance_tag} - {player_data.username}"
        else:
            nick = f"[{player_data.server}] {player_data.username}"
        if len(nick) > 32:
            nick = nick[:32]
        return nick

    async def _assign_roles(self, member: discord.Member, player_data, interaction: discord.Interaction):
        feedback = []
        confirmation_view = None

        guild = self.get_guild(self.settings.guild_id)
        server_role = discord.utils.find(
            lambda r: r.name == str(player_data.server),
            guild.roles if guild else [],
        )

        if server_role:
            try:
                await member.add_roles(server_role, reason=f"Verified via stfc.pro (server {player_data.server})")
                feedback.append(f"✅ Server role assigned: `{server_role.name}`")
                log.info(f"[WIZARD] Assigned server role {server_role.name} to {member.id}")
            except Exception as e:
                feedback.append(f"⚠️ Error assigning server role: {e}")
                log.warning(f"[WIZARD] Error assigning server role to {member.id}: {e}")
        else:
            feedback.append(f"⚠️ Server role `{player_data.server}` not found")
            await self.post_admin_notification(
                f"❌ Missing server role `{player_data.server}` for user {member.mention}"
            )
            log.error(f"[WIZARD] Server role {player_data.server} not found")

        min_ops = self.settings.minimum_ops_level or 71
        ops_role_id = self.settings.ops71_plus_role_id
        if player_data.level >= min_ops and ops_role_id:
            ops_role = guild.get_role(ops_role_id) if guild else None
            if ops_role:
                try:
                    await member.add_roles(
                        ops_role,
                        reason=f"Verified via stfc.pro - Level {player_data.level} >= {min_ops}",
                    )
                    feedback.append(f"✅ OPS 71+ role assigned")
                    log.info(f"[WIZARD] Assigned OPS 71+ role to {member.id} (level {player_data.level})")
                except Exception as e:
                    feedback.append(f"⚠️ Error assigning OPS role: {e}")
                    log.warning(f"[WIZARD] Error assigning OPS role to {member.id}: {e}")
        else:
            feedback.append(
                f"⚠️ OPS level {player_data.level} < {min_ops} - OPS role not assigned"
            )
            log.info(
                f"[WIZARD] Skipped OPS role for {member.id} (level {player_data.level} < {min_ops})"
            )

        return feedback, confirmation_view

    def _build_summary_embed(self, player_data) -> discord.Embed:
        min_ops = self.settings.minimum_ops_level or 71
        embed = discord.Embed(
            title="✅ Step 3: Verify Information",
            description="Please review your information below. If everything looks correct, click **Complete**.",
            colour=discord.Colour.gold(),
        )
        embed.add_field(name="Player Name", value=f"{player_data.username}", inline=True)
        embed.add_field(name="OPS Level", value=f"{player_data.level}", inline=True)
        embed.add_field(name="Server", value=f"{player_data.server}", inline=True)
        embed.add_field(name="Alliance", value=player_data.alliance_tag or "None", inline=True)
        ops_eligible = "✅ Yes" if player_data.level >= min_ops else f"❌ No (Level {player_data.level} < {min_ops})"
        embed.add_field(name="Eligible for OPS 71+ Role", value=ops_eligible, inline=False)
        embed.set_footer(text="Review the data above and click Complete or Restart")
        return embed

    def _build_log_embed(self, member: discord.Member, player_data, session: dict) -> discord.Embed:
        embed = discord.Embed(
            title="✅ Verification Successful",
            description=f"**{member.mention}** verified as **{player_data.username}**",
            colour=discord.Colour.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Player", value=f"{player_data.username}", inline=True)
        embed.add_field(name="OPS Level", value=f"{player_data.level}", inline=True)
        embed.add_field(name="Server", value=f"{player_data.server}", inline=True)
        embed.add_field(name="Alliance", value=player_data.alliance_tag or "None", inline=True)
        return embed

    async def _handle_update(self, member: discord.Member, user_id: int, stfc_link: str, player_data):
        old_data = self.store.get_player_data(user_id)
        old_level = old_data[1] if old_data else None

        new_nick = self._build_nickname(player_data)
        if member.nick != new_nick:
            try:
                await member.edit(nick=new_nick)
                log.info(f"[UPDATE] Updated nickname for {member.id} ({member.name}): {new_nick}")
            except discord.Forbidden:
                log.debug(f"[UPDATE] Could not update nickname for {member.id} (Forbidden)")
            except Exception as e:
                log.warning(f"[UPDATE] Error updating nickname for {member.id}: {e}")

        if old_level != player_data.level:
            log.info(f"[UPDATE] {member.id} ({member.name}) level changed: {old_level} → {player_data.level}")
            min_ops = self.settings.minimum_ops_level or 71
            ops_role_id = self.settings.ops71_plus_role_id
            has_ops_role = any(r.id == ops_role_id for r in member.roles) if ops_role_id else False

            if player_data.level >= min_ops and not has_ops_role and ops_role_id:
                guild = self.get_guild(self.settings.guild_id)
                ops_role = guild.get_role(ops_role_id) if guild else None
                if ops_role:
                    try:
                        await member.add_roles(
                            ops_role,
                            reason=f"Auto-promoted to OPS 71+ (level {player_data.level})",
                        )
                        log.info(f"[UPDATE] Promoted {member.id} ({member.name}) to OPS 71+ (level {player_data.level})")
                    except Exception as e:
                        log.warning(f"[UPDATE] Could not assign OPS role to {member.id}: {e}")

        self.store.store_stfc_player(user_id, stfc_link, player_data)


def run() -> None:
    settings = Settings.from_env()
    bot = VeilSecurityBot(settings)
    bot.run(settings.discord_token)


if __name__ == "__main__":
    run()
