import csv
import random
from pathlib import Path
from time import perf_counter
from chessbot.game import Game

def run_game(seed,move_limit = 300):
    game = Game()
    rng = random.Random(seed)
    moves_played = 0
    thinking_time = {"White":0.0,"Black":0.0}
    while game.outcome() is None and moves_played < move_limit:
        side = game.turn()
        board = game.board_copy()
        start = perf_counter()
        move = rng.choice(list(board.legal_moves))
        thinking_time[side] += perf_counter() - start
        game.apply_move(move.uci())
        moves_played += 1

    outcome = game.outcome()

    return{
        "seed":seed,
        "white_player": "random",
        "black_player": "random",
        "result": outcome["winner"] if outcome else "Unfinished",
        "reason": outcome["termination"] if outcome else "MOVE_LIMIT",
        "individual_moves": moves_played,
        "white_seconds": thinking_time["White"],
        "black_seconds": thinking_time["Black"],
        "final_fen": game.snapshot()["fen"],
    }

def main():
    results = []
    for game_number in range (1,11):
        result = run_game(seed = game_number)
        results.append({"game":game_number, **result})
        print(
            f"Game {game_number}: {result['result']} "
            f"after {result['individual_moves']} individual moves"
        )
    project_root = Path(__file__).resolve().parents[1]
    results_folder = project_root / "tests" / "simulations"
    results_folder.mkdir(parents = True, exist_ok = True)
    output_file = results_folder/"random_results.csv"

    with output_file.open("w",newline = "",encoding = "utf-8") as file:
        writer = csv.DictWriter(file,fieldnames= list(results[0]))
        writer.writeheader()
        writer.writerows(results)

    print("\nSummary")
    for outcome in ("White","Black","Draw","Unfinished"):
        count = sum(row["result"] == outcome for row in results)
        print(f"{outcome}:{count}")
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()