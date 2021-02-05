# bot.py
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
    async def on_ready(self):
        print('Logged into:')
        for guild in self.guilds:
            print(guild.name)


    async def on_message(self, message):
        if self.user == message.author:
            return
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
                    response = "{0} has been bonked {1} times".format(user.display_name, numBonks)
                    await message.channel.send(response)
                else:
                    response = "{0} has not been bonked yet".format(user.display_name)
                    await message.channel.send(response)
        return


        if '!bonk' in message.content:
            for user in message.mentions:
                r = requests.get(user.avatar_url, stream=True)
                if r.status_code == 200:
                    background = Image.open(io.BytesIO(r.content)) # Download the profile picture directly to memory                    
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
                        usersDict[str(user.id)] = usersDict[str(user.id)] + 1
                    else:
                        usersDict[str(user.id)] = 1
                    json.dump(usersDict, open("dictionary.txt", "w"))



client = MyClient()
client.run(TOKEN)
