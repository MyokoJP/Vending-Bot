import discord
from discord import Color, Embed

from database import Database


class EditVendingModal(discord.ui.Modal):
    name = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="新しい名前",
        placeholder="例: shop",
    )

    def __init__(self, outer, vending: Database.SemiVending):
        self.outer = outer
        self.vending = vending
        super().__init__(title="半自販機の編集 | Vending", custom_id="add_product")

    async def on_submit(self, ctx: discord.Interaction):
        self.vending.rename(self.name.value)

        embed = Embed(
            title="Success | Vending",
            description="変更が完了しました。",
            color=Color.green(),
        )
        embed.set_footer(text="By UTA SHOP")
        await ctx.response.send_message(embed=embed, ephemeral=True)
