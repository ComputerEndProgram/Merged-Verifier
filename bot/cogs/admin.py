import logging

import discord
from discord import app_commands
from discord.ext import commands

from bot.core.store import _support_ticket_text
from bot.core.i18n.translator import Translator
from bot.core.views import StartWizardView

log = logging.getLogger("veil_bot")


class AdminCog(commands.Cog):
    """Handles admin recall (guild-only)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._t = Translator(bot.settings.default_language)

    recall = app_commands.Group(name="recall", description="Recall commands")

    @recall.command(
        name="verification",
        description="[ADMIN] Recall a user's verification, remove all roles, and alert them",
    )
    @app_commands.guild_only()
    @app_commands.describe(
        user="The user to recall verification for",
        reason="Reason for the recall",
    )
    async def recall_verification_cmd(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        reason: str = "No reason provided",
    ):
        if not interaction.user or not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message(
                "❌ Could not verify your permissions.",
                ephemeral=True,
            )

        settings = self.bot.settings
        store = self.bot.store
        _t = self._t
        locale = interaction.locale

        admin_role = interaction.guild.get_role(settings.admin_role_id) if interaction.guild and settings.admin_role_id else None
        if not admin_role or admin_role not in interaction.user.roles:
            return await interaction.response.send_message(
                "❌ You do not have permission to use this command.",
                ephemeral=True,
            )

        await interaction.response.defer(thinking=True)

        player_data = store.get_player_data(user.id)
        if not player_data:
            return await interaction.followup.send(
                f"❌ **{user.mention}** has not verified their STFC account yet.",
                ephemeral=True,
            )

        guild = self.bot.get_guild(settings.guild_id)
        if not guild:
            return await interaction.followup.send("❌ Could not access the server.", ephemeral=True)

        member = guild.get_member(user.id)
        if not member:
            return await interaction.followup.send(
                "❌ User is not in the server or could not be found.",
                ephemeral=True,
            )

        player_data = store.get_player_data(user.id)

        try:
            roles_to_remove = []

            if settings.member_role_id:
                member_role = guild.get_role(settings.member_role_id)
                if member_role and member_role in member.roles:
                    roles_to_remove.append(member_role)

            if settings.commodore_role_id:
                commodore_role = guild.get_role(settings.commodore_role_id)
                if commodore_role and commodore_role in member.roles:
                    roles_to_remove.append(commodore_role)

            if settings.admiral_role_id:
                admiral_role = guild.get_role(settings.admiral_role_id)
                if admiral_role and admiral_role in member.roles:
                    roles_to_remove.append(admiral_role)

            if settings.ops71_plus_role_id:
                ops_role = guild.get_role(settings.ops71_plus_role_id)
                if ops_role and ops_role in member.roles:
                    roles_to_remove.append(ops_role)

            if settings.verified_role_id:
                verify_role = guild.get_role(settings.verified_role_id)
                if verify_role and verify_role in member.roles:
                    roles_to_remove.append(verify_role)

            alliance_role_id = store.get_user_alliance_role_id(user.id)
            if alliance_role_id:
                alliance_role = guild.get_role(alliance_role_id)
                if alliance_role and alliance_role in member.roles:
                    roles_to_remove.append(alliance_role)

            if player_data and len(player_data) >= 3:
                server_role = discord.utils.find(
                    lambda r: r.name == str(player_data[2]),
                    guild.roles,
                )
                if server_role and server_role in member.roles:
                    roles_to_remove.append(server_role)

            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason=f"[RECALL] {reason}")
                log.info(f"[RECALL] Removed {len(roles_to_remove)} roles from {member.id}")
        except Exception as e:
            log.warning(f"[RECALL] Error removing roles from {member.id}: {e}")

        store.delete_verification(user.id)
        store.log_verification_action(user.id, "recalled", interaction.user.id, reason)

        try:
            embed = discord.Embed(
                title=_t.t(locale, "wizard.recalled_title"),
                description=_t.t(locale, "wizard.recalled_desc"),
                colour=discord.Colour.red(),
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(
                name=_t.t(locale, "wizard.recalled_what"),
                value=_t.t(locale, "wizard.recalled_what_value"),
                inline=False,
            )
            embed.set_footer(text=_t.t(locale, "wizard.recalled_footer"))

            msg = await member.send(
                embed=embed,
                view=StartWizardView(store, lambda: _support_ticket_text(settings.support_channel_id), self._t),
            )
            store.save_pending_wizard_view(msg.id, msg.channel.id, member.id, "StartWizardView")
            log.info(f"[RECALL] Sent recall notification to {member.id}")
        except discord.Forbidden:
            log.warning(f"[RECALL] Could not send DM to {member.id} (DMs disabled)")
        except Exception as e:
            log.warning(f"[RECALL] Error sending DM to {member.id}: {e}")

        await interaction.followup.send(
            _t.t(locale, "wizard.recalled_success", member=member.mention),
            ephemeral=True,
        )

        if settings.log_channel_id:
            embed = discord.Embed(
                title=_t.t(locale, "wizard.log_recalled_title"),
                description=f"**{member.mention}** verification recalled by {interaction.user.mention}",
                colour=discord.Colour.red(),
                timestamp=interaction.created_at,
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            if player_data:
                embed.add_field(name="Player", value=f"{player_data[0]}", inline=True)
                rank_field = player_data[4] if len(player_data) > 4 else None
                if rank_field:
                    embed.add_field(name=_t.t(locale, "rank.label"), value=f"{rank_field}", inline=True)

            try:
                await self.bot.post_to_log_channel(embed)
                log.info("[RECALL] Logged recall to log channel")
            except Exception as e:
                log.warning(f"[RECALL] Could not log to channel: {e}")

        log.info(f"[RECALL] user={member.id} admin={interaction.user.id} reason={reason}")


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
