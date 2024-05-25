import discord
import aiosqlite

async def terminarausencia(interaction: discord.Interaction):
    try:
        user = interaction.user
        async with aiosqlite.connect('absences.db') as db:
            async with db.execute('SELECT * FROM absences WHERE user_id = ? AND status = ?', (user.id, 'approved')) as cursor:
                row = await cursor.fetchone()

            if not row:
                await interaction.response.send_message('No tienes ausencias aprobadas actualmente.', ephemeral=True)
                return

            absence_id, user_id, start_date, end_date, status, reason = row
            await db.execute('UPDATE absences SET status = ? WHERE id = ?', ('finished', absence_id))
            await db.commit()

            public_channel = interaction.client.get_channel(int(os.getenv('PUBLIC_CHANNEL_ID')))
            async for message in public_channel.history(limit=200):
                if f'Ausencia ID: {absence_id}' in message.content:
                    await message.clear_reactions()
                    await message.add_reaction('✅')
                    await message.edit(content=message.content.replace(":green_circle:", ":red_circle:"))
                    break

        await interaction.response.send_message('Tu ausencia ha sido marcada como terminada.', ephemeral=True)
    except Exception as e:
        print(f'Error in /terminarausencia command: {e}')

def setup(bot):
    bot.tree.add_command(app_commands.Command(name='terminarausencia', description="Termina manualmente tu última ausencia", callback=terminarausencia))
