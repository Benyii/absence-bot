from .ausencia import *
from .list_ausencias import *
from .clear_ausencias import *
from .terminarausencia import *
from .terminarausenciaid import *

def register_commands(bot):
    bot.add_application_command(ausencia)
    bot.add_application_command(list_ausencias)
    bot.add_application_command(clear_ausencias)
    bot.add_application_command(terminarausencia)
    bot.add_application_command(terminarausenciaid)
