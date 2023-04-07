import discord
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
import os
from time import sleep
import random
import asyncio

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#test
intents = discord.Intents.all()


client = commands.Bot(command_prefix='!', intents=intents)

client.players = {}
client.isHosted = False
client.gameHost = ""
client.amountOfSpies = 0
client.amountOfPlayers = 0
client.spies = {}

# 0 = Talking ; 1 = Voting ; 2 = Mission
client.gamePhase = 0
client.remainingPhases = 5
client.currentLeader = ""
client.currentTeam = ["","",""]
client.currentVote = {}
client.nodeHacked = 0
client.amountOfNodeCommands = 0
client.hostCtx = None


client.state = 0

@client.command()
async def ready(ctx):
    if (client.state != 1):
        return

    hostTemp = str(ctx.author)

    if hostTemp in client.players:
        client.players[hostTemp][1] = 1
        state = await printPlayerState()
        await ctx.send(state)

@client.command()
async def unready(ctx):
    if (client.state != 1):
        return

    hostTemp = str(ctx.author)

    if hostTemp in client.players:
        client.players[hostTemp][1] = 0
        state = await printPlayerState()
        await ctx.send(state)

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
    if (client.state != 1):
        return
    if(not await checkIfPlayer(str(ctx.author))):
        return
    if(not ctx.author.voice):
        await ctx.send("You are not in a voice channel!")
        return
    if(ctx.author.voice.channel != ctx.voice_client.channel):
        await ctx.send("You are not in the same channel as the Game Host!")
        return
    if(not await checkEveryoneReady()):
        await ctx.send("Not everyone is ready!")
        return
    else:    
        if(str(ctx.author) != client.gameHost):
            await ctx.send("You are not the Host! only the host can start the game!")
            return
        
        if client.amountOfPlayers <= 5 :
            client.amountOfSpies = 1
        else:
            client.amountOfSpies = 2
        tempDict = client.players.copy()
        while client.amountOfSpies > 0:
            listHelper = list(tempDict.keys())
            randomSpy = listHelper[random.randint(0,len(listHelper)-1)]
            tempDict.pop(randomSpy)
            for current in ctx.guild.members:
                if str(current) == randomSpy:
                    client.spies[str(current)] = 1
                    message = "Your Role is: "
                    embed = discord.Embed(title=message + "Spy", description="Your job is to sabotage everything!\n\n!vote [yes/no], to vote on node-teams\n!secure, to secure a node\n!hack, to hack a node", color=0xff0000)
                    await current.send(embed=embed)
            client.amountOfSpies -= 1
        for current in ctx.guild.members:
            if str(current) in tempDict:
                    message = "Your Role is: "
                    embed = discord.Embed(title=message + "Innocent", description="Your job is to make sure everything goes well! find that spy!\n\n!vote [yes/no], to vote on node-teams\n!secure, to secure a node", color=0x00f7ff)
                    await current.send(embed=embed)

        await ctx.send("Game Has Started! make sure you checked your role in dm's!")
        
        secondsTemp = 5
        message = await ctx.send("Get Ready! " + str(secondsTemp) + " until the game starts!")
        while True:
            secondsTemp -= 1
            if secondsTemp <= 0:
                await message.edit(content="The first round is Starting!")
                break
            await message.edit(content="Get Ready! " + str(secondsTemp) + " until the game starts!")
            await asyncio.sleep(1)

        await newNode(ctx=ctx)
        return
    
async def newNode(ctx):
    client.state = 2
    client.currentLeader = await getNewLeader()
    await ctx.send(await printGamePhase())
    await waitForSeconds(5)
    await changeGamePhase()
    await ctx.send(await printGamePhase())
    return
    
@client.command()
async def assemble(ctx, p1, p2, p3):
    if (client.gamePhase != 1) or (str(ctx.author) != client.currentLeader):
        await ctx.author.send("It is not currently the assembling phase, or you're not the current leader!")
        return
    await ctx.send("The chosen team is: " + p1 + ", " + p2 + " and " + p3 + "!")
    client.currentTeam[0] = p1
    client.currentTeam[1] = p2
    client.currentTeam[2] = p3
    client.currentVote = client.players.copy()
    try:
        client.currentVote.pop(p1)
        client.currentVote.pop(p2)
        client.currentVote.pop(p3)
    except:
        print("NO SUCH PLAYER!")
    for current in client.currentVote:
        client.currentVote[current][1] = 2
    print(client.currentVote)
    await ctx.send("Everyone else may now vote on this decision!")
    return

