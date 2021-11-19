import os
import discord
import random
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members=True
bot = commands.Bot(command_prefix="!",intents=intents)

@bot.event
async def on_ready():
    
    print(f'{bot.user} has connected to {bot.guilds[0].name}!')
    channel = bot.get_channel(910630657716260877)
    time = datetime.now().strftime('%H:%M')
    print(time)
    init = 'stinki started at %sCST' % time 
    await channel.send(init)
    #channel = discord.TextChannel
        
@bot.command()
async def whostinki(ctx):
    for member in ctx.guild.members:
        print('%s' % member.name)
    #print(members)
    msg = "ur stinki"
    await ctx.send(msg)
    
@bot.command()
async def test(ctx):
    print(ctx.guild.users)
    #await ctx.send('test')

bot.run(TOKEN)