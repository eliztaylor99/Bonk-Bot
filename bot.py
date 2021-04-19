# bot.py
# Code by Rhys Sullivan & Stack Overflow
import os
import io
import requests
import discord
import json
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from dotenv import load_dotenv
import textwrap

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

def findMatchingFontSettings(text, canvas, max_size=50, img_fraction=0.90, font_name="arial.ttf", ):
    fontsize = max_size  # starting font size    
    font = ImageFont.truetype(font_name, fontsize)
    while font.getsize(text)[0] > img_fraction*canvas.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize -= 1
        font = ImageFont.truetype(font_name, fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1
    if fontsize > max_size:
        fontsize = max_size
    return ImageFont.truetype(font_name, fontsize)

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
            await message.channel.send("0.2.5")
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
            members = message.mentions
            if ('@everyone' in message.content) or ('@global-bonk' in message.content) and self.canGlobalBonk:                                
                members = await message.guild.fetch_members(limit=None).flatten()            
            for user in members:
                r = requests.get(user.avatar_url, stream=True)
                if r.status_code == 200:
                    background = Image.open(io.BytesIO(r.content)) # Download the proflile picture directly to memory                    
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
                    images[0].info.pop('background', None)
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
        elif '!colorblind' in message.content:
            await message.delete()
            # Setup
            colorblind_message = message.content[message.content.index('!colorblind')+len('!colorblind')+1:]            
            colorblind_message = colorblind_message.replace('|','')
            background = Image.open('Media/colorblind_background.png')
            background = background.convert("RGBA")               
            x_margin = random.randint(20,40)
            y_margin = random.randint(20,50)
            lines = textwrap.wrap(colorblind_message, 12)
            offset = 0
            font_size = random.randint(40,50)
            rotation_amount = random.randint(-30, 30)
            if abs(rotation_amount) > 10:
                font_size = random.randint(20,25)
                font_size = 25
                offset = 30
            if len(lines) < 4:                
                offset = random.randint(60,80)
            # Add Text
            for line in lines:
                draw = ImageDraw.Draw(background)         
                colorblind_font = findMatchingFontSettings(line, font_name='arialbd.ttf', max_size=font_size, canvas=background)
                textwidth, textheight = draw.textsize(line, font=colorblind_font)
                if offset == 0:
                    offset = textheight
                x = 300-textwidth-x_margin
                y = textheight+offset
                draw.text((x, y), line, font=colorblind_font, fill="#69FC4B")
                offset += textheight

            # Apply post process            
            background = background.rotate(rotation_amount)
            new_background = Image.open('Media/colorblind_background.png')
            background = Image.alpha_composite(new_background.convert("RGBA"), background)                    
            background = background.convert("RGB")
            background = background.filter(ImageFilter.BLUR)                        

            # Send to discord
            arr = io.BytesIO()
            background.save(arr, format='png', save_all=True)
            arr.seek(0)
            await message.channel.send(file = discord.File(arr, 'colorblind.png'))
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
