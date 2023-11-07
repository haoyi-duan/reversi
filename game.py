from player import HumanPlayer, RandomPlayer, GPTPlayer, AlphaBetaPlayer
from board import Board
import datetime
from copy import deepcopy


class Game(object):
    def __init__(self, black_player, white_player) -> None:
        self.board = Board()
        self.current_player = None
        self.black_player = black_player
        self.white_player = white_player

    def run(self):
        total_time = {"X": 0, "O": 0}
        step_time = {"X": 0, "O": 0}
        winner = None
        diff = -1

        # Run the Game
        print("\n########## Game Start ##########\n")
        self.board.display(step_time=step_time, total_time=total_time)

        while True:
            self.current_player = self._switch_player()
            color = self.current_player.color
            legal_actions = list(self.board.get_legal_actions(color))

            if len(legal_actions) == 0:
                if self.game_over():
                    winner, diff = self.board.get_winner()
                    break
                else:
                    continue

            start_time = datetime.datetime.now()
            action = self.current_player.get_move(self.board)
            end_time = datetime.datetime.now()
            if action.lower() == "q":
                # Human player wants to end the game
                winner, diff = self.board.get_winner()
                break
            
            if action is None:
                continue
            else:
                es_time = (end_time - start_time).seconds
                self.board.move(action, color)
                step_time[color] = es_time
                total_time[color] += es_time
            self.board.display(step_time=step_time, total_time=total_time)

            if self.game_over():
                winner, diff = self.board.get_winner()
                break

        print("\n########## Game Over ##########\n")
        self.board.display(step_time=step_time, total_time=total_time)
        self._print_winner(winner=winner, diff=diff)
            
        return winner, diff

    def game_over(self):
        list_X = list(self.board.get_legal_actions('X'))
        list_O = list(self.board.get_legal_actions('O'))

        over = len(list_X) == 0 and len(list_O) == 0

        return over
    
    def _clear(self):
        self.board = Board()

    def _switch_player(self):
        if self.current_player == None:
            return self.black_player
        else:
            if self.current_player == self.black_player:
                return self.white_player
            else:
                return self.black_player

    def _print_winner(self, winner, diff):
        if winner == 0:
            player = self.black_player.player
            print("Player: {}".format(player))
        elif winner == 1:
            player = self.white_player.player
            print("Player: {}".format(player))
        print(["Black wins!", "White wins!", "Draw!"][winner], "Diff: {}".format(diff))

if __name__ == '__main__':
    black_player = RandomPlayer('X')
    white_player = AlphaBetaPlayer('O')
    game = Game(black_player=black_player, white_player=white_player)
    game.run()