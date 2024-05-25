from .ausencia import setup as setup_ausencia
from .list_ausencias import setup as setup_list_ausencias
from .clear_ausencias import setup as setup_clear_ausencias
from .terminarausencia import setup as setup_terminarausencia
from .terminarausenciaid import setup as setup_terminarausenciaid
from .remindertest import setup as setup_remindertest

def register_commands(bot):
    setup_ausencia(bot)
    setup_list_ausencias(bot)
    setup_clear_ausencias(bot)
    setup_terminarausencia(bot)
    setup_terminarausenciaid(bot)
    setup_remindertest(bot)
