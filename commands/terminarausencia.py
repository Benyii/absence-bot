import discord
from discord import app_commands
import aiosqlite
import os

async def terminarausencia(interaction: discord.Interaction):
    try:
        user = interaction.user
        async with aiosqlite.connect('absences.db') as db:
            async with db.execute('SELECT id, user_id, start_date, end_date, status, reason, public_message_id, approved_message_id, approver_user_id, tipo FROM absences WHERE user_id = ? AND status = ?', (user.id, 'approved')) as cursor:
                row = await cursor.fetchone()

            if not row:
                await interaction.response.send_message('No tienes ausencias aprobadas actualmente.', ephemeral=True)
                return

            absence_id, user_id, start_date, end_date, status, reason, public_message_id, approved_message_id, approver_user_id, tipo = row
            await db.execute('UPDATE absences SET status = ? WHERE id = ?', ('finished', absence_id))
            await db.commit()

            public_channel = interaction.client.get_channel(int(os.getenv('PUBLIC_CHANNEL_ID')))
            try:
                approved_message = await public_channel.fetch_message(approved_message_id)
                embed = approved_message.embeds[0]
                embed.color = discord.Color.red()
                embed.set_field_at(5, name="Estado", value="Finalizada", inline=False)
                await approved_message.edit(embed=embed)
                await approved_message.clear_reactions()
                await approved_message.add_reaction('✅')
            except discord.NotFound:
                print(f"Approved message with ID {approved_message_id} not found.")

        await interaction.response.send_message('Tu ausencia ha sido marcada como terminada.', ephemeral=True)
    except Exception as e:
        print(f'Error in /terminarausencia command: {e}')

def setup(bot):
    bot.tree.add_command(app_commands.Command(name='terminarausencia', description="Termina manualmente tu última ausencia", callback=terminarausencia))
