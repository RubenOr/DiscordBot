import os
import random
from datetime import datetime, time

import discord
import pytz
import redis

from discord.ext import commands

redis_server = redis.Redis()
DISCORD_TOKEN = str(redis_server.get('DISCORD_TOKEN').decode('utf-8'))
# DISCORD_CHANNEL = str(redis_server.get('DISCORD_CHAN').decode('utf-8'))

intents = discord.Intents.default()
# see guild members and their status
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!",intents=intents)
bot.remove_command('help')

def channel_update(guild:discord.Guild):
    try:
        bot_channel = bot.get_channel(int(redis_server.get(f'{str(guild)}_BOTCHAN').decode('utf-8')))
    except AttributeError:
        bot_channel = None

    return bot_channel

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to:')
    for guild in bot.guilds:
        print(f'{guild.id}:\t{guild.name}')



@bot.group(invoke_without_command=True,)
async def help(ctx):
    if ctx.channel == channel_update(ctx.guild):
        # primitive version of help command 
        emb = discord.Embed(title='Help', description="Use `!help <command>` for information about a specific command", color=discord.Colour.gold())
        emb.add_field(name="All Commands", value='`time`\n`decide`\n`whostinki`')
        await ctx.reply(embed=emb)

@help.command()
async def time(ctx):
    emb = discord.Embed(title='Time', description="Shows everyone's local time.", color=discord.Colour.gold())
    emb.add_field(name='**Usage**', value='`!time`')
    await ctx.reply(embed=emb)

@help.command()
async def decide(ctx):
    emb = discord.Embed(title='Decide', description="Bot chooses at random from any number of choices given. (Choices must be separated by a comma `,`  )", color=discord.Colour.gold())
    emb.add_field(name='**Usage**', value='!decide <option 1> `,` <option 2> `,` . . . `,` <option n>')
    await ctx.reply(embed=emb)

@help.command()
async def whostinki(ctx):
    emb = discord.Embed(title='whostinki', description="Bot chooses someone at random that is stinki.", color=discord.Colour.gold())
    emb.add_field(name='**Usage**', value='`!whostinki`')
    await ctx.reply(embed=emb)

@help.command()
async def stinkiboard(ctx):
    emb = discord.Embed(title='stinkiboard', description="Shows a leaderboard of who has been the most stinki.", color=discord.Colour.gold())
    emb.add_field(name='**Usage**', value='`!stinkiboard`')
    await ctx.reply(embed=emb)

@help.command()
async def _8ball(ctx):
    emb = discord.Embed(title='stinkiboard', description="Shows a leaderboard of who has been the most stinki.", color=discord.Colour.gold())
    emb.add_field(name='**Usage**', value='`!stinkiboard`')
    await ctx.reply(embed=emb)


@bot.command()
async def quit(ctx):
    if ctx.channel == channel_update(ctx.guild) and 'bot handler' in str(ctx.author.roles):
        print('closing connection')
        try:
            await bot.close()
        except RuntimeError:
            print('close success')
        print('close success')

@bot.command()
async def link(ctx):
    """
    [ADMIN USE ONLY]
    Assigns channel to use for Bot communication.
    """
    if 'bot handler' in str(ctx.author.roles):
        # try to assign channel to send messages to
        if redis_server.set(f'{str(ctx.guild)}_BOTCHAN', str(ctx.channel.id), nx=True) == 1:
            print(f'set {str(ctx.guild)} bot channel to id: {ctx.channel.id} name: {ctx.channel.name}')
            bot_channel = channel_update(ctx.guild)
            await bot_channel.send('This is now the assigned bot channel!')
        else:
            if ctx.channel == channel_update(ctx.guild):
                await ctx.reply('Bot is already linked to this channel!')
            else:
                await ctx.reply(f'Bot channel is already linked to {channel_update(ctx.guild).mention} !')

