import discord
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
import os
from time import sleep

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


intents = discord.Intents.all()


client = commands.Bot(command_prefix='!', intents=intents)\

players = []
ready_count = 0

@client.command()
async def ready(ctx):
    global Host
    Host = ctx.author
    await ctx.send(f"Ill join vc and wait for players, feel free to do **!start X** whenever you all are ready with 5v-8 players!")
    global channel 
    channel = ctx.author.voice.channel
    voice_client = await channel.connect()
    await voice_client.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
    global bot_ready
    bot_ready = True

@client.command()
async def unready(ctx):
    global channel
    if Host != ctx.author:
        await ctx.channel.send(f"You are not the host of this game!")
    else:
        voice_client = ctx.voice_client
        await voice_client.disconnect()
        await ctx.send(f"Ill go ahead and leave, When you can get a party and want to play again, Please do !ready")
        await channel.edit(user_limit=0)
        global bot_ready
        bot_ready = False


@client.command()
async def start(ctx, message):
    if bot_ready == True:
        global player_count
        global channel
        player_count = int(message)
        message = int(message)
        await channel.edit(user_limit=message+1)
        if message  <= 4 or message >= 9: 
            await ctx.send(f"please do '!start X' (where x is where x is how many players there are wishing to play in your voice channel!) you may have 5-8 players!")
        else:
            ready_check = await ctx.send(f"I'll go ahead and start the game when everyone is ready! Please do !play")
    else:
        await ctx.send(f"A game is not running! Please do !ready to start a game")

@client.command()
async def play(ctx):
    await ctx.send("A player is ready!")
    global player_count
    global players
    global ready_count
    players.append(ctx.author)
    ready_count += 1
    if ready_count == player_count:
        await ctx.send("Game Starting, If it was done!")
        #add the game function here!
        ready_count = 0
    else:
        pass
                




        

@client.command() 
async def credits(ctx):
    await ctx.send(f"Vocice acted by <@{540379480968134657}>\nConceptualized by <@{872496091336163438}> and <@{540379480968134657}>\nCode developed by <@{872496091336163438}> and <@{145065060568530944}> and <@{302817055080579084}>\nDebugged by <@{872496091336163438}> and <@{302817055080579084}>  ")

client.run(TOKEN)
