import aiosqlite
import os

async def create_db():
    create_db_flag = os.getenv('CREATE_DB', 'false').lower() in ['true', '1', 't']
    if create_db_flag:
        async with aiosqlite.connect('absences.db') as db:
            await db.execute('DROP TABLE IF EXISTS absences')
            await db.execute('''
                CREATE TABLE absences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    start_date TEXT,
                    end_date TEXT,
                    status TEXT,
                    reason TEXT,
                    message_id INTEGER
                )
            ''')
            await db.commit()
        print("Database created.")
    else:
        print("Database creation skipped.")
