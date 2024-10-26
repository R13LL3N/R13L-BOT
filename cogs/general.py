import random
import os
import cv2
import discord
import asyncio
from discord.ext import commands
from discord import app_commands, Embed, Interaction, User
try:
    import requests
except ImportError:
    print("Requests library not found. Some features may not work.")
    requests = None
import json
from config import CREATOR_ID
from PIL import Image, ImageDraw, ImageFont
import io
import logging

# Set up logging
logging.basicConfig(filename='bot_commands.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# List of meme templates
MEME_TEMPLATES = [
    "_error", "_test", "aag", "ackbar", "afraid", "agnes", "aint-got-time", "ams", "ants", "apcr",
    "astronaut", "atis", "away", "awesome-awkward", "awesome", "awkward-awesome", "awkward", "bad",
    "badchoice", "balloon", "bd", "because", "bender", "bihw", "bilbo", "biw", "blb", "boat", "bongo",
    "both", "box", "bs", "buzz", "cake", "captain-america", "captain", "cb", "cbb", "cbg", "center",
    "ch", "chair", "cheems", "chosen", "cmm", "country", "crazypills", "crow", "cryingfloor", "db",
    "dbg", "dg", "disastergirl", "dodgson", "doge", "dragon", "drake", "drowning", "drunk", "ds",
    "dsm", "dwight", "elf", "elmo", "ermg", "exit", "fa", "facepalm", "fbf", "feelsgood", "fetch",
    "fine", "firsttry", "fmr", "friends", "fry", "fwp", "gandalf", "gb", "gears", "genie", "ggg",
    "glasses", "gone", "grave", "gru", "grumpycat", "hagrid", "happening", "harold", "headaches",
    "hipster", "home", "icanhas", "imsorry", "inigo", "interesting", "ive", "iw", "jd", "jetpack",
    "jim", "joker", "jw", "keanu", "kermit", "khaby-lame", "kk", "kombucha", "kramer", "leo", "light",
    "live", "ll", "lrv", "made", "mb", "michael-scott", "midwit", "millers", "mini-keanu", "mmm",
    "money", "mordor", "morpheus", "mouth", "mw", "nails", "nice", "noah", "noidea", "ntot", "oag",
    "officespace", "older", "oprah", "panik-kalm-panik", "patrick", "perfection", "persian",
    "philosoraptor", "pigeon", "pooh", "pool", "prop3", "ptj", "puffin", "red", "regret", "remembers",
    "reveal", "right", "rollsafe", "sad-biden", "sad-boehner", "sad-bush", "sad-clinton", "sad-obama",
    "sadfrog", "saltbae", "same", "sarcasticbear", "say", "sb", "scc", "seagull", "sf", "sk", "ski",
    "slap", "snek", "soa", "sohappy", "sohot", "soup-nazi", "sparta", "spiderman", "spirit",
    "spongebob", "ss", "stew", "stonks", "stop-it", "stop", "success", "tenguy", "toohigh", "touch",
    "tried", "trump", "ugandanknuck", "vince", "wallet", "waygd", "wddth", "whatyear", "winter",
    "wishes", "wkh", "woman-cat", "wonka", "worst", "xy", "yallgot", "yodawg", "yuno", "zero-wing"
]

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Say hello to the bot")
    async def hello(self, interaction):
        await interaction.response.send_message("Hello! I'm your friendly Discord bot.")

    @app_commands.command(name="botinfo", description="Get information about the bot")
    async def botinfo(self, interaction):
        embed = Embed(title="Bot Information", color=0x00ff00)
        embed.add_field(name="Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        
        creator_id = 1234047365732896788
        creator = await self.bot.fetch_user(creator_id)
        embed.add_field(name="Creator", value=f"{creator.name} (ID: {creator_id})", inline=True)
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text="Creator", icon_url=creator.avatar.url if creator.avatar else None)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="refresh", description="Refresh and sync bot commands")
    async def refresh(self, interaction: Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        
        try:
            synced = await self.bot.tree.sync()
            print(f"Synced {len(synced)} command(s)")
            
            current_commands = [cmd.name for cmd in self.bot.tree.get_commands()]
            with open('synced_commands.json', 'w') as f:
                json.dump(current_commands, f)
            
            await interaction.followup.send(f"Refresh complete! {len(synced)} command(s) synced.")
        except Exception as e:
            await interaction.followup.send(f"Failed to sync commands: {e}")

    @app_commands.command(name="listcommands", description="List all available commands")
    async def list_commands(self, interaction: Interaction):
        command_list = [command.name for command in self.bot.tree.get_commands()]
        await interaction.response.send_message(f"Available commands: {', '.join(command_list)}")

    @app_commands.command(name="ping", description="Test the bot's response")
    async def ping(self, interaction: Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="meme", description="Generate a meme from a template")
    async def generate_meme(self, interaction: Interaction, template: str, text1: str, text2: str = None):
        await interaction.response.defer()
        
        if template not in MEME_TEMPLATES:
            await interaction.followup.send("Invalid template. Please choose a valid template.")
            return
        
        try:
            # Prepare the meme URL with the text parameters
            meme_url = f"https://api.memegen.link/images/{template}/{text1.replace(' ', '_')}"
            if text2:
                meme_url += f"/{text2.replace(' ', '_')}"
            meme_url += ".png"
            
            embed = Embed(title="Here's your meme!", color=0x00ff00)
            embed.set_image(url=meme_url)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send("Failed to generate meme. Please try again later.")
            print(f"Error generating meme: {e}")

    @generate_meme.autocomplete('template')
    async def meme_template_autocomplete(self, interaction: Interaction, current: str):
        suggestions = [template for template in MEME_TEMPLATES if current.lower() in template.lower()]
        return [app_commands.Choice(name=template, value=template) for template in suggestions]

    @app_commands.command(name="badapple", description="Play Bad Apple as ASCII art")
    async def bad_apple(self, interaction: Interaction):
        await interaction.response.defer()
        await interaction.followup.send("Starting Bad Apple playback...")

        video_path = 'bad_apple.mp4'
        if not os.path.exists(video_path):
            await interaction.followup.send(f"Error: {video_path} not found.")
            return

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            await interaction.followup.send("Error: Could not open video file.")
            return

        ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']
        message = None

        def resize_image(image, new_width=50):
            height, width = image.shape
            ratio = height / width
            new_height = int(new_width * ratio * 0.5)
            resized_image = cv2.resize(image, (new_width, new_height))
            return resized_image

        def pixels_to_ascii(image):
            pixels = image.flatten()
            return ''.join([ASCII_CHARS[pixel // 25] for pixel in pixels])

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % 4 != 0:  # Process every 4th frame
                continue

            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            resized_image = resize_image(gray_image)
            ascii_frame = pixels_to_ascii(resized_image)
            
            frame_width = resized_image.shape[1]
            ascii_image = "\n".join([ascii_frame[index:index + frame_width] for index in range(0, len(ascii_frame), frame_width)])
            
            content = f"```\n{ascii_image}\n```"

            try:
                if message:
                    await message.edit(content=content)
                else:
                    message = await interaction.followup.send(content)
            except discord.errors.HTTPException as e:
                if e.code == 50035:  # Invalid Form Body error
                    # If the message is too long, send a new message
                    message = await interaction.followup.send(content)
                else:
                    print(f"Error processing frame {frame_count}: {str(e)}")

            await asyncio.sleep(0.1)  # Adjust this value to control playback speed

        cap.release()
        await interaction.followup.send("Bad Apple playback completed!")

    @app_commands.command(name="rip", description="Generate a RIP photo from a mentioned user's avatar")
    async def rip(self, interaction: Interaction, user: User = None):
        await interaction.response.defer()
        
        # Use the mentioned user if provided, otherwise use the command invoker's avatar
        if user is None:
            user = interaction.user
        
        # Check if the user has an avatar
        if user.avatar:
            avatar_url = user.avatar.url
            api_url = f"https://agg-api.vercel.app/rip?avatar={avatar_url}"
            try:
                response = requests.get(api_url)
                
                if response.status_code == 200:
                    await interaction.followup.send(response.url)  # Send the generated RIP image
                else:
                    await interaction.followup.send("Failed to generate RIP image. Please try again.")
            except Exception as e:
                await interaction.followup.send(f"An error occurred: {str(e)}")
        else:
            await interaction.followup.send("The mentioned user does not have an avatar.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        # Remove or comment out the image processing code here

    @app_commands.command(name="example_command", description="An example command.")
    async def example_command(self, interaction: Interaction):
        await interaction.response.send_message("This is an example command.")
        logging.info(f"Command 'example_command' used by {interaction.user.name} (ID: {interaction.user.id})")

    @app_commands.command(name="textoverlay", description="Add text overlay to an image")
    async def textoverlay(
        self, 
        interaction: Interaction, 
        text: str,
        image: discord.Attachment
    ):
        await interaction.response.defer()

        try:
            response = await image.read()
            image_data = io.BytesIO(response)
            img = Image.open(image_data)
            
            # Configure text
            font_size = 48  # Start with a larger font size
            font = ImageFont.truetype("arial.ttf", font_size)
            max_width = img.width - 40
            border_height = int(img.height * 0.3)  # Increase text area to 30% of image height

            lines = []
            words = text.split()
            current_line = words[0]

            for word in words[1:]:
                test_line = current_line + " " + word
                bbox = font.getbbox(test_line)
                if bbox[2] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word

            lines.append(current_line)
            
            # Calculate text box size
            line_height = font.getbbox("Tg")[3] + 10  # Increase line spacing
            text_height = len(lines) * line_height
            
            # Adjust font size if text doesn't fit
            while text_height > border_height:
                font_size -= 2
                if font_size < 24:  # Set a minimum font size
                    border_height = text_height + 20  # Increase border height if text is too long
                    break
                font = ImageFont.truetype("arial.ttf", font_size)
                line_height = font.getbbox("Tg")[3] + 10
                text_height = len(lines) * line_height

            # Create a new image with space for the text box
            new_img = Image.new('RGB', (img.width, img.height + border_height), color='white')
            new_img.paste(img, (0, border_height))
            
            # Draw border
            draw = ImageDraw.Draw(new_img)
            draw.rectangle([0, 0, img.width, border_height], outline='black', width=2)
            
            # Draw text
            y_text = (border_height - text_height) // 2
            for line in lines:
                bbox = font.getbbox(line)
                x_text = (img.width - bbox[2]) // 2
                draw.text((x_text, y_text), line, font=font, fill='black')
                y_text += line_height
            
            # Save and send
            output = io.BytesIO()
            new_img.save(output, format='PNG')
            output.seek(0)
            
            await interaction.followup.send(
                file=discord.File(output, filename='overlay_image.png')
            )

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(General(bot))

