import os
import discord
from discord.ext import commands
from groq import Groq
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialize Discord bot
intents = discord.Intents.default()
intents.messages = True
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
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Add the user's message to the conversation
    user_message = {"role": "user", "content": message.content}
    conversation.append(user_message)

    try:
        # Generate a response using Groq
        chat_completion = groq_client.chat.completions.create(
            messages=conversation,
            model="llama-3.3-70b-versatile"
        )
        bot_response = chat_completion.choices[0].message.content
        conversation.append({"role": "assistant", "content": bot_response})

        # Send the response back to the Discord channel
        await message.channel.send(bot_response)
    except Exception as e:
        await message.channel.send(f"Error: {e}")

# Run the bot
bot.run(os.environ.get("DISCORD_TOKEN"))