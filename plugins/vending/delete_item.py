import discord
from discord import Color, Embed, SelectOption

from database import Database


class DeleteProductSelect(discord.ui.Select):
    def __init__(self,
                 outer,
                 products: list[Database.SemiVendingProduct],
                 ):
        self.outer = outer
        self.products = products

        options = [
            SelectOption(label=products[i].name, description=str(products[i].price) + " 円",
                         value=str(i)) for i in range(len(products))]
        super().__init__(options=options, placeholder="選択してください...")

    async def callback(self, ctx: discord.Interaction):
        product = self.products[int(self.values[0])]
        embed = Embed(
            title="Confirm | Vending",
            description="本当にこの商品を削除しますか?",
            color=Color.yellow(),
        )
        embed.set_footer(text="By UTA SHOP")
        await ctx.response.send_message(embed=embed,
                                        view=DeleteProductButton(self.outer, product,
                                                                 ctx), ephemeral=True)


class DeleteProductButton(discord.ui.View):
    def __init__(self, outer, product: Database.SemiVendingProduct, interaction,
                 timeout=None):
        self.outer = outer
        self.product = product
        self.interaction = interaction
        super().__init__(timeout=timeout)

    @discord.ui.button(label="確定", style=discord.ButtonStyle.red)
    async def delete(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.product.delete()
        button.disabled = True

        embed = Embed(
            title="Success | Vending",
            description="削除しました。",
            color=Color.green(),
        )
        embed.set_footer(text="By UTA SHOP")
        await ctx.response.edit_message(embed=embed, view=self)
