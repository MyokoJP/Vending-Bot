import discord
from discord import Embed, SelectOption

from database import Database


class EditProductSelect(discord.ui.Select):
    def __init__(self,
                 outer,
                 products: list[Database.SemiVendingProduct],
                 ):
        self.outer = outer
        self.products = products

        options = [SelectOption(label=products[i].name, description=str(products[i].price) + " 円",
                                value=str(i)) for i in range(len(products))]
        super().__init__(options=options, placeholder="選択してください...")

    async def callback(self, ctx: discord.Interaction):
        product = self.products[int(self.values[0])]
        return await ctx.response.send_modal(EditProductModal(self.outer, product))


# 商品追加モーダル
class EditProductModal(discord.ui.Modal):
    name = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="商品の名前",
        placeholder="例: 商品1",
        required=False,
        default=None,
    )

    description = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="商品の説明（任意）",
        placeholder="例: すごい商品",
        required=False,
        default=None,
    )

    price_string = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="商品の値段",
        placeholder="例: 50",
        required=False,
        default=None,
    )

    def __init__(self, outer, product: Database.SemiVendingProduct):
        self.outer = outer
        self.product = product
        super().__init__(title="商品の編集 | Vending", timeout=None)

    async def on_submit(self, ctx: discord.Interaction):
        msg = ""
        if self.name.value:
            self.product.edit_name(self.name.value)
            msg += f"\n商品名: `{self.name.value}`"

        if self.description.value:
            self.product.edit_description(self.description.value)
            msg += f"\n商品説明: `{self.description.value}`"

        if self.price_string.value:
            try:
                price = int(self.price_string.value)
                self.product.edit_price(price)

                msg += f"\n商品価格: `{price} 円`"
            except ValueError:
                return await ctx.response.send_message(
                    "価格が有効な数字ではありません。数字を入力してください。", ephemeral=True)

        embed = Embed(
            title="Success | Vending",
            description="更新が完了しました。\n" + msg,
        )
        embed.set_footer(text="By UTA SHOP")
        await ctx.response.send_message(embed=embed, ephemeral=True)
