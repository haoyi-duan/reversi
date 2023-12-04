import random
import sys
import os
from game import Game
from player import *

def match(black_player, white_player, num_simulations=1):
    winners = []
    diffs = []
    sys.stdout = open(os.devnull, 'w')
    for _ in range(num_simulations):
        game = Game(black_player=black_player, white_player=white_player)
        winner, diff = game.run()
        winners.append(winner)
        diffs.append(diff)
    sys.stdout = sys.__stdout__
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
        'GPT-4': GPTPlayer,
        'MCTS': MCTSPlayer,
    }
    for player1 in players:
        for player2 in players:
            if player1 == player2:
                continue
            black_player = players[player1]('X')
            white_player = players[player2]('O')
            winners, diffs = match(black_player, white_player, 3)
            result = calc(player1, player2, winners, diffs)
            print("{},{},{:.2f},{:.2f}".format(
                player1, player2, result[0], result[1]))