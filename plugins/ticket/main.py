import asyncio
from typing import Union

import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import config
from database import TicketButton


class TicketCog(Cog):
    def __init__(self, bot: Bot):

        # add_view
        self.bot = bot
        bot.add_view(self.CompleteButton(self))

        ticket_buttons = TicketButton.get_all()
        if ticket_buttons:
            for i in ticket_buttons:
                role = self.bot.get_guild(i.guild_id).get_role(i.role_id) if i.role_id else None
                bot.add_view(self.TicketButtonView(self, self.bot.get_channel(i.category_id), role, i.first_message), message_id=i.message_id)

    # ticketコマンド
    @app_commands.command(name="ticket", description="チケット作成ボタンを送信します")
    @app_commands.describe(title="パネルのタイトル",
                           description="パネルの説明",
                           image="パネルに乗せる画像のURL",
                           category="チケットを作成するカテゴリ",
                           role="チケット作成時にメンションするロール",
                           first_message="チケット作成時に最初に送るメッセージ")
    @app_commands.default_permissions(administrator=True)
    async def ticket(self,
                     ctx: discord.Interaction,
                     title: str,
                     description: str,
                     category: discord.CategoryChannel,
                     role: discord.Role = None,
                     image: str = None,
                     first_message: str = None):

        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("このコマンドを実行する権限がありません", ephemeral=True)
            return

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.random(),
        )

        if image:
            embed.set_image(url=image)

        message = await ctx.channel.send(embed=embed, view=self.TicketButtonView(self, category, role, first_message))

        role_id = None
        if role:
            role_id = role.id
        TicketButton.create(ctx.guild_id, ctx.channel_id, message.id, role_id, category.id, first_message)
        await ctx.response.send_message("チケット作成ボタンを送信しました", ephemeral=True)

    # チケット作成ボタン
    class TicketButtonView(discord.ui.View):
        def __init__(self,
                     outer: 'TicketCog',
                     category: discord.CategoryChannel,
                     role: Union[discord.Role, None] = None,
                     first_message=None,
                     timeout=None
                     ):
            self.outer = outer
            self.bot = outer.bot
            self.category = category
            self.role = role
            self.first_message = first_message
            super().__init__(timeout=timeout)

        @discord.ui.button(label="発行", style=discord.ButtonStyle.primary,
                           custom_id="issue_ticket")
        async def complete(self, ctx: discord.Interaction, button: discord.ui.Button):
            ticket_name = config.TICKET_CHANNEL_NAME.replace("{username}", ctx.user.name)
            ch = await self.category.create_text_channel(name=ticket_name)

            content = ""
            if self.role:
                content = f"{self.role.mention}"
            if self.first_message:
                content += f"\n{self.first_message}"

            await ch.send(content, view=self.outer.CompleteButton(self.outer))
            await ctx.response.send_message(f"チケットを作成しました: {ch.mention}", ephemeral=True)

    # チケット終了確認ぼたん
    class CompleteButton(discord.ui.View):
        def __init__(self, outer: 'TicketCog', timeout=None):
            self.outer = outer
            self.bot = outer.bot
            super().__init__(timeout=timeout)

        @discord.ui.button(label="終了", style=discord.ButtonStyle.red, custom_id="stop_ticket")
        async def complete(self, ctx: discord.Interaction, button: discord.ui.Button):
            embed = discord.Embed(
                title="本当にこのチケットを終了しますか？",
                description="終了する場合は下の終了ボタンを押してください",
            )

            await ctx.response.send_message(embed=embed, view=self.outer.ConfirmButton(self.outer, ctx.message),
                                            ephemeral=True)

    # チケット終了ボタン
    class ConfirmButton(discord.ui.View):
        def __init__(self, outer: 'TicketCog', message: discord.Message):
            self.bot = outer.bot
            self.message = message
            super().__init__()

        @discord.ui.button(label="終了", style=discord.ButtonStyle.red)
        async def complete(self, ctx: discord.Interaction, button: discord.ui.Button):
            embed = discord.Embed(
                title="ご利用ありがとうございました",
                description="このチャンネルは10秒後に削除されます",
            )

            # メッセージ削除
            await self.message.delete()

            button.disabled = True
            await ctx.response.edit_message(view=self)

            # embed送信
            await ctx.channel.send(embed=embed)

            # 10秒後に削除
            await asyncio.sleep(10)
            await ctx.channel.delete()
