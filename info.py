# Telegram API Configuration
API_ID = 12345678  # Your API ID from my.telegram.org
API_HASH = "your_api_hash_here"  # Your API Hash from my.telegram.org
BOT_TOKEN = "your_bot_token_here"  # Bot token from @BotFather

# MongoDB Configuration
MONGODB_URL = "mongodb://localhost:27017/"  # Your MongoDB connection URL
DATABASE_NAME = "movie_analysis_bot"  # Database name

# Channel/Chat Configuration
REPORT_CHANNEL_ID = -1001234567890  # Channel ID where daily reports will be sent

# Admin Configuration
ADMINS = [
    123456789,  # Replace with actual admin user IDs
    987654321,  # Add more admin IDs as needed
]

# Bot Settings
BOT_NAME = "Movie Analysis Bot"
BOT_USERNAME = "movieanalysisbot"  # Your bot username without @

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
