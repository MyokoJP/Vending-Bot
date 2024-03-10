import discord.ui

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
        view.add_item(SetRoleSelect(self.outer, self.vending, True))

        await ctx.response.edit_message(content=f"ロールを設定しました。\n購入者ロール: {role.mention}", view=view)
