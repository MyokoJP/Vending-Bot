import discord.ui
from discord import ChannelType

from database import Vending


class SetLinkSelect(discord.ui.ChannelSelect):
    def __init__(self, outer, vending: Vending, disabled=False):
        self.outer = outer
        self.vending = vending

        super().__init__(placeholder="チャンネルを選択してください...", channel_types=[ChannelType.text], disabled=disabled)

    async def callback(self, ctx: discord.Interaction):
        channel = self.values[0]
        self.vending.set_link_channel_id(channel.id)

        view = discord.ui.View()
        view.add_item(SetLinkSelect(self.outer, self.vending, True))

        await ctx.response.edit_message(content=f"チャンネルを設定しました。\nリンク送信チャンネル: {channel.mention}", view=view)


class SetPerformanceSelect(discord.ui.ChannelSelect):
    def __init__(self, outer, vending: Vending, disabled=False):
        self.outer = outer
        self.vending = vending

        super().__init__(placeholder="チャンネルを選択してください...", channel_types=[ChannelType.text], disabled=disabled)

    async def callback(self, ctx: discord.Interaction):
        channel = self.values[0]
        self.vending.set_performance_channel_id(channel.id)

        view = discord.ui.View()
        view.add_item(SetLinkSelect(self.outer, self.vending, True))

        await ctx.response.edit_message(content=f"チャンネルを設定しました。\n実績チャンネル: {channel.mention}", view=view)
