import discord
from discord import Color, Embed, Interaction, Member, app_commands
from discord.ext.commands import Bot, Cog


class BanCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="ban", description="ユーザーをBanします")
    @app_commands.describe(member="Banするメンバー", reason="理由(任意)")
    @app_commands.default_permissions(administrator=True)
    async def nuke(self, interaction: Interaction, member: Member, reason: str = None):
        if interaction.user.guild_permissions.administrator:
            embed = Embed(
                title="確認 | Confirm",
                description=f"本当に{member.mention}をKickしますか?",
                color=Color.yellow(),
                )
            embed.set_footer(text="By UTA SHOP")
            await interaction.response.send_message(embed=embed,
                                                    view=BanConfirmButtonView(self.bot, member, reason))


class BanConfirmButtonView(discord.ui.View):
    def __init__(self, bot: Bot, member: Member, reason: str):
        super().__init__(timeout=None)
        self.member = member
        self.reason = reason
        self.bot = bot

    @discord.ui.button(label="KICK", style=discord.ButtonStyle.danger)
    async def ban(self, ctx: discord.Interaction, button: discord.ui.Button):
        await self.member.kick(reason=self.reason)

        embed = discord.Embed(
            title="Success | Kick",
            description="正常にKickしました",
            color=Color.green()
        )
        embed.set_footer(text="By UTA SHOP")
        button.disabled = True
        self.cancel.disabled = True

        await ctx.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌キャンセル | CANCEL", style=discord.ButtonStyle.gray)
    async def cancel(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.message.delete()


async def setup(bot: Bot):
    await bot.add_cog(BanCog(bot))
