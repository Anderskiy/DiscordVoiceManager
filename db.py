import aiosqlite
from config import db_file

class TempVoices:
    _table = 'tempvoices'
    _key_column = 'channel_id'
    owner_id: int
    channel_id: int
    blocked: list

    def __init__(self, owner_id, channel_id, blocked=None):
        self.owner_id = owner_id
        self.channel_id = channel_id
        self.blocked = blocked or []

    @classmethod
    async def select(cls, user_id=None):
        async with aiosqlite.connect(db_file) as db:
            cursor = await db.execute(f'SELECT * FROM `{cls._table}` WHERE `{cls._key_column}`=?', (user_id,))
            data = await cursor.fetchone()

        if not data:
            return None
        return data

    @classmethod
    async def load(cls, channel_id):
        res = await cls.select(channel_id)
        return res if res else None

    @classmethod
    async def load_by_owner(cls, owner_id):
        async with aiosqlite.connect(db_file) as db:
            cursor = await db.execute('SELECT * FROM `tempvoices` WHERE `owner_id`=?', (owner_id,))
            data = await cursor.fetchone()

        return cls(*data) if data else None

    @classmethod
    async def voice_create(cls, channel_id, owner_id):
        async with aiosqlite.connect(db_file) as db:
            await db.execute('INSERT INTO tempvoices (owner_id, channel_id) VALUES (?, ?)', (owner_id, channel_id))
            await db.commit()

        return await TempVoices.load(channel_id)

    @classmethod
    async def voice_delete(cls, channel_id):
        async with aiosqlite.connect(db_file) as db:
            await db.execute('DELETE FROM tempvoices WHERE channel_id = ?', (channel_id,))
            await db.commit()

    @classmethod
    async def give_owner(cls, channel_id, owner_id):
        async with aiosqlite.connect(db_file) as db:
            await db.execute('UPDATE tempvoices SET owner_id=? WHERE channel_id=?', (owner_id, channel_id))
            await db.commit()