from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.API_ID = int(getenv("API_ID", 35508890))
        self.API_HASH = getenv("API_HASH", "a6eb1e2eb6a4fb440bc8d24c6dc18fbc")

        self.BOT_TOKEN = getenv("BOT_TOKEN", "8602594638:AAHVpQ_d68GCjWN2zbnsRAqn5hsI6X__eu4")
        self.MONGO_URL = getenv("MONGO_URL", "mongodb+srv://mustafaonurslsz_db_user:Nf91GSTS8K8ZwsRI@cluster0.bvknbf9.mongodb.net/?retryWrites=true&w=majority")

        self.LOGGER_ID = int(getenv("LOGGER_ID", -1004299297214))
        self.OWNER_ID = int(getenv("OWNER_ID", 8857741777))

        self.DURATION_LIMIT = int(getenv("DURATION_LIMIT", 60)) * 60
        self.QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", 20))
        self.PLAYLIST_LIMIT = int(getenv("PLAYLIST_LIMIT", 20))

        self.SESSION1 = getenv("SESSION", "BQId0poATVI9c2MJ0x_OtMuQoEyl4d2nF7FLydYNz46ghS9RdrKDHe39BNY3tlIlv9rX1THDLkQ6QkPlEYUaF4SNX8X-gI0AD1YyWZOHXX_Lhloy9ERHv9QHlGT62vUgtM-6Ogq1OSyDcZxE12yF3iqJ-R2x_oR1atZp1fWtorBMK1aYsHyESNlsCdakbBoSE4YHIqVtXKBkQqmpSYeyFga1yUBbdiFljcv9-llaGAbfJbfZzRBKEzCu-DcdPXfAOG5HG7YSoS5XwLW8-DDpKj5HFbU1P2vheJq71M6XSXgKerqANffsAfcuwVCr8b-p6hm6qSbL86wQLdSxyTrK0x6mg11chwAAAAIVDvDRAA")
        self.SESSION2 = getenv("SESSION2", None)
        self.SESSION3 = getenv("SESSION3", None)

        self.SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/fallenx")
        self.SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/DevilsHeavenMF")

        self.AUTO_LEAVE: bool = getenv("AUTO_LEAVE", "False").lower() == "true"
        self.AUTO_END: bool = getenv("AUTO_END", "False").lower() == "true"
    
        self.THUMB_GEN: bool = getenv("THUMB_GEN", "True").lower() == "true"
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", "True").lower() == "true"

        self.LANG_CODE = getenv("LANG_CODE", "tr")

        self.COOKIES_URL = []
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://te.legra.ph/file/3e40a408286d4eda24191.jpg")
        self.PING_IMG = getenv("PING_IMG", "https://files.catbox.moe/haagg2.png")
        self.START_IMG = getenv("START_IMG", "https://files.catbox.moe/zvziwk.jpg")

    def check(self):
        missing = [
            var
            for var in ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URL", "LOGGER_ID", "OWNER_ID", "SESSION1"]
            if not getattr(self, var)
        ]
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")