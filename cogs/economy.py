import discord
from discord.ext import commands
import random
import json
import os

class Economy:
    def __init__(self, filename='economy_data.json'):
        self.filename = filename
        self.users = {}
        self.load_data()

        # Define work ranks and their income multipliers
        self.work_ranks = {
            "peasant": 1,        # Low income
            "worker": 2,         # Medium income
            "manager": 3,        # High income
            "ceo": 5,            # Super high income
            "president": 10      # Extremely high income
        }

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.users = json.load(f)

    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.users, f)

    def get_user(self, user_id):
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {'balance': 0, 'job_rank': 'peasant'}
        return self.users[str(user_id)]

    def work(self, user_id):
        user = self.get_user(user_id)
        rank = user['job_rank']
        earnings = random.randint(10, 50) * self.work_ranks[rank]
        user['balance'] += earnings
        self.save_data()  # Save data after working
        return earnings

    def send_money(self, sender_id, receiver_id, amount):
        sender = self.get_user(sender_id)
        receiver = self.get_user(receiver_id)

        if sender['balance'] >= amount:
            sender['balance'] -= amount
            receiver['balance'] += amount
            self.save_data()  # Save data after sending money
            return True
        return False

    def bank(self, user_id, amount):
        user = self.get_user(user_id)
        if user['balance'] >= amount:
            user['balance'] -= amount
            self.save_data()  # Save data after banking
            return True
        return False

    def upgrade_job(self, user_id, new_rank):
        user = self.get_user(user_id)
        if new_rank in self.work_ranks:
            if new_rank == "president" and user_id != 1234047365732896788:
                return False  # Only the admin can have the president rank
            user['job_rank'] = new_rank
            self.save_data()  # Save data after upgrading job
            return True
        return False

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.economy = Economy()

    @discord.app_commands.command(name='work', description='Work to earn coins.')
    async def work_command(self, interaction: discord.Interaction):
        earnings = self.economy.work(interaction.user.id)
        await interaction.response.send_message(f"You worked and earned {earnings} coins!")

    @discord.app_commands.command(name='send', description='Send money to another user.')
    async def send_command(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if self.economy.send_money(interaction.user.id, member.id, amount):
            await interaction.response.send_message(f"You sent {amount} coins to {member.display_name}.")
        else:
            await interaction.response.send_message("You don't have enough balance to send that amount.")

    @discord.app_commands.command(name='bank', description='Deposit money into the bank.')
    async def bank_command(self, interaction: discord.Interaction, amount: int):
        if self.economy.bank(interaction.user.id, amount):
            await interaction.response.send_message(f"You deposited {amount} coins into the bank.")
        else:
            await interaction.response.send_message("You don't have enough balance to deposit that amount.")

    @discord.app_commands.command(name='balance', description='Check your current balance.')
    async def balance_command(self, interaction: discord.Interaction):
        user = self.economy.get_user(interaction.user.id)
        balance = user['balance']
        await interaction.response.send_message(f"Your current balance is {balance} coins.")

    @discord.app_commands.command(name='upgrade', description='Upgrade to a new job rank.')
    async def upgrade_command(self, interaction: discord.Interaction, new_rank: str):
        if self.economy.upgrade_job(interaction.user.id, new_rank):
            await interaction.response.send_message(f"Your job rank has been upgraded to {new_rank}!")
        else:
            await interaction.response.send_message("You do not have enough coins to upgrade.")

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
