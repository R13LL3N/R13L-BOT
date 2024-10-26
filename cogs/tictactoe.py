from discord.ext import commands
from discord import app_commands, Interaction, User
from discord.ui import Button, View
from discord import ButtonStyle

class TicTacToeButton(Button):
    def __init__(self, x, y):
        super().__init__(style=ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: TicTacToeView = self.view
        state = view.board[self.y][self.x]

        if interaction.user not in view.players:
            await interaction.response.send_message("You're not part of this game!", ephemeral=True)
            return

        if state != 0:
            await interaction.response.send_message("This position is already taken!", ephemeral=True)
            return

        if interaction.user != view.current_player:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        if view.current_player == view.players[0]:
            self.style = ButtonStyle.danger
            self.label = '❌'
            view.board[self.y][self.x] = view.X
            view.current_player = view.players[1]
            content = f"It's {view.players[1].display_name}'s (⭕) turn"
        else:
            self.style = ButtonStyle.success
            self.label = '⭕'
            view.board[self.y][self.x] = view.O
            view.current_player = view.players[0]
            content = f"It's {view.players[0].display_name}'s (❌) turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f'{view.players[0].display_name} (❌) wins!'
            elif winner == view.O:
                content = f'{view.players[1].display_name} (⭕) wins!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

class TicTacToeView(View):
    X = -1
    O = 1
    Tie = 2

    def __init__(self, starter: User):
        super().__init__(timeout=600)  # 10 minute timeout
        self.current_player = starter
        self.players = [starter, None]
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    async def interaction_check(self, interaction: Interaction) -> bool:
        if self.players[1] is None and interaction.user != self.players[0]:
            self.players[1] = interaction.user
            self.current_player = self.players[0]  # Ensure the first player starts
            await interaction.response.send_message(f"{interaction.user.display_name} joins as ⭕!", ephemeral=True)
            await interaction.message.edit(content=f"Tic Tac Toe: {self.players[0].display_name} (❌) vs {self.players[1].display_name} (⭕)\n{self.players[0].display_name}'s (❌) turn")
            return True
        return interaction.user in self.players

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tictactoe", description="Start a game of Tic Tac Toe!")
    async def tictactoe(self, interaction: Interaction):
        await interaction.response.send_message(f'{interaction.user.display_name} is waiting for an opponent', view=TicTacToeView(interaction.user))

async def setup(bot):
    await bot.add_cog(TicTacToe(bot))
