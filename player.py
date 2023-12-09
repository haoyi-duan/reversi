from copy import deepcopy
from collections import defaultdict
import random
import time
import numpy as np
import openai
import os
from collections import defaultdict


class BasePlayer():
    def __init__(self, color, player) -> None:
        self.color = color
        self.op_color = 'O' if color == 'X' else 'X'
        self.player = player

    def get_move(self):
        #print("Please wait for a while, {}-{} is thinking...".format(self.player, self.color))
        pass


class HumanPlayer(BasePlayer):
    def __init__(self, color) -> None:
        super().__init__(color, "human")

    def get_move(self, board):
        super().get_move()
        candidates = list(board.get_legal_actions(self.color))
        if len(candidates) == 0:
            return None
        
        action = input("Please enter the coordinate: ")
        action = action.strip(" ").upper()
        
        while action not in candidates:
            if action == 'Q':
                return action
            action = input("Legal actions include {}, please enter the coordinate again: ".format(candidates))
            action = action.strip(" ").upper()
        return action
    

class RandomPlayer(BasePlayer):
    def __init__(self, color) -> None:
        super().__init__(color, "random")

    def get_move(self, board):
        super().get_move()
        virtual_board = deepcopy(board)
        action = self.next_action(virtual_board, self.color)

        return action
    
    def next_action(self, board, color):
        candidates = list(board.get_legal_actions(color))
        if len(candidates) == 0:
            return None
        else:
            return random.choice(candidates)


class GPTPlayer_old(BasePlayer):
    def __init__(self, color, model='gpt-4') -> None:
        assert model in ['gpt-4', 'gpt-3.5-turbo'], "GPT version unknown, choose between ['gpt-4', 'gpt-3.5-turbo']!"
        super().__init__(color, model)
        self.candidates = [i+j for i in list("ABCDEFGH") for j in list("12345678")]

    def get_move(self, board):
        super().get_move()
        legal_actions = list(board.get_legal_actions(self.color))
        colors = {'X': "black", 'O': "white"}
        legal_message = ', '.join(legal_actions)
        content = f"Your color is '{self.color}': {colors[self.color]}. Please make your move by specifying a column (A-H) and a row (1-8), like 'D3' for column D, row 3.Your response should be only two letters. Your actions must be chosen from the following: "+legal_message+"."
        messages = [{"role": "system", "content": "You are reversi chess game player. Now you are going to play reversi with me. Black pieces are denoted as 'X', white pieces are denoted as 'O', you can place your move at '.'. Assume current board is:\n" + \
                    " " + " ".join(list("ABCDEFGH")) + "\n" + \
                    str(1) + ' ' + ' '.join(board[0]) + "\n" + \
                    str(2) + ' ' + ' '.join(board[1]) + "\n" + \
                    str(3) + ' ' + ' '.join(board[2]) + "\n" + \
                    str(4) + ' ' + ' '.join(board[3]) + "\n" + \
                    str(5) + ' ' + ' '.join(board[4]) + "\n" + \
                    str(6) + ' ' + ' '.join(board[5]) + "\n" + \
                    str(7) + ' ' + ' '.join(board[6]) + "\n" + \
                    str(8) + ' ' + ' '.join(board[7])}, \
                    {"role": "user", "content": content}]
        while True:
            try:
                response = openai.ChatCompletion.create(
                    model=self.player,
                    messages=messages,
                    temperature=1
                ) 
                response = response["choices"][0]["message"]["content"]
                if response not in legal_actions:
                    continue
                else:
                    break
            except openai.APIError as e:
                #Handle API error here, e.g. retry or log
                print(f"OpenAI API returned an API Error: {e}")
                print("Wait for a second and ask chatGPT4 again!")
                time.sleep(1)
                continue

        return response

class GPTPlayer(BasePlayer):
    def __init__(self, color, model='gpt-4') -> None:
        assert model in ['gpt-4', 'gpt-3.5-turbo'], "GPT version unknown, choose between ['gpt-4', 'gpt-3.5-turbo']!"
        super().__init__(color, model)
        self.candidates = [i+j for i in list("ABCDEFGH") for j in list("12345678")]

    def get_move(self, board):
        super().get_move()
        legal_actions = list(board.get_legal_actions(self.color))
        colors = {'X': "black", 'O': "white"}
        legal_message = ', '.join(legal_actions)
        content = f"Your color is '{self.color}': {colors[self.color]}. Please make your move by specifying a column (A-H) and a row (1-8), like 'D3' for column D, row 3.Your response should be only two letters. Your actions must be chosen from the following: "+legal_message+"."
        messages = [{"role": "system", "content": "You are reversi chess game player. Now you are going to play reversi with me. Black pieces are denoted as 'X', white pieces are denoted as 'O', you can place your move at '.'. Assume current board is:\n" + \
                    " " + " ".join(list("ABCDEFGH")) + "\n" + \
                    str(1) + ' ' + ' '.join(board[0]) + "\n" + \
                    str(2) + ' ' + ' '.join(board[1]) + "\n" + \
                    str(3) + ' ' + ' '.join(board[2]) + "\n" + \
                    str(4) + ' ' + ' '.join(board[3]) + "\n" + \
                    str(5) + ' ' + ' '.join(board[4]) + "\n" + \
                    str(6) + ' ' + ' '.join(board[5]) + "\n" + \
                    str(7) + ' ' + ' '.join(board[6]) + "\n" + \
                    str(8) + ' ' + ' '.join(board[7])}, \
                    {"role": "user", "content": content}]
        while True:
            try:
                response = openai.ChatCompletion.create(
                    model=self.player,
                    messages=messages,
                    temperature=1
                ) 
                response = response["choices"][0]["message"]["content"]
                if response not in legal_actions:
                    continue
                else:
                    break
            except openai.APIError as e:
                #Handle API error here, e.g. retry or log
                print(f"OpenAI API returned an API Error: {e}")
                print("Wait for a second and ask chatGPT4 again!")
                time.sleep(1)
                continue

        return response

