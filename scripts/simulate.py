import random
from time import perf_counter
from chessbot.game import Game

def run_game():
    game = Game()
    rng = random.Random(42)
    move_limit = 300
    moves_played = 0
    thinking_time = {"White":0.0, "Black":0.0}

    while game.outcome() is None and moves_played < move_limit:
        side = game.turn()
        board = game.board_copy()
        start = perf_counter()
        move = rng.choice(list(board.legal_moves))
        thinking_time[side] += perf_counter() - start
        game.apply_move(move.uci())
        moves_played += 1
    outcome = game.outcome()

    if outcome is None:
        print("Result unfinished - move limit reached")
    else:
        print("Result:", outcome["winner"])
        print("Reason:", outcome["termination"])
    
    print("Individual moves played:", moves_played)
    print("White thinking time:", round(thinking_time["White"], 6), "seconds")
    print("Black thinking time:", round(thinking_time["Black"], 6), "seconds")


if __name__ == "__main__":
    run_game()