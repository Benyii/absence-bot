import discord
from discord import app_commands
import aiosqlite
import os

async def terminarausencia(interaction: discord.Interaction):
    try:
        user = interaction.user
        async with aiosqlite.connect('absences.db') as db:
            async with db.execute('SELECT id, user_id, start_date, end_date, status, reason, message_id FROM absences WHERE user_id = ? AND status = ?', (user.id, 'approved')) as cursor:
                row = await cursor.fetchone()

            if not row:
                await interaction.response.send_message('No tienes ausencias aprobadas actualmente.', ephemeral=True)
                return

            absence_id, user_id, start_date, end_date, status, reason, message_id = row
            await db.execute('UPDATE absences SET status = ? WHERE id = ?', ('finished', absence_id))
            await db.commit()

            public_channel = interaction.client.get_channel(int(os.getenv('PUBLIC_CHANNEL_ID')))
            try:
                public_message = await public_channel.fetch_message(message_id)
                await public_message.clear_reactions()
                await public_message.add_reaction('✅')
                await public_message.edit(content=public_message.content.replace(":green_circle:", ":red_circle:"))
            except discord.NotFound:
                print(f"Public message with ID {message_id} not found.")

        await interaction.response.send_message('Tu ausencia ha sido marcada como terminada.', ephemeral=True)
    except Exception as e:
        print(f'Error in /terminarausencia command: {e}')

def setup(bot):
    bot.tree.add_command(app_commands.Command(name='terminarausencia', description="Termina manualmente tu última ausencia", callback=terminarausencia))
