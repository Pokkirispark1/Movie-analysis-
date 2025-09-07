import os

# Telegram API Configuration
API_ID = int(os.getenv("API_ID", "26592588"))  # Your API ID from my.telegram.org
API_HASH = os.getenv("API_HASH", "4f78c40e672ad86e10384cc8a0b43dc7")  # Your API Hash from my.telegram.org
BOT_TOKEN = os.getenv("BOT_TOKEN", "7341339052:AAE72GnRx-uGSxLueqDUKq2N0zQBo97Pu8M")  # Bot token from @BotFather

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://analysisbot:analysisbot@cluster0.babcaob.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Your MongoDB connection URL
DATABASE_NAME = os.getenv("DATABASE_NAME", "Cluster0")  # Database name

# Channel/Chat Configuration
REPORT_CHANNEL_ID = int(os.getenv("REPORT_CHANNEL_ID", "-1003025331112"))  # Channel ID where daily reports will be sent

# Admin Configuration
ADMINS = [
    int(admin_id) for admin_id in os.getenv("ADMINS", "1769132732,560951157").split(",") if admin_id.strip()
]  # Comma-separated admin user IDs

# Bot Settings
BOT_NAME = os.getenv("BOT_NAME", "Movie Analysis Bot")  # Bot name
BOT_USERNAME = os.getenv("BOT_USERNAME", "newreqqccccbot")  # Bot username without @

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # Log level
LOG_FILE = os.getenv("LOG_FILE", "bot.log")  # Log file name

# Report Configuration
REPORT_TIME_HOUR = int(os.getenv("REPORT_TIME_HOUR", "6"))  # Hour to send daily reports (24-hour format)
REPORT_TIME_MINUTE = int(os.getenv("REPORT_TIME_MINUTE", "0"))  # Minute to send daily reports

# Movie Detection Settings
MIN_MOVIE_NAME_LENGTH = int(os.getenv("MIN_MOVIE_NAME_LENGTH", "2"))  # Minimum length for movie names
MAX_MOVIE_REQUESTS_PER_MESSAGE = int(os.getenv("MAX_MOVIE_REQUESTS_PER_MESSAGE", "5"))  # Maximum movie names to extract per message

# Additional Settings
TIMEZONE = os.getenv("TIMEZONE", "UTC")  # Bot timezone
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "4000"))  # Maximum message length for reports
