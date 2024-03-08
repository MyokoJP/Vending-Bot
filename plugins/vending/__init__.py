from discord.ext.commands import Bot

from plugins.vending.main import Vending


def setup(bot: Bot):
    return bot.add_cog(Vending(bot))
