import asyncio

import discord
from discord import Color, Embed, Interaction, app_commands
from discord.ext.commands import Bot, Cog


class NukeCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="nuke", description="チャンネルログを全消去します")
    @app_commands.default_permissions(administrator=True)
    async def nuke(self, interaction: Interaction):
        if interaction.user.guild_permissions.administrator:
            embed = Embed(title="確認 | Confirm",
                          description="本当にチャンネルログを消去しますか？\n**消去を押した後操作は取り消せません**",
                          color=Color.yellow(),
                          )
            embed.set_footer(text="By UTA SHOP")
            await interaction.response.send_message(embed=embed,
                                                    view=NukeConfirmButtonView(bot=self.bot))


class NukeConfirmButtonView(discord.ui.View):
    def __init__(self, bot: Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="💥消去 | NUKE", style=discord.ButtonStyle.danger)
    async def allow(self, ctx: Interaction, button: discord.ui.Button):
        if ctx.user.guild_permissions.manage_messages:
            if ctx.channel.topic is None:
                topic = None
            else:
                topic = ctx.channel.topic
            new_channel = await ctx.channel.category.create_text_channel(name=ctx.channel.name,
                                                                         position=ctx.channel.position,
                                                                         overwrites=ctx.channel.overwrites,
                                                                         topic=topic)

            await ctx.channel.delete()

            embed_cleaned = discord.Embed(
                title="Success | Nuke",
                description="正常にチャンネルログを消去しました。\nこのメッセージは10秒後に消去されます",
                color=Color.green()
            )

            embed_cleaned.set_footer(text="By UTA SHOP")

            i = await new_channel.send(embed=embed_cleaned)
            await asyncio.sleep(10)
            await i.delete()

    @discord.ui.button(label="❌キャンセル | CANCEL", style=discord.ButtonStyle.gray)
    async def cancel(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.message.delete()


async def setup(bot: Bot):
    await bot.add_cog(NukeCog(bot))
