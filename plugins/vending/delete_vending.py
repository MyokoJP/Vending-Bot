import discord
from discord import Color, Embed

from database import Database


class DeleteVendingButton(discord.ui.View):
    def __init__(self, outer, vending: Database.SemiVending, timeout=None):
        self.outer = outer
        self.vending = vending
        super().__init__(timeout=timeout)

    @discord.ui.button(label="確定", style=discord.ButtonStyle.red)
    async def delete(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.vending.delete()
        button.disabled = True

        embed = Embed(
            title="Success | Vending",
            description="削除しました。",
            color=Color.green(),
        )
        embed.set_footer(text="By UTA SHOP")
        await ctx.response.edit_message(embed=embed, view=self)
