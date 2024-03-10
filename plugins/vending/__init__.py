from discord.ext.commands import Bot

from plugins.vending.main import VendingCog


def setup(bot: Bot):
    return bot.add_cog(VendingCog(bot))
