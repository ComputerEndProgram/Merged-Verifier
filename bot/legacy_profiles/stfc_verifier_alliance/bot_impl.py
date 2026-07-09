import logging
import os
from typing import Optional

import discord
from discord.ext import commands

from bot.config.settings import Settings
from bot.core.bot_base import BaseBot
from bot.core.store import _support_ticket_text
from bot.core.views import RankConfirmationView

log = logging.getLogger("veil_bot")


def get_rank_tier(rank: Optional[str]) -> Optional[str]:
    tiers = {
        "agent": "base", "operative": "base", "premier": "base",
        "commodore": "commodore", "admiral": "admiral",
    }
    if not rank:
        return None
    return tiers.get(rank.lower())


class STFCVerifierAllianceBot(BaseBot):
    """STFC Verifier Alliance bot - rank-based with server check."""

    def __init__(self, settings: Settings):
        super().__init__(settings, "stfc_verifier_alliance")

    def _build_nickname(self, player_data) -> str:
        if player_data.alliance_tag:
            nick = f"[{player_data.alliance_tag}] {player_data.username}"
        else:
            nick = player_data.username
        if len(nick) > 32:
            nick = nick[:32]
        return nick

    async def _assign_roles(self, member: discord.Member, player_data, interaction: discord.Interaction):
        feedback = []
        confirmation_view = None

        stfc_server_id = self.settings.stfc_server_number
        if stfc_server_id and player_data.server != stfc_server_id:
            await interaction.followup.send(
                f"❌ Your character must be on STFC Server {stfc_server_id}. "
                f"You are currently on Server {player_data.server}.",
                ephemeral=True,
            )
            log.warning(
                f"[WIZARD] User {member.id} attempted verification on wrong "
                f"server: {player_data.server} (expected {stfc_server_id})"
            )
            return feedback, confirmation_view

        guild = self.get_guild(self.settings.guild_id)
        member_role = guild.get_role(self.settings.member_role_id) if self.settings.member_role_id and guild else None
        commodore_role = guild.get_role(self.settings.commodore_role_id) if self.settings.commodore_role_id and guild else None
        admiral_role = guild.get_role(self.settings.admiral_role_id) if self.settings.admiral_role_id and guild else None

        rank_tier = get_rank_tier(getattr(player_data, "rank", None))

        if not member_role:
            feedback.append(f"❌ Member role {self.settings.member_role_id} not found - cannot assign ranks")
            log.error(f"[WIZARD] Member role {self.settings.member_role_id} not found for {member.id}")
        else:
            try:
                if rank_tier == "base":
                    await member.add_roles(member_role, reason=f"Verified rank: {player_data.rank}")
                    feedback.append(f"✅ Base role assigned (rank: {player_data.rank})")
                    if commodore_role and commodore_role in member.roles:
                        await member.remove_roles(commodore_role, reason="Rank downgrade")
                    if admiral_role and admiral_role in member.roles:
                        await member.remove_roles(admiral_role, reason="Rank downgrade")
                    log.info(f"[WIZARD] Assigned base role to {member.id} (rank: {player_data.rank})")

                elif rank_tier in ("commodore", "admiral"):
                    await member.add_roles(member_role, reason=f"Verified rank: {player_data.rank}")
                    feedback.append(f"✅ Base role assigned (rank: {player_data.rank})")
                    confirmation_view = RankConfirmationView(
                        member.id, member.name, player_data.rank,
                        player_data.username, player_data.alliance_tag or "N/A",
                        self.settings, self.store, lambda: self.get_guild(self.settings.guild_id),
                        self._t,
                    )
                    role_name = "Commodore" if rank_tier == "commodore" else "Admiral"
                    feedback.append(f"⏳ {role_name} role pending admin confirmation...")
                    log.info(f"[WIZARD] Created confirmation for {member.id}: {role_name} rank")
            except Exception as e:
                feedback.append(f"❌ Error assigning roles: {e}")
                log.error(f"[WIZARD] Error assigning roles to {member.id}: {e}")

        return feedback, confirmation_view

    def _build_summary_embed(self, player_data) -> discord.Embed:
        embed = discord.Embed(
            title="✅ Step 3: Verify Information",
            description="Please review your information below. If everything looks correct, click **Complete**.",
            colour=discord.Colour.gold(),
        )
        embed.add_field(name="Player Name", value=f"{player_data.username}", inline=True)
        embed.add_field(name="Level", value=f"{player_data.level}", inline=True)
        embed.add_field(name="Server", value=f"{player_data.server}", inline=True)
        embed.add_field(name="Alliance", value=player_data.alliance_tag or "None", inline=True)
        embed.add_field(name="Rank", value=getattr(player_data, "rank", "Unknown"), inline=True)
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
        embed.add_field(name="Rank", value=getattr(player_data, "rank", "N/A"), inline=True)
        embed.add_field(name="Level", value=f"{player_data.level}", inline=True)
        embed.add_field(name="Server", value=f"{player_data.server}", inline=True)
        embed.add_field(name="Alliance", value=player_data.alliance_tag or "None", inline=True)
        return embed

    async def _handle_update(self, member: discord.Member, user_id: int, stfc_link: str, player_data):
        old_data = self.store.get_player_data(user_id)
        if not old_data:
            return
        old_rank = old_data[4] if len(old_data) > 4 else None

        new_nick = self._build_nickname(player_data)
        if member.nick != new_nick:
            try:
                await member.edit(nick=new_nick)
                log.info(f"[UPDATE] Updated nickname for {member.id} ({member.name}): {new_nick}")
            except discord.Forbidden:
                log.debug(f"[UPDATE] Could not update nickname for {member.id} (Forbidden)")
            except Exception as e:
                log.warning(f"[UPDATE] Error updating nickname for {member.id}: {e}")

        if old_rank != player_data.rank:
            log.info(f"[UPDATE] Rank change detected for {member.id} ({member.name}): {old_rank} → {player_data.rank}")
            guild = self.get_guild(self.settings.guild_id)
            confirmation_view = RankConfirmationView(
                member.id, member.name, player_data.rank,
                player_data.username, player_data.alliance_tag or "N/A",
                self.settings, self.store, lambda: self.get_guild(self.settings.guild_id),
                self._t,
            )
            admin_ping = f"<@&{self.settings.admin_role_id}>" if self.settings.admin_role_id else "Admins"
            alliance_display = f"[{player_data.alliance_tag}]" if player_data.alliance_tag else "N/A"
            confirm_embed = discord.Embed(
                title="🔔 Rank Change Detected - Confirmation Required",
                description=f"{admin_ping}, please confirm this rank change.",
                color=discord.Color.orange(),
            )
            confirm_embed.add_field(
                name="Player",
                value=f"{member.mention} ({player_data.username})",
                inline=False,
            )
            confirm_embed.add_field(name="Previous Rank", value=old_rank or "N/A", inline=True)
            confirm_embed.add_field(name="New Rank", value=player_data.rank or "N/A", inline=True)
            confirm_embed.add_field(name="Alliance", value=alliance_display, inline=True)
            log_msg = await self.post_to_log_channel(embed=confirm_embed, view=confirmation_view)
            if log_msg:
                confirmation_view.log_message = log_msg
                confirmation_view.confirmation_message_id = log_msg.id
                confirmation_view.confirmation_channel_id = log_msg.channel.id
                self.store.save_pending_rank_confirmation(
                    log_msg.id, log_msg.channel.id,
                    member.id, str(member), player_data.rank,
                    player_data.username,
                    player_data.alliance_tag or "N/A",
                )

        self.store.store_stfc_player(user_id, stfc_link, player_data)


def run() -> None:
    settings = Settings.from_env()
    bot = STFCVerifierAllianceBot(settings)
    bot.run(settings.discord_token)


if __name__ == "__main__":
    run()
