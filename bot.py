import discord
from discord.ext import commands
import time
import json

async def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True  # Ensure this is enabled
    bot = commands.Bot(command_prefix='!', intents=intents)

    # Load cogs
    await bot.load_extension('cogs.general')

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('Starting command sync...')
        await sync_commands_if_changed(bot)
        print('Command sync process finished')

    return bot

async def sync_commands_if_changed(bot):
    print("Starting sync process...")
    try:
        start_time = time.time()
        synced = await bot.tree.sync()
        end_time = time.time()
        print(f"Sync completed in {end_time - start_time:.2f} seconds")
        print(f"Synced {len(synced)} command(s)")
        
        # Update synced_commands.json
        current_commands = [cmd.name for cmd in bot.tree.get_commands()]
        with open('synced_commands.json', 'w') as f:
            json.dump(current_commands, f)
        
        print(f"Synced commands: {', '.join(current_commands)}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print("Sync process completed")
