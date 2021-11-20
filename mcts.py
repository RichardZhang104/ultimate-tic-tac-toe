import random
import nine
import numpy as np
import time


# Subclasses the Game class, so inherits:
# Attribute: self.state
# Methods: get_turn_player(state), make_play(state, play), get_plays(state), check_game_over(state)
class Mcts(nine.Game):
    def __init__(self):
        # Constructor of nine.Game sets self.state to an empty board with player 1 to play
        nine.Game.__init__(self)
        # Number of visits for each state
        self.visits = {self.state: 0}
        # Number of wins for each state
        self.value = {self.state: 0}
        # Dict of next valid states for a given state
        self.valid_states = {}
        # Dict of valid plays for a given state
        self.valid_plays = {}
        # AI thinking time
        self.simulation_time = 5

    # Get all valid next states given some state
    def fast_valid_states(self, state):
        if state in self.valid_states:
            return self.valid_states[state].copy()
        else:
            valid_states = [self.make_play(state, play) for play in self.get_plays(state)]
            self.valid_states[state] = valid_states
            return valid_states

    # Get all valid next states given some state
    def fast_valid_plays(self, state):
        if state in self.valid_plays:
            return self.valid_plays[state].copy()
        else:
            valid_plays = self.get_plays(state)
            self.valid_plays[state] = valid_plays
            return valid_plays

    # Get all valid next states given some state
    def standard_valid_states(self, state):
        return [self.make_play(state, play) for play in self.get_plays(state)]

    # Get the best play for the turn player of self.state
    def get_best_play(self):
        if self.state not in self.visits:
            self.visits[self.state] = 0
            self.value[self.state] = 0

        # Run simulations for a given amount of time
        start = time.time()
        counter = 0
        while time.time() - start <= self.simulation_time:
            counter += 1
            states_list = self.traverse()
            result = self.expand(states_list[-1])
            self.backprop(states_list, result)
        print(counter)

        # Choose the most visited child
        valid_plays = self.get_plays(self.state)
        current_best_play = None
        threshold = 0
        for play in valid_plays:
            try:
                child_visits = self.visits[self.make_play(self.state, play)]
                if child_visits >= threshold:
                    current_best_play = play
                    threshold = child_visits
            except:
                pass
        return current_best_play

    # Check if all possible states after state have been visited. Also return False if no children exist.
    def check_fully_expanded(self, valid_states):
        if valid_states == []:
            return False

        for x in valid_states:
            if x not in self.visits:
                return False

        return True

    @staticmethod
    def ucb_formula(w, n, N):
        c = 1.03125
        return (w / n) + c * ((np.log(N) / n) ** 0.5)

    # Given an array of states, pick the one with the highest UCB value. Eg. All the states have player 1 to play.
    # Then we want to (roughly) pick the one where player 1 is most likely to lose, since the choice is done
    # form the perspective of player -1.
    def ucb(self, valid_states, parent):
        N = self.visits[parent]

        best_value = -1
        best_state = None
        for state in valid_states:
            w = -1 * self.value[state]
            n = self.visits[state]
            ucb_value = self.ucb_formula(w, n, N)
            if ucb_value >= best_value:
                best_value = ucb_value
                best_state = state
        return best_state

    # Moves along tree using UCB.
    def traverse(self):
        states_list = [self.state]

        while True:
            valid_states = self.fast_valid_states(states_list[-1])
            if not self.check_fully_expanded(valid_states):
                break
            states_list.append(self.ucb(valid_states, states_list[-1]))

        # If there are no children, necessarily true that game is over
        if self.check_game_over(states_list[-1]) is not None:
            return states_list

        # If this point is reached, it is necessary that states_list[-1] has at least 1 child
        leaf_candidates = valid_states
        # We want an unvisited child
        for candidate in leaf_candidates:
            if candidate in self.visits:
                leaf_candidates.remove(candidate)

        leaf = random.choice(leaf_candidates)
        states_list.append(leaf)
        self.visits[leaf] = 0
        self.value[leaf] = 0

        return states_list

    # From given state, play random moves until the game is over (if the game is already over, no moves are required).
    # Return the result of the game.
    def expand(self, state):
        while self.check_game_over(state) is None:
            state = self.make_play(state, random.choice(self.get_plays(state)))
        return self.check_game_over(state)

    # Each of the states in states_list will already be in self.visits and self.wins.
    def backprop(self, states_list, result):
        for state in states_list:
            self.visits[state] += 1
            if self.get_turn_player(state) == result:
                self.value[state] += 1
            if self.get_turn_player(state) == -1 * result:
                self.value[state] -= 1
