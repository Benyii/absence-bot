import aiosqlite
from datetime import datetime, timedelta
from discord.ext import tasks
from absence_bot import AbsenceBot

@tasks.loop(hours=24)
async def check_absences():
    try:
        print("Checking absences...")
        now = datetime.utcnow()
        async with aiosqlite.connect('absences.db') as db:
            async with db.execute('SELECT * FROM absences WHERE status = ?', ('approved',)) as cursor:
                rows = await cursor.fetchall()
                print(f"Found {len(rows)} approved absences.")
                for row in rows:
                    absence_id, user_id, start_date, end_date, status, reason = row
                    end_date_dt = datetime.strptime(end_date, '%d-%m-%Y')
                    if end_date_dt <= now:
                        async with db.execute('UPDATE absences SET status = ? WHERE id = ?', ('finished', absence_id)):
                            await db.commit()
                        public_channel = AbsenceBot.get_channel(int(os.getenv('PUBLIC_CHANNEL_ID')))
                        async for message in public_channel.history(limit=200):
                            if f'Ausencia ID: {absence_id}' in message.content:
                                await message.clear_reactions()
                                await message.add_reaction('✅')
                                break
                    elif end_date_dt - now <= timedelta(days=1):
                        user = AbsenceBot.get_user(user_id)
                        await user.send(f'Tu ausencia está por finalizar en 1 día.')
        print("Finished checking absences.")
    except Exception as e:
        print(f'Error in check_absences task: {e}')
