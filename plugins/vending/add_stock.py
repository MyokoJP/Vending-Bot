import discord
from discord import Embed, Interaction, SelectOption

from database import VendingProduct, VendingStock


class AddStockSelect(discord.ui.Select):
    def __init__(self, outer, products: list[VendingProduct]):
        self.outer = outer
        self.products = products

        options = [SelectOption(label=products[i].name, description=str(products[i].price) + " 円",
                                value=str(i)) for i in range(len(products))]
        super().__init__(options=options, placeholder="選択してください...")

    async def callback(self, ctx: discord.Interaction):
        product = self.products[int(self.values[0])]
        return await ctx.response.send_modal(AddStockModal(self.outer, product))


class AddStockModal(discord.ui.Modal):
    stock = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="補充する商品を１行ずつ改行して入力してください",
        placeholder="example1@example.com:password1234\nexample2@example.com:password5678",

    )
    def __init__(self, outer, product: VendingProduct):

        self.outer = outer
        self.product = product

        stocks = product.stocks
        print(stocks)
        self.stock.label += f"（現在の在庫数: {len(stocks)}個）"

        super().__init__(title="商品の補充 | Vending")

    async def on_submit(self, ctx: Interaction):
        for i in self.stock.value.split("\n"):
            if i:
                VendingStock.add(self.product.product_id, i)

        embed = Embed(
            title="Success | Vending",
            description=f"商品が追加されました。現在の在庫数: `{len(self.product.stocks)}個`"
        )
        embed.set_footer(text="By UTA SHOP")

        await ctx.response.send_message(embed=embed, ephemeral=True)
