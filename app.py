import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MovieAnalysisBot:
    def __init__(self):
        self.app = Client(
            "movie_analysis_bot",
            api_id=info.API_ID,
            api_hash=info.API_HASH,
            bot_token=info.BOT_TOKEN
        )
        
        # MongoDB setup with error handling
        try:
            self.mongo_client = MongoClient(info.MONGODB_URL)
            self.db = self.mongo_client[info.DATABASE_NAME]
            self.messages_collection = self.db.messages
            self.chats_collection = self.db.chats
            
            # Test MongoDB connection
            self.mongo_client.admin.command('ping')
            logger.info("MongoDB connection successful")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            # Continue without MongoDB for testing
            self.mongo_client = None
            self.db = None
            self.messages_collection = None
            self.chats_collection = None
        
        # Scheduler
        self.scheduler = AsyncIOScheduler()
        
        # Movie keywords and patterns
        self.movie_patterns = [
            r'\b(?:movie|film|series|show|season)\b',
            r'\b(?:watch|download|need|want|looking for)\b',
            r'\b(?:hindi|english|tamil|telugu|malayalam|dubbed)\b'
        ]
        
        self.setup_handlers()
        
    def setup_handlers(self):
        # Add a catch-all handler to see if ANY message is received
        @self.app.on_message()
        async def catch_all_messages(client, message: Message):
            logger.info(f"📨 Message received from chat {message.chat.id} ({message.chat.type}), user: {message.from_user.id if message.from_user else 'None'}")
            logger.info(f"📝 Message text: {message.text[:100] if message.text else 'No text'}...")
        
        @self.app.on_message(filters.command("start"))
        async def start_command(client, message: Message):
            logger.info(f"⭐ Start command received from user {message.from_user.id}")
            start_text = """
🎬 **Hi! I'm a Movie Analysis Bot made by Cinema Terminal** 🎬

I monitor your groups and analyze movie requests to provide daily reports!

**Commands:**
• `/addchat -100xxxxxxx` - Add a chat to monitoring
• `/removechat -100xxxxxxx` - Remove a chat from monitoring
• `/stats` - View current statistics
• `/report` - Generate instant report
• `/help` - Show this help message
• `/test` - Test if bot is working

**Features:**
✅ Automatic daily reports at 6:00 AM
✅ Movie request analysis
✅ Top 10 most requested movies
✅ MongoDB data storage
✅ Smart movie detection

**Contact:** @CinemaTerminal
            """
            try:
                await message.reply_text(start_text)
                logger.info(f"✅ Start message sent successfully to user {message.from_user.id}")
            except Exception as e:
                logger.error(f"❌ Error sending start message: {e}")

        @self.app.on_message(filters.command("addchat") & filters.user(info.ADMINS))
        async def add_chat(client, message: Message):
            try:
                chat_id = message.text.split()[1]
                chat_id = int(chat_id)
                
                # Check if chat already exists
                existing_chat = self.chats_collection.find_one({"chat_id": chat_id})
                if existing_chat:
                    await message.reply_text("❌ Chat is already being monitored!")
                    return
                
                # Add chat to database
                self.chats_collection.insert_one({
                    "chat_id": chat_id,
                    "added_by": message.from_user.id,
                    "added_date": datetime.now(),
                    "status": "active"
                })
                
                await message.reply_text(f"✅ Successfully added chat {chat_id} to monitoring!")
                logger.info(f"Chat {chat_id} added by admin {message.from_user.id}")
                
            except (IndexError, ValueError):
                await message.reply_text("❌ Please provide a valid chat ID!\nUsage: `/addchat -100xxxxxxxxx`")
            except Exception as e:
                await message.reply_text(f"❌ Error adding chat: {str(e)}")
                logger.error(f"Error adding chat: {e}")

        @self.app.on_message(filters.command("removechat") & filters.user(info.ADMINS))
        async def remove_chat(client, message: Message):
            try:
                chat_id = message.text.split()[1]
                chat_id = int(chat_id)
                
                result = self.chats_collection.delete_one({"chat_id": chat_id})
                if result.deleted_count > 0:
                    await message.reply_text(f"✅ Successfully removed chat {chat_id} from monitoring!")
                    logger.info(f"Chat {chat_id} removed by admin {message.from_user.id}")
                else:
                    await message.reply_text("❌ Chat not found in monitoring list!")
                    
            except (IndexError, ValueError):
                await message.reply_text("❌ Please provide a valid chat ID!\nUsage: `/removechat -100xxxxxxxxx`")
            except Exception as e:
                await message.reply_text(f"❌ Error removing chat: {str(e)}")
                logger.error(f"Error removing chat: {e}")

        @self.app.on_message(filters.command("stats") & filters.user(info.ADMINS))
        async def stats_command(client, message: Message):
            try:
                # Get monitored chats count
                chats_count = self.chats_collection.count_documents({"status": "active"})
                
                # Get today's message count
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                today_messages = self.messages_collection.count_documents({
                    "date": {"$gte": today}
                })
                
                # Get today's movie requests
                movie_requests = self.messages_collection.count_documents({
                    "date": {"$gte": today},
                    "is_movie_request": True
                })
                
                stats_text = f"""
📊 **Bot Statistics**

🔍 **Monitored Chats:** {chats_count}
📨 **Today's Messages:** {today_messages}
🎬 **Movie Requests Today:** {movie_requests}
📅 **Date:** {datetime.now().strftime("%d-%m-%Y")}
⏰ **Time:** {datetime.now().strftime("%H:%M:%S")}
                """
                
                await message.reply_text(stats_text)
                
            except Exception as e:
                await message.reply_text(f"❌ Error fetching stats: {str(e)}")
                logger.error(f"Error fetching stats: {e}")

        @self.app.on_message(filters.command("report") & filters.user(info.ADMINS))
        async def manual_report(client, message: Message):
            await message.reply_text("📊 Generating report...")
            await self.generate_and_send_report()

        @self.app.on_message(filters.command("test"))
        async def test_command(client, message: Message):
            logger.info(f"🧪 Test command received from user {message.from_user.id}")
            try:
                response = f"""
✅ **Bot is working perfectly!**

🤖 **Bot Info:**
• Username: @{client.me.username if client.me else 'Unknown'}
• Name: {client.me.first_name if client.me else 'Unknown'}

📊 **System Status:**
• MongoDB: {'✅ Connected' if self.mongo_client else '❌ Disconnected'}
• Scheduler: ✅ Running
• Handlers: ✅ Active

🕐 **Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

**Test successful! 🎉**
                """
                await message.reply_text(response)
                logger.info("✅ Test response sent successfully")
            except Exception as e:
                logger.error(f"❌ Error in test command: {e}")
                try:
                    await message.reply_text(f"❌ Error occurred: {str(e)}")
                except:
                    pass

        @self.app.on_message(filters.command("help"))
        async def help_command(client, message: Message):
            logger.info(f"📚 Help command received from user {message.from_user.id}")
            help_text = """
🔧 **Movie Analysis Bot Help**

**User Commands:**
• `/start` - Start the bot
• `/help` - Show this help
• `/test` - Test bot functionality

**Admin Commands:**
• `/addchat -100xxxxxxx` - Add chat to monitoring
• `/removechat -100xxxxxxx` - Remove chat from monitoring  
• `/stats` - View statistics
• `/report` - Generate instant report

**How it works:**
1. Add your groups using `/addchat`
2. Bot monitors all messages automatically
3. Analyzes movie requests using AI
4. Sends daily reports at 6:00 AM
5. Clears data after report generation

**Made with ❤️ by Cinema Terminal**
            """
            try:
                await message.reply_text(help_text)
                logger.info("✅ Help message sent successfully")
            except Exception as e:
                logger.error(f"❌ Error sending help message: {e}")
        
        # Simple fallback for unknown commands
        @self.app.on_message(filters.command("") & ~filters.regex(r"^/(start|help|test|addchat|removechat|stats|report)"))
        async def unknown_command(client, message: Message):
            logger.info(f"❓ Unknown command received: {message.text}")
            try:
                await message.reply_text("❓ Unknown command. Send /help to see available commands.")
            except Exception as e:
                logger.error(f"❌ Error in unknown command handler: {e}")

        @self.app.on_message(filters.text & ~filters.command(""))
        async def process_message(client, message: Message):
            logger.info(f"Received message from chat {message.chat.id}: {message.text[:50]}...")
            
            # Only process messages from monitored chats
            monitored_chat = self.chats_collection.find_one({
                "chat_id": message.chat.id,
                "status": "active"
            })
            
            if not monitored_chat:
                logger.info(f"Chat {message.chat.id} not monitored, skipping...")
                return
            
            try:
                # Analyze if message is a movie request
                is_movie_request, movie_names = self.analyze_movie_request(message.text)
                
                # Store message in database
                message_data = {
                    "chat_id": message.chat.id,
                    "chat_title": getattr(message.chat, 'title', 'Unknown'),
                    "user_id": message.from_user.id if message.from_user else None,
                    "username": message.from_user.username if message.from_user else None,
                    "message_text": message.text,
                    "date": datetime.now(),
                    "is_movie_request": is_movie_request,
                    "extracted_movies": movie_names,
                    "message_id": message.id
                }
                
                self.messages_collection.insert_one(message_data)
                
                if is_movie_request:
                    logger.info(f"Movie request detected: {movie_names} from chat {message.chat.id}")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    def analyze_movie_request(self, text: str) -> tuple[bool, List[str]]:
        """Analyze if a message is a movie request and extract movie names"""
        if not text:
            return False, []
        
        text_lower = text.lower()
        movie_names = []
        
        # Common movie request indicators
        movie_indicators = [
            'movie', 'film', 'series', 'show', 'season',
            'watch', 'download', 'need', 'want', 'looking for',
            'hindi', 'english', 'tamil', 'telugu', 'malayalam',
            'dubbed', 'subtitles', 'link', 'available'
        ]
        
        # Check if message contains movie indicators
        has_indicators = any(indicator in text_lower for indicator in movie_indicators)
        
        if not has_indicators:
            return False, []
        
        # Split text by common separators to find multiple movie names
        potential_movies = []
        separators = [',', '&', 'and', 'also', '+', '|']
        
        # First split by separators
        text_parts = [text]
        for sep in separators:
            new_parts = []
            for part in text_parts:
                new_parts.extend(part.split(sep))
            text_parts = new_parts
        
        # Process each part
        for part in text_parts:
            words = part.split()
            filtered_words = [word for word in words if len(word) >= info.MIN_MOVIE_NAME_LENGTH and word.lower() not in [
                'movie', 'film', 'series', 'show', 'season', 'watch', 'download', 
                'need', 'want', 'looking', 'for', 'hindi', 'english', 'tamil', 
                'telugu', 'malayalam', 'dubbed', 'subtitles', 'link', 'available',
                'please', 'anyone', 'have', 'send', 'share', 'upload', 'the', 'and', 'any',
                'with', 'please', 'bro', 'sir', 'guys', 'all', 'can', 'you', 'me'
            ]]
            
            if filtered_words:
                # Join words that might form movie names
                movie_name = ' '.join(filtered_words).strip()
                
                # Apply minimum movie name length check to the complete movie name
                if len(movie_name) >= info.MIN_MOVIE_NAME_LENGTH:
                    movie_names.append(movie_name)
                    
                    # Respect maximum movie requests per message
                    if len(movie_names) >= info.MAX_MOVIE_REQUESTS_PER_MESSAGE:
                        break
        
        return len(movie_names) > 0, movie_names

    async def generate_and_send_report(self):
        """Generate daily report and send to channel"""
        try:
            # Get today's date range
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            # Get all movie requests for today
            movie_requests = list(self.messages_collection.find({
                "date": {"$gte": today, "$lt": tomorrow},
                "is_movie_request": True
            }))
            
            if not movie_requests:
                report_text = f"""
📊 **Daily Movie Analysis Report**
📅 **Date:** {today.strftime("%d-%m-%Y")}

❌ **No movie requests found today!**

🔍 **Total Messages Monitored:** 0
🎬 **Movie Requests:** 0

**Made by Cinema Terminal** 🎭
                """
            else:
                # Count movie requests
                movie_counter = {}
                total_requests = 0
                
                for request in movie_requests:
                    for movie in request.get('extracted_movies', []):
                        movie_clean = movie.lower().strip()
                        if movie_clean:
                            movie_counter[movie_clean] = movie_counter.get(movie_clean, 0) + 1
                            total_requests += 1
                
                # Sort movies by request count
                sorted_movies = sorted(movie_counter.items(), key=lambda x: x[1], reverse=True)
                top_10 = sorted_movies[:10]
                
                # Generate report text
                report_text = f"""
📊 **Daily Movie Analysis Report**
📅 **Date:** {today.strftime("%d-%m-%Y")}

🎬 **Top Requested Movies:**

"""
                
                for i, (movie, count) in enumerate(top_10, 1):
                    report_text += f"{i}. {movie.title()} ({count} request{'s' if count > 1 else ''})\n"
                
                report_text += f"""
📈 **Summary:**
🔍 **Total Messages Monitored:** {len(movie_requests)}
🎬 **Total Movie Requests:** {total_requests}
🏆 **Unique Movies Requested:** {len(movie_counter)}

**Made by Cinema Terminal** 🎭
                """
            
            # Send report to channel
            if hasattr(info, 'REPORT_CHANNEL_ID'):
                await self.app.send_message(info.REPORT_CHANNEL_ID, report_text)
                logger.info(f"Daily report sent to channel {info.REPORT_CHANNEL_ID}")
            
            # Clear today's data after sending report
            deleted_count = self.messages_collection.delete_many({
                "date": {"$gte": today, "$lt": tomorrow}
            }).deleted_count
            
            logger.info(f"Cleared {deleted_count} messages from database")
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")

    async def start_scheduler(self):
        """Start the scheduler for daily reports"""
        # Schedule daily report at 6:00 AM
        self.scheduler.add_job(
            self.generate_and_send_report,
            CronTrigger(hour=6, minute=0),
            id='daily_report',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler started - Daily reports will be sent at 6:00 AM")

    async def run(self):
        """Start the bot"""
        await self.app.start()
        
        # Pyrogram uses polling by default, no need to clear webhooks
        logger.info("Using polling mode (default for Pyrogram)")
        
        await self.start_scheduler()
        logger.info("Movie Analysis Bot started successfully!")
        
        # Send a test message to verify bot is working
        try:
            bot_info = await self.app.get_me()
            logger.info(f"Bot started as: @{bot_info.username} ({bot_info.first_name})")
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
        
        # Keep the bot running
        await asyncio.Event().wait()

# Main execution
if __name__ == "__main__":
    bot = MovieAnalysisBot()
    asyncio.run(bot.run())
