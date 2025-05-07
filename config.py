import os

from dotenv import load_dotenv

load_dotenv()

TOKEN: str = os.getenv("TOKEN")

db_file: str = "voices.db"

create_channel_id: int = 00000000000
category_channel_id: int = 00000000000

# example: "<:VoiceName:1113760036792057866>"
name_emoji: str = ""
limit_emoji: str = ""
kick_emoji: str = ""
invite_emoji: str = ""
allow_emoji: str = ""
forbid_emoji: str = ""
mute_emoji: str = ""
hear_emoji: str = ""
