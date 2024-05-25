import aiosqlite
import os

async def delete_db():
    if os.path.exists('absences.db'):
        os.remove('absences.db')
        print("Database deleted.")
    else:
        print("Database does not exist.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(delete_db())
