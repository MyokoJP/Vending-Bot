from discord.ext.commands import Bot

from plugins.ticket.main import TicketCog


def setup(bot: Bot):
    return bot.add_cog(TicketCog(bot))
