import discord
from discord.ext import commands

class AbsenceBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.synced = False

    async def setup_hook(self):
        await self.tree.sync()
        print(f'Synced slash commands.')
