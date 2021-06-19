# bot.py
# Code by Rhys Sullivan & Stack Overflow
import os
import io
from discord import message
import requests
import discord
import json
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from dotenv import load_dotenv
import textwrap
from asyncio import sleep
import tinder_api
from threading import Timer
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
LIKES_STATS_CHANNEL_ID = 853125126555828246
PASSES_STATS_CHANNNEL_ID = 853125242519420929
RHYS_PROFILE_ID = 523949187663134754
CANIDATE_CHANNEL = 853106128471588874
MAID_GANG_ID = 588906458368704512
RHYS_TINDER_PROFILE_ID = "60c2db8cd821c401008981df"

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

async def sendPicture(image, ctx, compressed=True):
    with io.BytesIO() as image_binary:
        if compressed:
            image.save(image_binary, "JPEG", optimize = True, quality = 10)
            image_binary.seek(0)
            return await ctx.send(file=discord.File(fp=image_binary, filename='image.jpeg'))
        else:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            return await ctx.send(file=discord.File(fp=image_binary, filename='image.png'))

class MyClient(discord.Client):   
    canGlobalBonk = True 
    likes = 0
    passes = 0
    matches = 0
    maid_gang = None

    async def on_ready(self):
        print('Logged into:')
        for guild in self.guilds:
            if(guild.id == MAID_GANG_ID):
                self.maid_gang = guild
        #await self.updateTinderStats()
        await self.updateTinderMessages()
        #await self.send_canidate_message()
    
    def writeStat(self, key, value):
        statsDict = json.load(open("stats.json"))
        statsDict[key] = value
        json.dump(statsDict, open("stats.json", "w"))

    def getStat(self, key):
        statsDict = json.load(open("stats.json"))
        return statsDict[key] 
    
    async def updateTinderStats(self):        
        likes_stats_channel = self.get_channel(LIKES_STATS_CHANNEL_ID)
        passes_stats_channel = self.get_channel(PASSES_STATS_CHANNNEL_ID)
        await likes_stats_channel.edit(name="{0}-likes".format(self.getStat("likes")))
        await passes_stats_channel.edit(name="{0}-passes".format(self.getStat("passes")))
    
    def generateEmbedFromJSON(self, entry):
        woman_data = entry["user"]
        name = woman_data["name"]
        try:
            bio = woman_data["bio"]
        except:
            bio = "None"
        try:
            school = woman_data["schools"][0]["name"]
        except:
            school = "None"
        try:
            interest_array = woman_data["experiment_info"]["user_interests"]["selected_interests"]
            interests = ""
            for x in interest_array:
                interests += x["name"] + " "
        except:
            interests = "None"                    
        embed=discord.Embed(title=name, description=bio)
        embed.add_field(name="Interests", value=interests, inline=False)
        embed.add_field(name="School", value=school, inline=True)
        return embed


    async def send_canidate_message(self):
        # PREP DATA
        #await self.updateTinderStats()
        jsonData = tinder_api.get_suggestions()
        if jsonData["meta"]["status"] != 200:
            print("error")
            return
        
        peopleQueue = jsonData["data"]["results"]

        for entry in peopleQueue:
            if entry["type"] != "user":
                continue
            cooldownComplete = False
            woman_data = entry["user"]
            name = woman_data["name"]
            s_number = entry["s_number"]
            id = woman_data["_id"]
            profile_photos = []
            profile_photo_index = 0
            for photo in woman_data["photos"]:
                r = requests.get(photo["url"], stream=True)
                if r.status_code == 200:
                    photo = Image.open(io.BytesIO(r.content)) # Download the proflile picture directly to memory                    
                    profile_photos.append(photo)
            try:
                bio = woman_data["bio"]
            except:
                bio = "None"
            try:
                school = woman_data["schools"][0]["name"]
            except:
                school = "None"
            try:
                interest_array = woman_data["experiment_info"]["user_interests"]["selected_interests"]
                interests = ""
                for x in interest_array:
                    interests += x["name"] + " "
            except:
                interests = "None"
            canidate_channel = self.get_channel(CANIDATE_CHANNEL)
            
            embed=discord.Embed(title=name, description=bio)
            embed.add_field(name="Interests", value=interests, inline=False)
            embed.add_field(name="School", value=school, inline=True)
            embed_msg = await canidate_channel.send(embed=embed)
            
            async def sendGif():
                size = 600, 600
                
                def thumbnails(frames):
                    resized = []
                    for frame in frames:
                        thumbnail = frame.copy()
                        thumbnail.thumbnail(size, Image.BICUBIC)
                        resized.append(thumbnail)
                    return resized
                
                frames = thumbnails(profile_photos)

                # Save output            
                arr = io.BytesIO()
                (list(frames)[0]).save(arr, format='GIF', save_all=True, append_images=list(frames), duration=500, loop=0)
                arr.seek(0)
                return await canidate_channel.send(file = discord.File(arr, 'bonk.gif'))
            
            async def addPicControls(msg):
                await msg.add_reaction('⬅️')
                await msg.add_reaction('➡️')
                if cooldownComplete:
                    await msg.add_reaction('❌')
                    await msg.add_reaction('✅')
            
            async def endCooldown(msg):
                cooldownComplete = True
                addPicControls(msg)
            

            #msg = await sendGif()
            msg = await sendPicture(profile_photos[profile_photo_index], canidate_channel)
            await addPicControls(msg)
            
            voted = False
            cooldown = 0
            while not(voted):
                cooldown += .2
                if cooldown > 5:
                    if not(cooldownComplete):
                        cooldownComplete = True
                        await addPicControls(msg)

                reactions = discord.utils.get(self.cached_messages, id=msg.id).reactions
                for reaction in reactions:
                    if reaction.count < 2:
                        continue
                    emoji = str(reaction)
                    if emoji == '✅':                        
                        voted = True
                        self.writeStat("likes", self.getStat("likes")+1)
                        tinder_api.like_person(s_number, id)
                    elif emoji == '❌':                        
                        voted = True     
                        self.writeStat("passes", self.getStat("passes")+1)
                        tinder_api.pass_person(s_number, id)                            
                    elif emoji == '⬅️':                        
                        await msg.delete()
                        if not(voted):
                            profile_photo_index = (profile_photo_index - 1) % len(profile_photos)
                            msg = await sendPicture(profile_photos[profile_photo_index], canidate_channel)
                            await addPicControls(msg)
                    elif emoji == '➡️':
                        await msg.delete()
                        if not(voted):
                            profile_photo_index = (profile_photo_index + 1) % len(profile_photos)
                            msg = await sendPicture(profile_photos[profile_photo_index], canidate_channel)
                            await addPicControls(msg)
                await sleep(.2)        
            #await msg.delete()
            #await embed_msg.delete()
        
        await self.send_canidate_message()

    async def updateTinderMessages(self):
        match_data = tinder_api.getMatches()
        if match_data["meta"]["status"] != 200:
            print("error getting matches")
            return
        matches = match_data["data"]["matches"]


        for match in matches:
            try:
                json_data = tinder_api.getMessages(match["_id"])
            except:
                continue
            if json_data["meta"]["status"] != 200:
                print("error reading messages")
                return
            tinder_channel = self.get_channel(CANIDATE_CHANNEL)
            messageQueue = json_data["data"]["messages"]
            profile_data = {}        
            channel_messages = {}
            private_conversations = ["60c2db8cd821c401008981df60c435fcb92eb1010041e3dd"]        
            for tinder_message in reversed(messageQueue):
                sender = tinder_message["from"]    
                receiver = tinder_message["to"]        
                channel_name = tinder_message["match_id"]

                if channel_name in private_conversations:
                    continue

                message_channel  = discord.utils.get(self.maid_gang.channels, name=channel_name)
                if message_channel == None:
                    message_channel = await self.maid_gang.create_text_channel(channel_name, category=tinder_channel.category)
                
                madeNewChannel = False
                if not(channel_name in channel_messages):
                    madeNewChannel=True
                    channel_messages[channel_name] = await message_channel.history(limit=200).flatten()
                
                messages = channel_messages[channel_name]
                content = tinder_message["message"]
                already_sent = False
                for bubble in messages:
                    for embeded_content in bubble.embeds:
                        if content in embeded_content.description or embeded_content.description in content:
                            already_sent = True
                if already_sent:
                    continue
                girl_name = ""
                girl_url  = ""
                girl_bio  = ""
                girl_url  = ""
                if not(sender in profile_data):            
                    jsonData = tinder_api.getProfileFromID(sender)
                    if jsonData["status"] != 200:
                        print("error reading profile")
                        return
                    profileJSON = jsonData["results"]
                    girl_name = profileJSON["name"]
                    girl_url = profileJSON["photos"][0]["url"]
                    girl_bio = profileJSON["bio"]
                    profile_dict = {"name": girl_name, "url": girl_url}
                    profile_data[sender] = profile_dict
                
                name = profile_data[sender]["name"]
                url = profile_data[sender]["url"]
                
                if madeNewChannel:
                    if sender == RHYS_TINDER_PROFILE_ID:
                        girlJSON = tinder_api.getProfileFromID(receiver)                        
                        girlJSON = girlJSON["results"]
                        girl_name = girlJSON["name"]
                        girl_url = girlJSON["photos"][0]["url"]
                        girl_bio = girlJSON["bio"]
                    
                    embed =discord.Embed(title=girl_name, description=girl_bio)                                                            
                    embed_msg = await message_channel.send(embed=embed)
                    r = requests.get(girl_url, stream=True)
                    if r.status_code == 200:
                        photo = Image.open(io.BytesIO(r.content)) # Download the proflile picture directly to memory                                            
                        msg = await sendPicture(photo, message_channel)


                embed=discord.Embed(title=name, description=content)
                embed.set_thumbnail(url=url)
                await message_channel.send(embed=embed)        
        print("Up to date on messages")
        await asyncio.sleep(random.randint(60,300))    
        await self.updateTinderMessages()

    async def on_message(self, message):        
        if self.user == message.author:
            return
        if not message.guild:            
            img_url = message.content
            img_url_start = img_url.index("http")
            img_url_end = img_url.index("colorblind.png") + len("colorblind.png")
            img_url = img_url[img_url_start:img_url_end]
            r = requests.get(img_url, stream=True)
            background = Image.open(io.BytesIO(r.content)) # Download the proflile picture directly to memory                    
            background = background.convert("P", palette=Image.ADAPTIVE, colors=256)
            background.show()
            await message.channel.send('this is a dm')
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
                colorblind_font = findMatchingFontSettings(line, font_name='DejaVuSans-Bold.ttf', max_size=font_size, canvas=background)
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
        elif len(message.channel.name.split("60c2db8cd821c401008981df")) > 1:
            print(message.channel.name.split("60c2db8cd821c401008981df")[1])
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
