import discord
from discord import Color, Embed, Interaction, SelectOption, app_commands
from discord.ext.commands import Bot, Cog

from database import Vending, VendingPanel
from plugins.vending.add_item import AddProductModal
from plugins.vending.add_stock import AddStockSelect
from plugins.vending.buy import BuyButton
from plugins.vending.delete_item import DeleteProductSelect
from plugins.vending.delete_vending import DeleteVendingButton
from plugins.vending.edit_item import EditProductSelect
from plugins.vending.edit_vending import EditVendingModal
from plugins.vending.return_stock import ReturnStockSelect
from plugins.vending.set_links import SetLinkSelect, SetPerformanceSelect
from plugins.vending.set_role import SetRoleSelect


class VendingCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        panels = VendingPanel.get_all()
        if panels:
            for i in panels:
                vending = i.vending
                bot.add_view(BuyButton(self, vending), message_id=i.message_id)

    # 自販機作成コマンド
    @app_commands.command(name="vending_create", description="半自動販売機を作成します")
    @app_commands.describe(name="半自動販売機の名前")
    @app_commands.choices(
        type=[
            app_commands.Choice(name="全自動", value="Auto"),
            app_commands.Choice(name="半自動", value="SemiAuto")
        ]
    )
    @app_commands.default_permissions(administrator=True)
    async def create(self, ctx: Interaction, name: str, type: str):
        Vending.create(ctx.guild_id, name)

        embed = Embed(
            title="作成完了",
            description="半自動販売機の作成が完了しました。",
            color=Color.green(),
        )
        embed.add_field(name="名前", value=name)
        embed.add_field(name="作成したサーバー", value=ctx.guild.name)
        embed.set_footer(text="By UTA SHOP")

        await ctx.response.send_message(embed=embed, ephemeral=True)

    # 自販機パネル送信コマンド
    @app_commands.command(name="vending_panel", description="半自動販売機のパネルを設置します")
    @app_commands.describe()
    async def panel(self, ctx: Interaction):
        vending = Vending.get_by_guild(ctx.guild_id)

        if not vending:
            embed = Embed(
                title="エラー",
                description="半自動販売機が作成されていません。`/vending create`で半自動販売機を作成してください。",
                color=Color.red(),
            )
            embed.set_footer(text="By UTA SHOP")
            await ctx.response.send_message(embed=embed, ephemeral=True)

        elif len(vending) == 1:

            if not vending[0].link_channel_id:
                return await ctx.response.send_message("リンク送信チャンネルが設定されていません。")

            msg = await ctx.channel.send(embed=create_panel(vending[0]), view=BuyButton(self, vending[0]))
            await ctx.response.send_message("パネルを送信しました。", ephemeral=True)

            VendingPanel.add(ctx.guild_id, ctx.channel_id, msg.id, vending[0].id)

        else:
            view = discord.ui.View(timeout=None)
            view.add_item(self.VendingPanelSelect(self, vending))
            return await ctx.response.send_message("設置する半自販機を選択してください。", view=view, ephemeral=True)

    # 自販機選択
    class VendingPanelSelect(discord.ui.Select):
        def __init__(self,
                     outer: 'VendingCog',
                     vending: list[Vending],
                     ):
            self.outer = outer
            self.vending = vending

            options = [
                SelectOption(label=vending[i].name, description=str(vending[i].id),
                             value=str(i))
                for i in range(len(vending))]
            super().__init__(options=options, placeholder="選択してください...")

        async def callback(self, ctx: discord.Interaction):
            vending = self.vending[int(self.values[0])]

            if not vending.link_channel_id:
                return await ctx.response.send_message("リンク送信チャンネルが設定されていません。")

            msg = await ctx.channel.send(embed=create_panel(vending), view=BuyButton(self, vending))
            await ctx.response.send_message("パネルを送信しました。", ephemeral=True)

            VendingPanel.add(ctx.guild_id, ctx.channel_id, msg.id, vending.id)

    # 自販機設定コマンド
    @app_commands.command(name="vending_setting",
                          description="半自動販売機の設定パネルを表示します")
    @app_commands.describe()
    async def setting(self, ctx: Interaction):
        vending = Vending.get_by_guild(ctx.guild_id)
        if not vending:
            embed = Embed(
                title="エラー",
                description="半自動販売機が作成されていません。`/vending create`で半自動販売機を作成してください。",
                color=Color.red(),
            )
            embed.set_footer(text="By UTA SHOP")
            return await ctx.response.send_message(embed=embed, ephemeral=True)

        elif len(vending) == 1:
            embeds = create_setting(self.bot, vending[0])
            return await ctx.response.send_message(embeds=embeds,
                                                   view=self.AddProductButton(self, vending[0]),
                                                   ephemeral=True)

        else:
            view = discord.ui.View()
            view.add_item(self.VendingSettingSelect(self, vending))
            return await ctx.response.send_message("設定を行う半自販機を選択してください。",
                                                   view=view, ephemeral=True)

    # 自販機選択
    class VendingSettingSelect(discord.ui.Select):
        def __init__(self,
                     outer: 'VendingCog',
                     vending: list[Vending],
                     ):
            self.outer = outer
            self.vending = vending

            options = [
                SelectOption(label=vending[i].name, description=str(vending[i].id), value=str(i))
                for i in range(len(vending))]
            super().__init__(options=options, placeholder="選択してください...")

        async def callback(self, ctx: discord.Interaction):
            vending = self.vending[int(self.values[0])]

            embeds = create_setting(self.outer.bot, vending)
            return await ctx.response.edit_message(embeds=embeds,
                                                   view=self.outer.AddProductButton(self.outer,
                                                                                    vending),
                                                   ephemeral=True)

    # 設定ボタン
    class AddProductButton(discord.ui.View):
        def __init__(self, outer: 'VendingCog', vending: Vending, timeout=None):
            self.outer = outer
            self.vending = vending
            super().__init__(timeout=timeout)

        @discord.ui.button(label="商品追加", style=discord.ButtonStyle.success)
        async def add_product(self, ctx: discord.Interaction, button: discord.ui.Button):
            await ctx.response.send_modal(AddProductModal(self.outer, self.vending))

        @discord.ui.button(label="商品編集", style=discord.ButtonStyle.primary)
        async def edit_product(self, ctx: discord.Interaction, button: discord.ui.Button):
            products = self.vending.products
            if not products:
                return await ctx.response.send_message(
                    "編集できる商品がありません。商品を追加してください。", ephemeral=True)

            view = discord.ui.View(timeout=None)
            view.add_item(EditProductSelect(self.outer, products))
            await ctx.response.send_message("編集する商品を選択してください。", view=view,
                                            ephemeral=True)

        @discord.ui.button(label="商品削除", style=discord.ButtonStyle.danger)
        async def delete_product(self, ctx: discord.Interaction, button: discord.ui.Button):
            products = self.vending.products
            if not products:
                return await ctx.response.send_message(
                    "削除できる商品がありません。商品を追加してください。", ephemeral=True)

            view = discord.ui.View(timeout=None)
            view.add_item(DeleteProductSelect(self.outer, products))
            await ctx.response.send_message("削除する商品を選択してください。", view=view,
                                            ephemeral=True)

        @discord.ui.button(label="商品補充", style=discord.ButtonStyle.primary)
        async def add_stock(self, ctx: discord.Interaction, button: discord.ui.Button):
            products = self.vending.products
            if not products:
                return await ctx.response.send_message(
                    "補充できる商品がありません。商品を追加してください。", ephemeral=True)

            view = discord.ui.View(timeout=None)
            view.add_item(AddStockSelect(self.outer, products))
            await ctx.response.send_message("補充する商品を選択してください。", view=view,
                                            ephemeral=True)

        @discord.ui.button(label="商品取り出し", style=discord.ButtonStyle.gray)
        async def return_stock(self, ctx: discord.Interaction, button: discord.ui.Button):
            products = self.vending.products
            if not products:
                return await ctx.response.send_message("取り出しできる商品がありません。",
                                                       ephemeral=True)

            view = discord.ui.View(timeout=None)
            view.add_item(ReturnStockSelect(self.outer, products))
            await ctx.response.send_message("取り出しする商品を選択してください。", view=view,
                                            ephemeral=True)

        @discord.ui.button(label="リンク送信チャンネルの設定", style=discord.ButtonStyle.success)
        async def set_link_channel(self, ctx: discord.Interaction, button: discord.ui.Button):
            view = discord.ui.View(timeout=None)
            view.add_item(SetLinkSelect(self.outer, self.vending))
            await ctx.response.send_message(
                "購入された際のPayPayリンクを送信するチャンネルを設定してください。", view=view,
                ephemeral=True)

        @discord.ui.button(label="実績チャンネルの設定", style=discord.ButtonStyle.success)
        async def set_performance_channel(self, ctx: discord.Interaction,
                                          button: discord.ui.Button):
            view = discord.ui.View(timeout=None)
            view.add_item(SetPerformanceSelect(self.outer, self.vending))
            await ctx.response.send_message(
                "購入が完了した際の実績メッセージを送信するチャンネルを設定してください。",
                view=view, ephemeral=True)

        @discord.ui.button(label="購入者ロールの設定", style=discord.ButtonStyle.success)
        async def set_buyer_role(self, ctx: discord.Interaction, button: discord.ui.Button):
            view = discord.ui.View(timeout=None)
            view.add_item(SetRoleSelect(self.outer, self.vending))
            await ctx.response.send_message(
                "購入が完了した際に設定する購入者ロールを設定してください。", view=view,
                ephemeral=True)

        @discord.ui.button(label="半自販機編集", style=discord.ButtonStyle.primary)
        async def edit_vending(self, ctx: discord.Interaction, button: discord.ui.Button):
            await ctx.response.send_modal(EditVendingModal(self.outer, self.vending))

        @discord.ui.button(label="半自販機削除", style=discord.ButtonStyle.danger)
        async def delete_vending(self, ctx: discord.Interaction, button: discord.ui.Button):
            embed = Embed(
                title="Confirm | Vending",
                description="本当にこの半自販機を削除しますか?",
                color=Color.red(),
            )
            embed.set_footer(text="By UTA SHOP")
            await ctx.response.send_message(embed=embed,
                                            view=DeleteVendingButton(self.outer, self.vending),
                                            ephemeral=True)