@client.command()
async def vote(ctx, arg):
    try:
        if "N" in arg:
            client.currentVote[str(ctx.author)][1] = 0
        elif "Y" in arg:
            client.currentVote[str(ctx.author)][1] = 1 
    except:
        print("NOT IN DICT")
    countY = 0
    countN = 0
    for current in client.currentVote:
        if client.currentVote[str(current)][1] == 1:
            countY += 1
        elif client.currentVote[str(current)][1] == 0:
            countN += 1
    await ctx.send("There are currently " + str(countY) + " votes FOR this team, and " + str(countN) + " AGAINST it!")

@client.command()
async def finishVote(ctx):
    if (str(ctx.author) != client.currentLeader) or (client.gamePhase != 1):
        await ctx.author.send("It is not currently the voting phase, or you're not the current leader!")
        return
    for current in client.currentVote:
        if client.currentVote[str(current)][1] == 2:
            await ctx.author.send("Not everyone has voted yet!")
            return
    countY = 0
    countN = 0
    for current in client.currentVote:
        if client.currentVote[str(current)][1] == 1:
            countY += 1
        elif client.currentVote[str(current)][1] == 0:
            countN += 1
    if countY >= countN:
        await ctx.send("The vote is over, and the team was voted FOR!")
    else:
        await ctx.send("The vote is over, and the team was voted AGAINST!")
    await changeGamePhase()
    await ctx.send(await printGamePhase())
    await waitForSeconds(5)
    await ctx.send("You may now decide on your action during the expedition!\n(do make sure you write your command to me in dms, otherwise you'll end up spoiling the game!)")
    return      

@client.event
async def on_message(message):
    await client.process_commands(message)
    if ((client.gamePhase == 2) and (str(message.author) in client.currentTeam)):
        if(str(message.content) == "secure"):
            await message.channel.send("Node has been secured!")
            client.amountOfNodeCommands += 1 
        elif((str(message.content) == "hack") and (str(message.author) in client.spies)):
            await message.channel.send("Node has been hacked!")   
            client.amountOfNodeCommands += 1 
            client.nodeHacked += 1  
        if client.amountOfNodeCommands >= 3:
            await changeGamePhase()
            return
    

    
async def changeGamePhase():
    if client.gamePhase == 2:
        client.gamePhase = 0
        client.remainingPhases -= 1
        await client.hostCtx.send("The expedition has now been concluded with...")
        await client.hostCtx.send("The Node has been hacked " + str(client.nodeHacked) + " times!")
        await client.hostCtx.send("There are " + str(client.remainingPhases) + " Nodes remaining!")
        await client.hostCtx.send("The next Node will begin shortly!")
        client.amountOfNodeCommands = 0
        client.nodeHacked = 0
        await waitForSeconds(5)
        await newNode(client.hostCtx)
    else:
        client.gamePhase += 1

async def printGamePhase():
    if client.gamePhase == 0:
        return "Current Phase: **TALKING!**\nMake sure you know who you want to vote for the expedition!\nYou have 90 seconds!\nThis Round's Leader is: " + client.currentLeader
    elif client.gamePhase == 1:
        return "Current Phase: **VOTING!**\nThe current leader can now assemble an expedition group, and the rest can vote on it!"
    elif client.gamePhase == 2:
        return "Current Phase: **EXPEDITION!**\nThose of you that are undertaking the expedition can now prepare to secure the node!\nYou have 15 seconds to decide!"
    
async def getNewLeader():
    listHelper = list(client.players.keys())
    currentRandom = random.randint(0,len(listHelper)-1)
    return str(listHelper[currentRandom])

async def waitForSeconds(seconds):
    while True:
        seconds -= 1
        if seconds <= 0:
            break
        await asyncio.sleep(1)
    print("Timer Ended!")

async def generateSpy():
    return random.randint(0,3)

@client.command()
async def host(ctx):        
    if (client.state != 0):
        return
    if (not await joinCall(ctx)):
        return
    client.state = 1
    client.hostCtx = ctx
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
    if(not ctx.author.voice):
        await ctx.send("you must be in a voice channel to join a game!")
        return

    if(ctx.author.voice.channel != ctx.voice_client.channel):
        await ctx.send("if you want to participate in the game you must be in the same voice channel as the bot!")
        return
    
    if(str(ctx.author) in client.players): 
        await ctx.send(str(ctx.author) + " is already participating in the game!")
    else:
        await ctx.send(str(ctx.author) + " has joined the game!")
        client.players[str(ctx.author)] = ["None",0]
        client.amountOfPlayers += 1
                


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
