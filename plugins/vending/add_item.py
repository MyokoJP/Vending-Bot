import discord
from discord import Embed

from database import Database


class AddProductModal(discord.ui.Modal):
    name = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="商品の名前",
        custom_id="name",
        placeholder="例: 商品1",
    )

    description = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="商品の説明（任意）",
        custom_id="description",
        placeholder="例: すごい商品",
        required=False,
        default=None,
    )

    price_string = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="商品の値段",
        custom_id="price",
        placeholder="例: 50"
    )

    def __init__(self, outer, vending: Database.SemiVending):
        self.outer = outer
        self.vending = vending
        super().__init__(title="商品の追加 | Vending", custom_id="add_product")

    async def on_submit(self, ctx: discord.Interaction):
        try:
            price = int(self.price_string.value)
        except ValueError:
            return await ctx.response.send_message(
                "価格が有効な数字ではありません。数字を入力してください。", ephemeral=True)

        Database.SemiVendingProduct.add(self.vending.id, self.name.value,
                                        self.description.value, price)

        description = f"商品を追加しました。\n\n商品名: `{self.name.value}`\n商品説明:"
        if self.description.value:
            description += f"`{self.description}`"
        else:
            description += "`なし`"
        description += f"\n商品価格: `{price} 円`"

        embed = Embed(
            title="Success | Vending",
            description=description,
        )
        embed.set_footer(text="By UTA SHOP")
        await ctx.response.send_message(embed=embed, ephemeral=True)
