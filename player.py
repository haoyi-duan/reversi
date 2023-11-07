from copy import deepcopy
import random
import time
import numpy as np
import openai
openai.api_key = "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"


class BasePlayer():
    def __init__(self, color, player) -> None:
        self.color = color
        self.op_color = 'O' if color == 'X' else 'X'
        self.player = player

    def get_move(self):
        print("Please wait for a while, {}-{} is thinking...".format(self.player, self.color))


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


class GPTPlayer(BasePlayer):
    def __init__(self, color, model='gpt-4') -> None:
        assert model in ['gpt-4', 'gpt-3.5-turbo'], "GPT version unknown, choose between ['gpt-4', 'gpt-3.5-turbo']!"
        super().__init__(color, model)
        self.candidates = [i+j for i in list("ABCDEFGH") for j in list("12345678")]

    def get_move(self, board):
        super().get_move()
        legal_actions = list(board.get_legal_actions(self.color))
        colors = {'X': "black", 'O': "white"}
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
                    {"role": "user", "content": "If you are '{}': {}, Please tell me your move in terms of column (A-H) and row (1-8), like 'D3' for column D, row 3.".format(self.color, colors[self.color])}]
        while True:
            try:
                response = openai.ChatCompletion.create(
                    model=self.player,
                    messages=messages,
                ) 
                response = response["choices"][0]["message"]["content"]
                try:
                    print(response)
                    output = response.strip(" ").strip(".")
                    for coord in self.candidates:
                        if coord in output:
                            output = coord
                    assert output[0] in list("ABCDEFGH"), output[1] in list("12345678")
                except AssertionError as e:
                    assistant_message = {"role": "assistant", "content": response}
                    user_message = {"role": "user", "content": "The output format is not correct. Please try again, tell me your move in terms of column (A-H) and row (1-8), like 'D3' for column D, row 3:\n"}
                    messages.append(assistant_message)
                    messages.append(user_message)
                    print("The output format is not correct. chatGPT4, let's try again!", str(e))
                    continue
                else:
                    if output not in legal_actions:
                        assistant_message = {"role": "assistant", "content": response}
                        op_color = 'O' if self.color =='X' else 'X'
                        user_message = {"role": "user", "content": "The output action is not legal. Please try again, tell me your move in terms of column (A-H) and row (1-8), like 'D3' for column D, row 3. After the move, some of the {}: {} pieces will be flipped. For example legal actions including {}\n".format(op_color, colors[op_color], legal_actions)}
                        messages.append(assistant_message)
                        messages.append(user_message)
                        print("The output action is not legal. chatGPT4, let's try again!")
                        continue
                    else:
                        break
            except openai.APIError as e:
                #Handle API error here, e.g. retry or log
                print(f"OpenAI API returned an API Error: {e}")
                print("Wait for a second and ask chatGPT4 again!")
                time.sleep(1)
                continue

        return output

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
        

        

        