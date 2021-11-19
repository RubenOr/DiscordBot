import os
import discord
import random
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    
    print(f'{bot.user} has connected to {bot.guilds[0].name}!')
    channel = bot.get_channel(910630657716260877)
    time = datetime.now().strftime('%H:%M')
    print(time)
    await channel.send('stinki started at {time} CST')
    #channel = discord.TextChannel
        
@bot.command()
async def whostinki(ctx):
    msg = "ur stinki"
    print("here")
    await ctx.send(msg)
    
@bot.command()
async def test(ctx):
    print(ctx.guild.users)
    #await ctx.send('test')

bot.run(TOKEN)