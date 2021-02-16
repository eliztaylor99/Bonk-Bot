# bot.py
# Code by Rhys Sullivan & Stack Overflow
import os
import io
import requests
import discord
import json
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

async def scrapeboard(guild):
    if guild.name == "Bloodlust and Lies":
        usersDict = json.load(open("dictionary.txt"))
        for channel in guild.channels:
            validChannels = ["bonk-bot"]
            if channel.name in validChannels:
                print(channel.name)
                messages = await channel.history(limit=2000).flatten()
                for message in messages:
                    if "!bonk" in message.content:
                        for user in message.mentions:
                            print(message.content)
                            if str(user.id) in usersDict:
                                usersDict[str(user.id)] = [usersDict[str(user.id)][0] + 1, user.display_name]
                            else:
                                usersDict[str(user.id)] = [1, user.display_name]
        json.dump(usersDict, open("dictionary.txt", "w"))


class MyClient(discord.Client):   
    canGlobalBonk = True 
    async def on_ready(self):
        print('Logged into:')
        for guild in self.guilds:
            print(guild.name)


    async def on_message(self, message):
        if self.user == message.author:
            return
        if 'version' in message.content:
            await message.channel.send("0.2.4")
        if '!bonkboard' in message.content:
            usersDict = json.load(open("dictionary.txt"))
            allBonks = []
            for item in usersDict.items():
                allBonks.append(item[1])

            allBonks.sort(reverse=True)
            embedVar = discord.Embed(title="Bonk Leaderboard", value="", color=0xff0000)
            for x in range(0, 4):
                embedVar.add_field(name="{0}".format(allBonks[x][1]), value="{0} bonks".format(allBonks[x][0]), inline=False)
            await message.channel.send(embed=embedVar)
        elif '!bonks' in message.content:
            for user in message.mentions:
                usersDict = json.load(open("dictionary.txt"))
                if str(user.id) in usersDict:
                    numBonks = usersDict[str(user.id)]
                    response = "{0} has been bonked {1} times".format(user.display_name, numBonks[0])
                    await message.channel.send(response)
                else:
                    response = "{0} has not been bonked yet".format(user.display_name)
                    await message.channel.send(response)
        elif '!bonk' in message.content:
            members = message.mentions;
            if ('@everyone' in message.content) or ('@global-bonk' in message.content) and self.canGlobalBonk:                                
                members = await message.guild.fetch_members(limit=None).flatten()            
            for user in members:
                r = requests.get(user.avatar_url, stream=True)
                if r.status_code == 200:
                    background = Image.open(io.BytesIO(r.content)) # Download the profile picture directly to memory                    
                    background = background.convert("P", palette=Image.ADAPTIVE, colors=256)
                    #background.save(os.path.join('profile.png'), quality=85) # CODE TO SAVE THE FILE
                    print(user.id)
                    print(user.avatar_url)                    
                    gif = Image.open('Media/TransparentBonkGif.gif')                                        
                    background = background.convert("RGBA")
                    imgSize = (256,256)
                    background = background.resize(imgSize)
                    images = []
                    for frame in range(0, gif.n_frames):
                        gif.seek(frame)
                        images.append(Image.alpha_composite(background, gif.resize(imgSize).convert("RGBA")))                        
                        gif.seek(0)
                    arr = io.BytesIO()
                    images[0].save(arr, format='GIF', save_all=True, append_images=images[1:], duration=100, loop=0)
                    arr.seek(0)
                    await message.channel.send(file = discord.File(arr, 'bonk.gif'))

                    usersDict = json.load(open("dictionary.txt"))

                    if str(user.id) in usersDict:
                        usersDict[str(user.id)] = [usersDict[str(user.id)][0] + 1, user.display_name]
                    else:
                        usersDict[str(user.id)] = [1, user.display_name]                                        
                    json.dump(usersDict, open("dictionary.txt", "w"))

                    allBonks = 0
                    for item in usersDict.items():
                        allBonks += item[1][0]

                    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="{0} bonks".format(allBonks)))
        if message.author.id == 241702743834624000:            
            await message.add_reaction("🇭")
        if message.author.id == 523949187663134754:
            if '!clear' in message.content:
                for user in message.mentions:
                    usersDict = json.load(open("dictionary.txt"))
                    if str(user.id) in usersDict:
                        usersDict[str(user.id)] = (0, user.id)
                        await message.channel.send("Cleared {0}".format(user.display_name))                                                                                  
                    json.dump(usersDict, open("dictionary.txt", "w"))
        authorized = [523949187663134754, 179037422389166080, 262238367079464960, 137766512248225792]
        if message.author.id in authorized:
            if '!toggleGlobalBonk' in message.content:
                self.canGlobalBonk = not(self.canGlobalBonk)
                if self.canGlobalBonk:
                    await message.channel.send("Enabled Global Bonk")
                else:
                    await message.channel.send("Disabled Global Bonk")

intents = discord.Intents.default()
intents.members = True
client = MyClient(intents=intents)
client.run(TOKEN)
