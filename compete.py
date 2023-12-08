import random
import sys
import os
from game import Game
from player import *

def match(player1, player2, num_simulations=1):
    black_player = players[player1]('X')
    white_player = players[player2]('O')
    winners = []
    diffs = []
    sys.stdout = open(os.devnull, 'w')
    logfile = open(f'{player1}_{player2}.txt', 'w')
    for _ in range(num_simulations):
        game = Game(black_player=black_player, white_player=white_player)
        winner, diff = game.run()
        logfile.write(f'{winner},{diff}\n')
        winners.append(winner)
        diffs.append(diff)
    sys.stdout = sys.__stdout__
    logfile.close()
    return winners, diffs

def calc(player1, player2, winners, diffs):
    # compute the winning rate of player1
    total = len(winners)
    player1_win = 0
    player1_gain = 0
    for winner, diff in zip(winners, diffs):
        if winner == 0:
            player1_win += 1
            player1_gain += diff
        elif winner == 1:
            player1_gain -= diff
    win_rate = 100.0 * player1_win / total
    avg_gain = player1_gain / total
    return win_rate, avg_gain

if __name__ == '__main__':
    random.seed(0)
    players = {
        'Random': RandomPlayer,
        'AlphaBeta' : AlphaBetaPlayer,
        # 'GPT-4': GPTPlayer,
        'MCTS': MonteCarloPlayer,
    }
    for player1 in players:
        for player2 in players:
            if player1 == player2:
                continue
            winners, diffs = match(player1, player2, 3)
            result = calc(player1, player2, winners, diffs)
            print("{},{},{:.2f},{:.2f}".format(
                player1, player2, result[0], result[1]))