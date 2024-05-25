import discord
from absence_bot import AbsenceBot
import aiosqlite

@bot.tree.command(name='clear_ausencias', description="Borra todas las ausencias registradas en la base de datos")
async def clear_ausencias(interaction: discord.Interaction):
    try:
        if not any(role.id == int(os.getenv('APPROVER_ROLE_ID')) for role in interaction.user.roles):
            await interaction.response.send_message('No tienes permiso para realizar esta acción.', ephemeral=True)
            return

        async with aiosqlite.connect('absences.db') as db:
            await db.execute('DELETE FROM absences')
            await db.commit()

        await interaction.response.send_message('Todas las ausencias han sido borradas.', ephemeral=True)
    except Exception as e:
        print(f'Error in /clear_ausencias command: {e}')
