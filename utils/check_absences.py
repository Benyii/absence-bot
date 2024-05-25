import aiosqlite
from datetime import datetime, timedelta
import discord
import os

async def check_absences(bot):
    print("Started check_absences task.")
    async with aiosqlite.connect('absences.db') as db:
        async with db.execute('SELECT id, user_id, start_date, end_date, status, reason, public_message_id, approved_message_id, approver_user_id, tipo FROM absences WHERE status = ?', ('approved',)) as cursor:
            rows = await cursor.fetchall()

        now = datetime.utcnow()

        for row in rows:
            absence_id, user_id, start_date, end_date, status, reason, public_message_id, approved_message_id, approver_user_id, tipo = row
            end_date_dt = datetime.strptime(end_date, '%d-%m-%Y')
            if end_date_dt <= now:
                async with db.execute('UPDATE absences SET status = ? WHERE id = ?', ('finished', absence_id)):
                    await db.commit()
                public_channel = bot.get_channel(int(os.getenv('PUBLIC_CHANNEL_ID')))
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
            elif end_date_dt - now <= timedelta(days=1):
                user = bot.get_user(user_id)
                await user.send(f'Tu ausencia está por finalizar en 1 día.')
    print("Finished checking absences.")
