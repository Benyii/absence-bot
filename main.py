import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiosqlite
import time
from absence_bot import AbsenceBot
from commands import register_commands
from views.absence_button_view import AbsenceButtonView
from utils.check_absences import check_absences
from utils.database import create_db

# Cargar variables del archivo .env
load_dotenv()
print("Loaded .env file.")

TOKEN = os.getenv('TOKEN')
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID'))
GUILD_ID = int(os.getenv('GUILD_ID'))
print(f"TOKEN: {TOKEN}")
print(f"LOG_CHANNEL_ID: {LOG_CHANNEL_ID}")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = AbsenceBot(command_prefix='!', intents=intents)

async def send_startup_message():
    print("send_startup_message called.")
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel is None:
        print("Log channel not found.")
        return

    start_time = time.time()

    # Contar el número de comandos
    num_commands = len(bot.tree.get_commands())
    print(f"Number of commands loaded: {num_commands}")

    # Contar el número de ausencias
    async with aiosqlite.connect('absences.db') as db:
        async with db.execute('SELECT COUNT(*) FROM absences') as cursor:
            num_absences = (await cursor.fetchone())[0]
    print(f"Number of absences found: {num_absences}")

    end_time = time.time()
    startup_time = end_time - start_time

    embed = discord.Embed(
        title="Bot Iniciado",
        description=f"El bot ha sido iniciado correctamente.",
        color=discord.Color.green()
    )
    embed.add_field(name="Comandos Cargados", value=num_commands)
    embed.add_field(name="Ausencias Registradas", value=num_absences)
    embed.add_field(name="Tiempo de Inicio", value=f"{startup_time:.2f} segundos")
    embed.set_footer(text=f"Iniciado a las {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC")

    print("Sending startup message to log channel.")
    await log_channel.send(embed=embed)
    print("Startup message sent.")

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    await create_db()
    print("Database checked.")
    check_absences.start()
    print("Started check_absences task.")
    await bot.setup_hook()
    print("Bot setup_hook completed.")
    bot.add_view(AbsenceButtonView())
    print('Views added.')
    await send_startup_message()
    print("Sent startup message.")

# Registrar comandos
register_commands(bot)
print("Commands registered.")

# Comando para sincronizar los comandos slash
@bot.tree.command(name='sync', description="Sincroniza los comandos slash del bot")
async def sync(interaction: discord.Interaction):
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    await interaction.response.send_message('Comandos slash sincronizados.', ephemeral=True)
    print("Slash commands synced.")

print("Running bot.")
bot.run(TOKEN)
print("Bot run called.")