class AlphaBetaPlayer(BasePlayer):
    def __init__(self, color) -> None:
        super().__init__(color, "alpha-beta")
        self.weight = [ [70, -20, 20, 20, 20, 20, -15, 70], 
	                    [-20, -30, 5, 5, 5, 5, -30, -15], 
	                    [20, 5, 1, 1, 1, 1, 5, 20],
	                    [20, 5, 1, 1, 1, 1, 5, 20],
	                    [20, 5, 1, 1, 1, 1, 5, 20],
                        [20, 5, 1, 1, 1, 1, 5, 20],
	                    [-20, -30, 5, 5, 5, 5, -30, -15],
	                    [70, -15, 20, 20, 20, 20, -15, 70] ]
        self.deepth = 0

        self.maxdeepth = 6
        self.emptylistFlag = 10000000

    def calculate(self, board):
        count = 0
        for i in range(8):
            for j in range(8):
                if board[i][j] == self.color:
                    count += self.weight[i][j]
                elif board[i][j] == self.op_color:
                    count -= self.weight[i][j]
        return count

    def alphaBeta(self, board, color, a, b):
        if self.deepth > self.maxdeepth:
            return None, self.calculate(board)
        colorNext = 'O' if color == 'X' else 'X'
        legal_actions = list(board.get_legal_actions(color))
        
        if len(legal_actions) == 0:
            if len(list(board.get_legal_actions(colorNext))) == 0:
                return None, self.calculate(board)
            return self.alphaBeta(board, colorNext, a, b)

        max = -np.inf
        min = np.inf  
        action = None

        for p in legal_actions:
            reversed = board.move(p, color)
            self.deepth += 1
            p1, current = self.alphaBeta(board, colorNext, a, b)
            self.deepth -= 1
            board.backpropagation(p, reversed, color)

            # alpha-beta pruning
            if color == self.color:
                if current > a:
                    if current > b:
                        return p, current
                    a = current
                if current > max:
                    max = current
                    action = p
            
            else:
                if current < b:
                    if current < a:
                        return p, current
                    b = current
                if current < min:
                    min = current
                    action = p

        if color == self.color:
            return action, max
        else:
            return action, min

    def get_move(self, board):
        super().get_move()
        virtual_board = deepcopy(board)
        action, weight = self.alphaBeta(virtual_board, self.color, -np.inf, np.inf)

        return action
        
class MonteCarloPlayer(BasePlayer):
    def __init__(self, color, num_simulation=100, C=1.41) -> None:
        super().__init__(color, "MonteCarlo")
        self.num_simulation = num_simulation
        self.C=C
    
    def uct_value(self, action, action_plays, action_wins):
        total_plays=sum(action_plays.values())
        if action_plays[action]==0:
            return float("inf")
        win_rate=action_wins[action]/action_plays[action]
        return win_rate+self.C*np.sqrt(np.log(total_plays)/action_plays[action])
    
    def get_move(self, board):
        super().get_move()
        legal_actions=list(board.get_legal_actions(self.color))
        if not legal_actions:
            return None
        else:
            action_wins=defaultdict(int)
            action_plays=defaultdict(int)
            for _ in range(self.num_simulation):
                # choose an action
                best_action=max(legal_actions,key=lambda a:self.uct_value(a,action_plays,action_wins))
                #for action in legal_actions:
                virtual_board=deepcopy(board)
                win=self.simulate(virtual_board,best_action)
                action_wins[best_action]+=win
                action_plays[best_action]+=1
            return max(legal_actions, key=lambda a: action_wins[a] / action_plays[a] if action_plays[a] > 0 else 0)
    
    def simulate(self, board, action):
        current_color=self.color
        board.move(action,current_color)
        while True:
            current_color="O" if current_color=="X" else "X"
            legal_actions=list(board.get_legal_actions(current_color))
            if len(legal_actions) == 0:
                list_X = list(board.get_legal_actions('X'))
                list_O = list(board.get_legal_actions('O'))
                if len(list_X) == 0 and len(list_O) == 0:
                    winner, diff = board.get_winner()
                    return 1 if winner==(0 if self.color=="X" else 1) else 0
            else:
                board.move(random.choice(legal_actions),current_color)
        

        
