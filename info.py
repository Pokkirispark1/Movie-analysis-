# Telegram API Configuration
API_ID = 26592588  # Your API ID from my.telegram.org
API_HASH = "4f78c40e672ad86e10384cc8a0b43dc7"  # Your API Hash from my.telegram.org
BOT_TOKEN = "7341339052:AAE72GnRx-uGSxLueqDUKq2N0zQBo97Pu8M"  # Bot token from @BotFather

# MongoDB Configuration
MONGODB_URL = "mongodb+srv://analysisbot:analysisbot@cluster0.babcaob.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Your MongoDB connection URL
DATABASE_NAME = "Cluster0"  # Database name

# Channel/Chat Configuration
REPORT_CHANNEL_ID = -1003025331112 # Channel ID where daily reports will be sent

# Admin Configuration
ADMINS = [
    1769132732,  # Replace with actual admin user IDs
    560951157,  # Add more admin IDs as needed
]

# Bot Settings
BOT_NAME = "Movie Analysis Bot"
BOT_USERNAME = "newreqqccccbot"  # Your bot username without @

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "bot.log"

# Report Configuration
REPORT_TIME_HOUR = 6  # Hour to send daily reports (24-hour format)
REPORT_TIME_MINUTE = 0  # Minute to send daily reports

# Movie Detection Settings
MIN_MOVIE_NAME_LENGTH = 2  # Minimum length for movie names
MAX_MOVIE_REQUESTS_PER_MESSAGE = 5  # Maximum movie names to extract per message

# Additional Settings
TIMEZONE = "UTC"  # Bot timezone
MAX_MESSAGE_LENGTH = 4000  # Maximum message length for reports
