from game import *
from player import *
from board import Board
import datetime
from copy import deepcopy

black_player = AlphaBetaPlayer('X')
white_player = MonteCarloPlayer('O',num_simulation=400)
black_win=0
white_win=0
draw=0
total_time = {"X": 0, "O": 0}
move_cnt={"X": 0, "O": 0}
for i in range(0,3):
    game = Game(black_player=black_player, white_player=white_player)
    game.run()
    total_time["X"]+=game.total_time["X"]
    move_cnt["X"]+=game.move_cnt["X"]
    total_time["O"]+=game.total_time["O"]
    move_cnt["O"]+=game.move_cnt["O"]
    if game.board.get_winner()[0]==0:
        black_win+=1
    elif game.board.get_winner()[0]==1:
        white_win+=1
    else:
        draw+=1
print(f"black win:{black_win}")
print(f"white win{white_win}")
print(f"draw{draw}")
bt=total_time["X"]/move_cnt["X"]
wt=total_time["O"]/move_cnt["O"]
print(f"black_avg_move_time{bt}s")
print(f"white_avg_move_time{wt}s")