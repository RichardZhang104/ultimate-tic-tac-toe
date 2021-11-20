class Game:
    def __init__(self):
        # (full board, overall board, restriction, turn player)
        self.state = (((0,) * 9,) * 9, (0,) * 9, -1, 1)

    @staticmethod
    def get_turn_player(state):
        return state[3]

    # Check for win on a 3x3 board for given player
    @staticmethod
    def check_sub_win(board, player):
        win = (player, player, player)

        r1 = board[:3]
        r2 = board[3:6]
        r3 = board[6:]

        c1 = (board[0], board[3], board[6])
        c2 = (board[1], board[4], board[7])
        c3 = (board[2], board[5], board[8])

        d1 = (board[0], board[4], board[8])
        d2 = (board[2], board[4], board[6])

        if r1 == win or r2 == win or r3 == win or c1 == win or c2 == win or c3 == win or d1 == win or d2 == win:
            return True
        return False

    # Play is of the form (board_select, cell_select)
    def make_play(self, state, play):
        full_board = state[0]
        overall_board = state[1]

        # Make the play on the full board (no checking if valid)
        full_board = full_board[:play[0]] + (
            full_board[play[0]][:play[1]] + (state[3],) + full_board[play[0]][play[1] + 1:],) + full_board[play[0] + 1:]

        # Check for a win on the sub board, for the player that just played
        if self.check_sub_win(full_board[play[0]], state[3]):
            overall_board = overall_board[:play[0]] + (state[3],) + overall_board[play[0] + 1:]

        if 0 not in full_board[play[1]] or overall_board[play[1]] != 0:
            restriction = -1
        else:
            restriction = play[1]

        return full_board, overall_board, restriction, -1 * state[3]

    @staticmethod
    def get_plays(state):
        full_board = state[0]
        overall_board = state[1]
        restriction = state[2]

        plays = []

        # If no restriction, can play in any cell of a non-won board
        if restriction == -1:
            for i, board in enumerate(full_board):
                if overall_board[i] == 0:
                    for j, cell in enumerate(board):
                        if cell == 0:
                            plays.append((i, j))
        else:
            for i, cell in enumerate(full_board[restriction]):
                if cell == 0:
                    plays.append((restriction, i))

        return plays

    # Either return winning player (1 or -1), 0 for draw, or None for game still ongoing.
    def check_game_over(self, state):
        full_board = state[0]
        overall_board = state[1]

        # Say turn player is player -1 in the state. Then player 1 just played so only need to check win for player 1.
        if self.check_sub_win(overall_board, -1 * state[3]):
            return -1 * state[3]

        # Sub boards that can still be played in must be 0 in overall board
        for i, board in enumerate(overall_board):
            if board == 0:
                # If there is at least one cell that is 0
                if 0 in full_board[i]:
                    return None

        return 0
