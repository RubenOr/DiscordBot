import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
bot = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print(f'{client.user} has connected to {client.guilds}!')

    
        
@bot.command(name='whostinki') 
async def on_message(message):
    if message.author == client.user:
        return
    
    print(discord.User)

    msg = "bingbong"
    await message.channel.send(msg)
    

client.run(TOKEN)