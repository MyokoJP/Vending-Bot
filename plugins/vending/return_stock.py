import discord
from discord import Embed, Interaction, SelectOption

from database import Database


class ReturnStockSelect(discord.ui.Select):
    def __init__(self, outer, products: list[Database.SemiVendingProduct]):
        self.outer = outer
        self.products = products

        options = [SelectOption(label=products[i].name, description=str(products[i].price) + " 円",
                                value=str(i)) for i in range(len(products))]
        super().__init__(options=options, placeholder="選択してください...")

    async def callback(self, ctx: discord.Interaction):
        product = self.products[int(self.values[0])]

        view = discord.ui.View(timeout=None)
        view.add_item(OrderSelect(self.outer, product))

        await ctx.response.edit_message(content="取り出し方法を選択してください。", view=view)


class OrderSelect(discord.ui.Select):
    def __init__(self, outer, product: Database.SemiVendingProduct):
        self.outer = outer
        self.product = product

        options = [SelectOption(label="古い順", description="古いほうから取り出し"),
                   SelectOption(label="新しい順", description="新しいほうから取り出し"),
                   SelectOption(label="全て", description="全ての在庫を取り出し"),]
        super().__init__(options=options, placeholder="選択してください...")

    async def callback(self, ctx: discord.Interaction):
        selected = self.values[0]

        if selected == "古い順":
            return await ctx.response.send_modal(ReturnStockModal(self.outer, self.product, False))

        elif selected == "新しい順":
            return await ctx.response.send_modal(ReturnStockModal(self.outer, self.product, True))

        else:
            return_stocks = self.product.return_all()

            content = "```" + "\n".join([i.value for i in return_stocks]) + "```"
            embed = Embed(
                title="Success | Vending",
                description=f"商品が取り出されました現在の在庫数: `{len(self.product.stocks)}個`"
            )
            embed.set_footer(text="By UTA SHOP")
            await ctx.response.send_message(content, embed=embed, ephemeral=True)


class ReturnStockModal(discord.ui.Modal):
    number_stocks = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="取り出しを行う個数を入力してください",
        placeholder="例: 2",
    )

    def __init__(self, outer, product: Database.SemiVendingProduct, order_by_latest: bool):
        self.outer = outer
        self.product = product
        self.order_by_latest = order_by_latest

        self.number_stocks.label += f"（現在の在庫数: {len(product.stocks)}個）"
        super().__init__(title="商品の取り出し | Vending")

    async def on_submit(self, ctx: Interaction):
        try:
            number_stocks = int(self.number_stocks.value)
        except ValueError:
            return await ctx.response.send_message("有効な数字ではありません。数字を入力してください。")

        if self.order_by_latest:
            return_stocks = self.product.return_order_by_latest(number_stocks)
        else:
            return_stocks = self.product.return_order_by_oldest(number_stocks)

        content = "```" + "\n".join([i.value for i in return_stocks]) + "```"
        embed = Embed(
            title="Success | Vending",
            description=f"商品が取り出されました現在の在庫数: `{len(self.product.stocks)}個`"
        )
        embed.set_footer(text="By UTA SHOP")
        await ctx.response.send_message(content, embed=embed, ephemeral=True)
