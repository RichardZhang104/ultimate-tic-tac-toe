import discord
import numpy as np
import mcts


class MyClient(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)
        self.game = mcts.Mcts()

    @staticmethod
    async def on_ready():
        print('Bot is ready')

    # Convert current board state into emojis formatted correctly for discord
    @staticmethod
    def emoji(state):
        # Convert state information
        full_board = np.asarray(state[0]).reshape((3, 3, 3, 3))
        overall_board = np.asarray(state[1]).reshape(3, 3)
        if state[2] != -1:
            restriction = (int(np.floor(state[2] / 3)), state[2] % 3)
        else:
            restriction = (-1, -1)

        # Each element of discord_message will be a separate line of a discord message
        discord_message = ['' for i in range(9)]

        # Colour won sub boards
        for index, cell in np.ndenumerate(overall_board):
            if cell == 1:
                full_board[index] = 2 * np.ones((3, 3))
            elif cell == -1:
                full_board[index] = -2 * np.ones((3, 3))

        if restriction != (-1, -1):
            for index, cell in np.ndenumerate(full_board[restriction]):
                if cell == 0:
                    full_board[restriction + index] = 10

        for i in range(9):
            # Slice relevant row in the board
            relevant_row = full_board[int(np.floor(i / 3)), :, int(i % 3), :]
            relevant_row = relevant_row.flatten()

            for j, element in enumerate(relevant_row):
                if j % 3 == 0 and j != 0:
                    discord_message[i] += '      '
                if element == 1:
                    discord_message[i] += ':blue_square:'
                elif element == -1:
                    discord_message[i] += ':red_square:'
                elif element == 2:
                    discord_message[i] += ':blue_circle:'
                elif element == -2:
                    discord_message[i] += ':red_circle:'
                elif element == 10:
                    discord_message[i] += ':yellow_square:'
                else:
                    discord_message[i] += ':white_large_square:'

        combined_message = ''

        for i in range(9):
            if i % 3 == 0 and i != 0:
                combined_message += '\n'
            combined_message += discord_message[i] + '\n'
        return combined_message

    # User inputs 1 to 9, returns corresponding index (row, column) for the board
    @staticmethod
    def get_index(user_input):
        input_dict = {7: 0, 8: 1, 9: 2, 4: 3, 5: 4, 6: 5, 1: 6, 2: 7, 3: 8}
        return input_dict[int(user_input)]

    async def reset(self, message):
        self.game = mcts.Mcts()
        await message.channel.send('Game has been reset.')

    async def ai_turn(self, message):
        play = self.game.get_best_play()
        await message.channel.send(
            'AI simulations: ' + str(self.game.visits[self.game.state]) + '\nAI evaluation before: ' + str(
                self.game.value[self.game.state] / self.game.visits[self.game.state]))

        self.game.state = self.game.make_play(self.game.state, play)

        await message.channel.send(
            'AI evaluation after: ' + str(self.game.value[self.game.state] / self.game.visits[self.game.state]))

        await message.channel.send('AI plays:\n' + self.emoji(self.game.state))

    async def game_over(self, message):
        if self.game.check_game_over(self.game.state) is not None:
            await message.channel.send('Player ' + str(self.game.check_game_over(self.game.state)) + ' wins!')
            await self.reset(message)

    async def on_message(self, message):
        # ensure bot does not reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('.'):
            # Message body
            body = message.content[1:]

            if body == 'reset':
                await self.reset(message)
            else:
                # Human turn
                board_select = self.get_index(body[0])
                cell_select = self.get_index(body[1])
                play = (board_select,) + (cell_select,)

                if play not in self.game.get_plays(self.game.state):
                    await message.channel.send('Invalid play, please try again.')
                    return

                self.game.state = self.game.make_play(self.game.state, play)
                await message.channel.send('You played:\n' + self.emoji(self.game.state))

                if self.game.check_game_over(self.game.state) is not None:
                    await self.game_over(message)
                else:
                    await self.ai_turn(message)
                    await self.game_over(message)


with open('token.txt') as f:
    token = f.read()

client = MyClient()
client.run(token)