def create_setting(bot, vending: Vending):
    embed = Embed(
        title=vending.name + "の設定",
        description="設定を行うには下の各種ボタンを押して設定を行ってください。",
        color=Color.green(),
    )
    embed.set_footer(text="By UTA SHOP")

    guild = bot.get_guild(vending.guild_id)
    embed.add_field(name="Shopの作成されたサーバー", value=guild.name, inline=False)

    link_channel_name = "なし"
    if vending.link_channel_id:
        link_channel = guild.get_channel(vending.link_channel_id)
        if link_channel:
            link_channel_name = link_channel.mention
    embed.add_field(name="ShopのPayPay送信チャンネル", value=link_channel_name, inline=False)

    performance_channel_name = "なし"
    if vending.performance_channel_id:
        performance_channel = guild.get_channel(vending.performance_channel_id)
        if performance_channel:
            performance_channel_name = performance_channel.mention
    embed.add_field(name="Shopの実績送信チャンネル", value=performance_channel_name, inline=False)

    buyer_role_name = "なし"
    if vending.buyer_role:
        buyer_role = guild.get_channel(vending.buyer_role)
        if buyer_role:
            buyer_role_name = buyer_role.mention
    embed.add_field(name="Shopの購入者ロール", value=buyer_role_name, inline=False)

    products = vending.products

    embed.add_field(name="商品数", value=str(len(products)), inline=False)

    if products:
        products_description = []
        for i in products:
            products_description.append(
                f"商品: `{i.name}`\n価格: `{i.price}円` 在庫: `{len(i.stocks)}`")

        products_embed = Embed(
            title="商品一覧",
            description="\n\n".join(products_description)
        )

        return [embed, products_embed]

    return [embed]


def create_panel(vending: Vending):
    products = vending.products

    values = []
    for i in products:
        if i.description:
            description = i.description
        else:
            description = "説明無し"
        values.append(f"{i.name} - {i.price}円\n`{description}`")

    embed = Embed(
        title=f"{vending.name} - 半自販機",
        description="購入するには下のボタンを押してください\n\n\n" + "\n".join(values),
    )
    embed.set_footer(text="By UTA SHOP")

    return embed
