# bot.py
import os
import io
import requests
import discord
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')



class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged into:')
        for guild in self.guilds:
            print(guild.name)
    async def on_message(self, message):
        if self.user == message.author:
            return
            
        if '!bonk' in message.content:             
            for user in message.mentions:
                r = requests.get(user.avatar_url, stream=True)
                if r.status_code == 200:
                    background = Image.open(io.BytesIO(r.content)) # Download the profile picture directly to memory                    
                    #background.save(os.path.join('profile.png'), quality=85) # CODE TO SAVE THE FILE                    
                    print(user.avatar_url)                    
                    gif = Image.open('Media/TransparentBonkGif.gif')                                        
                    background = background.convert("RGBA")
                    background = background.resize((513,513))
                    images = []
                    for frame in range(0, gif.n_frames):
                        gif.seek(frame)
                        images.append(Image.alpha_composite(background, gif.convert("RGBA")))                        
                    

                    images[0].save('bonk.gif', save_all=True, append_images=images[1:], optimize=False, duration=100, loop=0)
                    await message.channel.send(file=discord.File('bonk.gif'))
client = MyClient()
client.run(TOKEN)