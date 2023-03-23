import discord
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
import os
from time import sleep
import random

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#test
intents = discord.Intents.all()


client = commands.Bot(command_prefix='!', intents=intents)\

client.players = {}
ready_count = 0
client.isHosted = False
client.gameHost = ""
client.amountOfSpies = 0
client.amountOfPlayers = 0

@client.command()
async def ready(ctx):
    hostTemp = str(ctx.author)

    if hostTemp in client.players:
        client.players[hostTemp][1] = 1
        state = await printPlayerState()
        await ctx.send(state)
        print(hostTemp)

@client.command()
async def unready(ctx):
    hostTemp = str(ctx.author)

    if hostTemp in client.players:
        client.players[hostTemp][1] = 0
        state = await printPlayerState()
        await ctx.send(state)
        print(client.players)

async def printPlayerState():
    sentence = ""
    for current in client.players:
        if(client.players[current][1] == 1):    
            sentence = sentence + current + " is: ✅\n"
        else: 
            sentence = sentence + current + " is: ❎\n"
    return sentence

async def checkEveryoneReady():
    for current in client.players:
        if(client.players[current][1] == 0):
            return False
    return True

async def checkIfPlayer(player):
    return player in client.players

@client.command()
async def startGame(ctx):
    if(not await checkIfPlayer(str(ctx.author))):
        print("NOT A PLAYER!")
        return
    '''
    if(not ctx.author.voice):
        await ctx.send("You are not in a voice channel!")
        return
    if(ctx.author.voice.channel != ctx.voice_client.channel):
        await ctx.send("You are not in the same channel as the Game Host!")
        return
    '''
    if(not await checkEveryoneReady()):
        await ctx.send("Not everyone is ready!")
        return
    else:    
        if(str(ctx.author) != client.gameHost):
            await ctx.send("You are not the Host! only the host can start the game!")
            return
        await ctx.send("DEBUG: Game Started!")
        for current in ctx.guild.members:
            if await checkIfPlayer(str(current)):
                message = "Your Role is: "
                if await generateSpy() == 0:
                    embed = discord.Embed(title=message + "Spy", description="Your job is to sabotage everything!")
                else:
                    embed = discord.Embed(title=message + "Innocent", description="Your job is to make sure everything goes well! find that spy!")
                await current.send(embed=embed)
        return


async def generateSpy():
    return random.randint(0,3)

@client.command()
async def host(ctx):        
    #if (not await joinCall(ctx)):
        #return
    hostTemp = str(ctx.author)
    if not client.isHosted:    
        client.isHosted = True 
        client.gameHost = hostTemp
        client.players = {}
        client.players[hostTemp] = ["None",0]
        await ctx.send(hostTemp + " is now hosting a new game!")
        client.amountOfPlayers += 1
        return
    else:
        await ctx.send("A Game is already being hosted!")
        return

    
async def joinCall(ctx):
    if(ctx.author.voice):
        channel = ctx.author.voice.channel
        await channel.connect()
        print(channel)
        print(ctx.voice_client.channel)
        return True
    else:
        await ctx.send("You must be connected to a voice channel to run this command!")
        return False
    

@client.command()
async def leavecall(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("I am not in a voice channel!")

@client.command()
async def leavegame(ctx):
    tempPlayer = str(ctx.author)
    if tempPlayer in client.players:
        del client.players[str(ctx.author)]  
        await ctx.send(tempPlayer + " has left the game!")
    

@client.command()
async def joingame(ctx):
    '''
    if(not ctx.author.voice):
        await ctx.send("you must be in a voice channel to join a game!")
        return

    if(ctx.author.voice.channel != ctx.voice_client.channel):
        await ctx.send("if you want to participate in the game you must be in the same voice channel as the bot!")
        return
    '''
    
    if(str(ctx.author) in client.players): 
        await ctx.send(str(ctx.author) + " is already participating in the game!")
    else:
        await ctx.send(str(ctx.author) + " has joined the game!")
        client.players[str(ctx.author)] = ["None",0]
        client.amountOfPlayers += 1
        print(client.players[str(ctx.author)])
                


@client.event
async def on_ready():
    print("INIT DONE")

        
@client.command()
async def debug(ctx):
    await ctx.send("isHosted: " + str(client.isHosted) + "\n")
    if client.isHosted:
        await ctx.send("Host: " + client.gameHost + "\n")
    await ctx.send("Players: \n" + str(client.players))


@client.command() 
async def credits(ctx):
    await ctx.send(f"Vocice acted by <@{540379480968134657}>\nConceptualized by <@{872496091336163438}> and <@{540379480968134657}>\nCode developed by <@{872496091336163438}> and <@{145065060568530944}> and <@{302817055080579084}>\nDebugged by <@{872496091336163438}> and <@{302817055080579084}>  ")

client.run(TOKEN)
