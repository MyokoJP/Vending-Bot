import re

import discord
from discord import Color, Embed, Interaction, SelectOption

from database import Database


class BuyButton(discord.ui.View):
    def __init__(self,
                 outer,
                 vending: Database.SemiVending,
                 products: list[Database.SemiVendingProduct],
                 timeout=None):
        self.outer = outer
        self.vending = vending
        self.products = products
        super().__init__(timeout=timeout)

    @discord.ui.button(label="購入", style=discord.ButtonStyle.success)
    async def add_product(self, ctx: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View(timeout=None)
        view.add_item(BuyProductSelect(self.outer, self.vending, self.products))
        await ctx.response.send_message("購入する商品を選択してください。", view=view, ephemeral=True)


class BuyProductSelect(discord.ui.Select):
    def __init__(self,
                 outer,
                 vending: Database.SemiVending,
                 products: list[Database.SemiVendingProduct],
                 ):
        self.outer = outer
        self.vending = vending
        self.products = products

        options = [SelectOption(label=products[i].name,
                                description=f"価格: {products[i].price}円 - 在庫数{len(products[i].stocks)}個",
                                value=str(i)) for i in range(len(products))]
        super().__init__(options=options, placeholder="商品を一つ選択してください")

    async def callback(self, ctx: discord.Interaction):
        product = self.products[int(self.values[0])]
        return await ctx.response.send_modal(BuyProductModal(self.outer, self.vending, product))


class BuyProductModal(discord.ui.Modal):
    quantity = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="数量",
        placeholder="例: 1",
    )

    def __init__(self, outer, vending: Database.SemiVending, product: Database.SemiVendingProduct):
        self.outer = outer
        self.vending = vending
        self.product = product

        self.quantity.label += f"（現在の在庫数: {len(product.stocks)}個）"
        super().__init__(title="購入 | Vending")

    async def on_submit(self, ctx: Interaction):
        try:
            quantity = int(self.quantity.value)
        except ValueError:
            return await ctx.response.send_message(
                "有効な数字ではありません。数字を入力してください。")

        total = self.product.price * quantity

        embed = Embed(
            title=f"支払額 {total}円",
            description=f"下のボタンを押して支払いを行ってください。",
            color=Color.blurple(),
        )
        embed.set_footer(text="By UTA SHOP")
        await ctx.response.send_message(embed=embed, view=PayButton(self.outer, self.vending, self.product, quantity, total), ephemeral=True)


class PayButton(discord.ui.View):
    def __init__(self,
                 outer: 'Vending',
                 vending: Database.SemiVending,
                 product: Database.SemiVendingProduct,
                 quantity: int,
                 total: int,
                 timeout=None):
        self.outer = outer
        self.vending = vending
        self.product = product
        self.quantity = quantity
        self.total = total
        super().__init__(timeout=timeout)

    @discord.ui.button(label="支払い", style=discord.ButtonStyle.success)
    async def add_product(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(PayPayLinkModal(self.outer, self.vending, self.product, self.quantity, self.total))


class PayPayLinkModal(discord.ui.Modal):
    link = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="PayPayリンク",
        placeholder="例: https://pay.paypay.ne.jp/xxxxxxxxxxxxxxxx",
        min_length=41,
        max_length=41,
    )
    password = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="受け取りパスコード（ある場合）",
        placeholder="例: 1234",
        required=False,
        default=None,
    )
    note = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="備考（任意）",
        required=False,
        default=None,
    )

    def __init__(self,
                 outer: 'Vending',
                 vending: Database.SemiVending,
                 product: Database.SemiVendingProduct,
                 quantity: int,
                 total: int,
                 timeout=None):
        self.outer = outer
        self.vending = vending
        self.product = product
        self.quantity = quantity
        self.total = total

        super().__init__(title="購入 | Vending", timeout=timeout)

    async def on_submit(self, ctx: Interaction):
        match = re.match(r"https://pay.paypay.ne.jp/[a-zA-Z]{16}", self.link.value)
        if not match:
            return await ctx.response.send_message("有効なPayPayリンクの形式ではありません。以下のような形で入力してください。\nhttps://pay.paypay.ne.jp/xxxxxxxxxxxxxxxx")

        ### paypayリンクチェックの処理 ###

        embed = Embed(
            title="半自販機 - 購入リクエスト",
            description="以下のユーザーが半自販機を使用しました。PayPayリンクを受け取った後、ボタンを押してください。",
            color=Color.green(),
        )
        embed.add_field(name="購入ユーザー", value=f"{ctx.user.mention}(ID: {ctx.user.id})", inline=False)
        embed.add_field(name="購入品目", value=self.product.name, inline=False)
        embed.add_field(name="支払金額", value=f"{self.total} 円", inline=False)
        embed.add_field(name="PayPayリンク", value=self.link, inline=False)

        if self.password.value:
            password = self.password.value
        else:
            password = "パスコードなし"
        embed.add_field(name="パスコード", value=password, inline=False)

        if self.note.value:
            note = self.note.value
        else:
            note = "なし"
        embed.add_field(name="備考", value=note)

        link_channel = self.outer.bot.get_channel(self.vending.link_channel_id)
        await link_channel.send(embed=embed)

        await ctx.response.send_message("購入リクエストを送信しました。管理者がPayPayリンクを受け取り後、DMに商品が送信されますのでBotからのDMが届く状態にしておいてください。")
