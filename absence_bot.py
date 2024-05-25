import discord
from discord.ext import commands
from utils.database import create_db
from utils.check_absences import check_absences

class AbsenceBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.synced = False

    async def setup_hook(self):
        await self.tree.sync()
        await create_db()
        check_absences.start()
        print(f'Synced slash commands.')
