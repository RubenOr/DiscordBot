import os
import discord
import random
import pytz
from datetime import datetime, time
from discord import channel
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
# see guild members and their status
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!",intents=intents)

@bot.event
async def on_ready():
    txt_channel = bot.get_channel(910997848986882129)
    # send message on channel join
    print(f'{bot.user} has connected to {bot.guilds[0].name}!')

    time = datetime.now().strftime('%I:%M')
    init = f'stinki started at {time}'

    await txt_channel.send(init)

@bot.command()
async def quit(ctx):
    print('closing connection')
    await bot.close()

@bot.command()
async def connect(ctx):
    # try to assign channel to send messages to
    

    print(ctx.channel.id)
    return None

@bot.command()        
async def decide(ctx, *choices: str):
    # decides between given choices separated by comma(',') delimiter
    options = ' '.join([''.join(opt) for opt in choices]).split(',')

    if len(options) < 2:
        await ctx.reply(f'Sorry, please include more choices for me to choose from!')
    else:
        openings = ['I\'m going with', 
                    'I think you guys should choose',
                    'stinki says',
                    ]
        await ctx.reply(f'{random.choice(openings)} {random.choice(options)}')

@bot.command()
async def whostinki(ctx):
    # gets members of guild and chooses one at random excluding bot(s). if all members are offline return "No one is stinki" message
    members = ctx.guild.members

    stinki = random.choice(members)
    #print(f'{stinki.name} is {stinki.raw_status}')
    count = 0

    # count is to prevent infinite loop. stinki will never ping offline members
    # if member is bot or offline reroll pick
    while (stinki.bot or stinki.raw_status == 'offline') and count < 20:
        stinki = random.choice(members)
        count+=1

    if count == 20:
        msg = 'No one is stinki!'    
    else: 
        msg = f'{stinki.mention} is stinki'

    await ctx.send(msg)

@bot.command()
async def time(ctx):
    # show everyones current times in different timezones
    fmt = '%I:%M %p'
    now = datetime.now(pytz.utc)

    pst_tz = pytz.timezone('America/Los_Angeles')
    cst_tz = pytz.timezone('America/Chicago')
    est_tz = pytz.timezone('America/New_York')
    chile_tz = pytz.timezone('America/Santiago')

    pst_time = now.astimezone(pst_tz)
    cst_time = now.astimezone(cst_tz)
    est_time = now.astimezone(est_tz)
    chile_time = now.astimezone(chile_tz)
    # now.strftime('%H:%M %m %d')   

    await ctx.send('Current times are:\n'+
                    f'**Pacific**:\t {pst_time.strftime(fmt)}\n'+
                    f'**Central**:\t{cst_time.strftime(fmt)}\n'+
                    f'**Eastern**:   {est_time.strftime(fmt)}\n'+
                    f'**Chile**:\t\t{chile_time.strftime(fmt)}'
                    )

bot.run(TOKEN)