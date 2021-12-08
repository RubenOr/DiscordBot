import os
import random
from datetime import datetime, time

import discord
import pytz
import redis

from discord import channel
from discord.ext import commands

redis_server = redis.Redis()
DISCORD_TOKEN = str(redis_server.get('DISCORD_TOKEN').decode('utf-8'))
# DISCORD_CHANNEL = str(redis_server.get('DISCORD_CHAN').decode('utf-8'))

intents = discord.Intents.default()
# see guild members and their status
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!",intents=intents)

def channel_update():
    try:
        bot_channel = bot.get_channel(int(redis_server.get('DISCORD_BOTCHAN').decode('utf-8')))
    except AttributeError:
        print('DNE')
        bot_channel = None

    return bot_channel

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to:')
    for guild in bot.guilds:
        print(f'{guild.id}:\t{guild.name}\n')

    txt_channel = channel_update()

    time = datetime.now(pytz.utc).astimezone(pytz.timezone('America/Chicago'))
    init = f'stinki started at {time.strftime("%I:%M %p")} CST'

    if txt_channel == None:
        print('Bot has not been linked')
    else:
        await txt_channel.send(init)

@bot.command()
async def quit(ctx):
    if ctx.channel == channel_update():
        print('closing connection')
        try:
            await bot.close()
        except RuntimeError:
            print('close success')
        print('close success')


@bot.command()
async def link(ctx):
    # bot manager role only 

    
    # try to assign channel to send messages to
    if redis_server.set('DISCORD_BOTCHAN', str(ctx.channel.id), nx=True) == 1:
        print(f'set bot channel to id: {ctx.channel.id} name: {ctx.channel.name}')
        bot_channel = channel_update()
        await bot_channel.send('This is now the assigned bot channel!')
    else:
        await ctx.send(f'Bot channel is already linked to {channel_update().mention} !')

    return None

@bot.command()
async def unlink(ctx):
    # bot manager role only 

    if ctx.channel == channel_update():
        # unassign linked channel
        if redis_server.delete('DISCORD_BOTCHAN') == 1:
            await ctx.send('Channel has been unlinked.')
        else:
            await ctx.send('Channel has not been linked.')
    else:
        await ctx.send('Stinki Bot is not linked to this channel.')

    return None

@bot.command()        
async def decide(ctx, *choices: str):
    if ctx.channel == channel_update():
        # decides between given choices separated by comma(',') delimiter
        options = ' '.join([''.join(opt) for opt in choices]).split(',')

        if len(options) < 2:
            await ctx.reply(f'Sorry, please include more choices for me to choose from!\n'+
                            'Format: <option 1> `,` <option 2> `,` . . . `,` <option n>')
        else:
            openings = ['I\'m going with', 
                        'I think you guys should choose',
                        'stinki says',
                        ]
            await ctx.reply(f'{random.choice(openings)} {random.choice(options)}')

@bot.command()
async def whostinki(ctx):
    # gets members of guild and chooses one at random excluding bot(s). if all members are offline return "No one is stinki" message
    if ctx.channel == channel_update():
        members = ctx.guild.members

        stinki = random.choice(members)
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

        await channel_update().send(ctx.author.mention +': ' + msg)

@bot.command()
async def time(ctx):
    if ctx.channel == channel_update():
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

        await channel_update().send('Current times are:\n'+
                        f'**Pacific**:\t {pst_time.strftime(fmt)}\n'+
                        f'**Central**:\t{cst_time.strftime(fmt)}\n'+
                        f'**Eastern**:   {est_time.strftime(fmt)}\n'+
                        f'**Chile**:\t\t{chile_time.strftime(fmt)}'
                        )

bot.run(DISCORD_TOKEN)