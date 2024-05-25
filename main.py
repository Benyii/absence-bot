import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from absence_bot import AbsenceBot
from commands import register_commands
from views.absence_button_view import AbsenceButtonView
from utils.check_absences import check_absences
from utils.database import create_db

# Cargar variables del archivo .env
load_dotenv()

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = AbsenceBot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    await create_db()
    check_absences.start()
    await bot.setup_hook()
    bot.add_view(AbsenceButtonView())
    print('Views added.')

# Registrar comandos
register_commands(bot)

bot.run(TOKEN)