@bot.command()
async def unlink(ctx):
    """ 
    [ADMIN USE ONLY]
    Unassigns Bot communication channel.
    """
    if 'bot handler' in str(ctx.author.roles):
        if ctx.channel == channel_update(ctx.guild):
            # unassign linked channel
            if redis_server.delete(f'{str(ctx.guild)}_BOTCHAN') == 1:
                await ctx.reply('Channel has been unlinked.')
            else:
                await ctx.reply('Channel has not been linked.')
        else:
            await ctx.reply('Stinki Bot is not linked to this channel.')

@bot.command()        
async def decide(ctx, *choices: str):
    """
    Bot chooses at random from any number of choices given.
    """
    if ctx.channel == channel_update(ctx.guild):
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
            await ctx.reply(f'{random.choice(openings)} **{random.choice(options)}**')

@bot.command()
async def whostinki(ctx):
    """ 
    Bot chooses someone at random that is stinki.
    """
    if ctx.channel == channel_update(ctx.guild):
        members = ctx.guild.members

        stinki = random.choice(members)
        count = 0

        # count is to prevent infinite loop. stinki will never ping offline members
        # if member is bot or offline reroll pick
        while (stinki.bot or stinki.raw_status == 'offline' or str(stinki.id) =='705268624608198677') and count < 20:
            
            stinki = random.choice(members)
            count+=1

        if count == 20:
            msg = 'No one is stinki!'    
        else: 
            redis_server.incr(f"{stinki.id}_{ctx.guild}_count",1)
            msg = f'{stinki.mention} is stinki'

        await channel_update(ctx.guild).send(msg)

@bot.command()
async def stinkiboard(ctx):
    """
    Shows a leaderboard of who has been the most stinki.
    """
    if ctx.channel == channel_update(ctx.guild):
        members = ctx.guild.members
        board = []
        for m in members:
            if not m.bot:
                count = redis_server.get(f"{m.id}_{ctx.guild}_count")
                if count == None:
                    count = 0
                else:
                    count = int(count.decode('utf-8'))
                
                if m.nick==None:
                    board.append(tuple([m.name,count]))
                else:
                    board.append(tuple([m.nick,count]))
        
        board.sort(key= lambda x:x[1], reverse=True)

        msg = ">>>%40s | %s\n" % ('**Name**', '**Stinki Count**')
        msg += '%-40s | %5d\n' % (board[0][0],board[0][1])
        for member in board[1:]:
            msg += '%-40s | %5d\n' % (member[0],member[1])

        await ctx.send(msg)

@bot.command()
async def time(ctx):
    """
    Shows everyone's local time.
    """
    if ctx.channel == channel_update(ctx.guild):
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

        await channel_update(ctx.guild).send('Current times are:\n'+
                        '%-20s %s\n' % ("**Pacific**:",pst_time.strftime(fmt))+
                        '%-19s %s\n' % ("**Central**:",cst_time.strftime(fmt))+
                        '%-18s %s\n' % ("**Eastern**:",est_time.strftime(fmt))+
                        '%-21s %s' % ("**Chile**:",chile_time.strftime(fmt))
                        )

@bot.command(aliases=['8ball'])
async def _8ball(ctx):
    ball = [
        ("As I see it, yes"),
        ("It is certain"),
        ("It is decidedly so"),
        ("Most likely"),
        ("Outlook good"),
        ("Signs point to yes"),
        ("Without a doubt"),
        ("Yes"),
        ("Yes  definitely"),
        ("You may rely on it"),
        ("Reply hazy, try again"),
        ("Ask again later"),
        ("Better not tell you now"),
        ("Cannot predict now"),
        ("Concentrate and ask again"),
        ("Don't count on it"),
        ("My reply is no"),
        ("My sources say no"),
        ("Outlook not so good"),
        ("Very doubtful"),
    ]
    if ctx.channel == channel_update(ctx.guild):
        await ctx.reply(random.choice(ball))


bot.run(DISCORD_TOKEN)