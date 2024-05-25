import aiosqlite

async def create_db():
    async with aiosqlite.connect('absences.db') as db:
        await db.execute('DROP TABLE IF EXISTS absences')
        await db.execute('''
            CREATE TABLE absences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                start_date TEXT,
                end_date TEXT,
                status TEXT,
                reason TEXT
            )
        ''')
        await db.commit()
