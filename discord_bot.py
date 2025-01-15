import os
import discord
from discord.ext import commands
from pymongo import MongoClient
from groq import Groq
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# MongoDB Setup
mongo_client = MongoClient(os.environ.get("MONGO_URI"))
db = mongo_client["bot_database"]  # Replace with your database name
messages_collection = db["messages"]  # Replace with your collection name

# Initialize Groq client
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Conversation history (optional)
conversation = [
    {"role": "system", "content": "You are a helpful assistant."}
]

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    print(message.content)
    if message.author == bot.user:
        return

    user_message = message.content
    username = message.author.name
    channel_name = message.channel.name

    try:
        # Save user message to MongoDB
        messages_collection.insert_one({
            "username": username,
            "channel": channel_name,
            "role": "user",
            "message": user_message,
        })

        # Generate a response using Groq
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
            model="llama-3.3-70b-versatile",
        )

        bot_response = chat_completion.choices[0].message.content

        # Save bot's response to MongoDB
        messages_collection.insert_one({
            "username": "Bot",
            "channel": channel_name,
            "role": "assistant",
            "message": bot_response,
        })

        # Send the response back to the Discord channel
        await message.channel.send(bot_response)

    except Exception as e:
        await message.channel.send(f"Error: {e}")

# Run the bot
bot.run(os.environ.get("DISCORD_TOKEN"))