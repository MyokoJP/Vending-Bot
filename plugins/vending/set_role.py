import discord.ui
from discord import Color, Embed

from database import Vending


class SetRoleSelect(discord.ui.RoleSelect):
    def __init__(self, outer, vending: Vending, disabled=False):
        self.outer = outer
        self.vending = vending

        super().__init__(placeholder="ロールを選択してください...", disabled=disabled)

    async def callback(self, ctx: discord.Interaction):
        role = self.values[0]
        self.vending.set_buyer_role_id(role.id)

        view = discord.ui.View()
        self.disabled = True
        view.add_item(self)

        if ctx.guild.self_role.position < role.position:
            embed = Embed(
                title="Success | Vending",
                description="ロールの設定を更新しました。",
                color=Color.yellow(),
            )
            embed.add_field(name="購入者ロール", value=role.mention, inline=False)
            embed.add_field(name=":warning: 注意", value="権限の設定でロールの付与ができないため、\nロールの順序を入れ替えてください", inline=False)
            embed.set_footer(text="By UTA SHOP")

            return await ctx.response.edit_message(
                content="",
                embed=embed,
                view=view,
            )

        embed = Embed(
            title="Success | Vending",
            description="ロールの設定を更新しました。",
            color=Color.green(),
        )
        embed.add_field(name="購入者ロール", value=role.mention)
        embed.set_footer(text="By UTA SHOP")
        await ctx.response.edit_message(content="", embed=embed, view=view)
