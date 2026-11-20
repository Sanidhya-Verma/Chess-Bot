import csv
import random
from pathlib import Path
from time import perf_counter

from chessbot.game import Game
from chessbot.minimax import minimax_engine


DEPTH = 4
GAMES = 2
MOVE_LIMIT = 300


def run_game(seed):
    game = Game()
    rng = random.Random(seed)
    minimax_colour = "White" if seed % 2 else "Black"

    players = {
        "White": "minimax" if minimax_colour == "White" else "random",
        "Black": "minimax" if minimax_colour == "Black" else "random",
    }
    thinking_time = {"White": 0.0, "Black": 0.0}
    move_counts = {"White": 0, "Black": 0}
    moves_played = 0

    while game.outcome() is None and moves_played < MOVE_LIMIT:
        side = game.turn()
        board = game.board_copy()

        start = perf_counter()
        if players[side] == "minimax":
            move = minimax_engine(DEPTH, board)
        else:
            move = rng.choice(list(board.legal_moves))

        elapsed = perf_counter() - start
        thinking_time[side] += elapsed

        if move is None or move not in board.legal_moves:
            raise RuntimeError(f"{players[side]} returned an invalid move")

        game.apply_move(move.uci())
        moves_played += 1
        move_counts[side] += 1

        print(
            f"Move {moves_played}: {side} ({players[side]}) "
            f"played {move.uci()} in {elapsed:.2f}s",
            flush=True,
        )

    outcome = game.outcome()
    result = outcome["winner"] if outcome else "Unfinished"
    winner = players[result] if result in players else result

    return {
        "seed": seed,
        "white_player": players["White"],
        "black_player": players["Black"],
        "result": result,
        "winner": winner,
        "reason": outcome["termination"] if outcome else "MOVE_LIMIT",
        "individual_moves": moves_played,
        "move_limit": MOVE_LIMIT,
        "white_moves": move_counts["White"],
        "black_moves": move_counts["Black"],
        "white_seconds": thinking_time["White"],
        "black_seconds": thinking_time["Black"],
        "minimax_depth": DEPTH,
        "final_fen": game.snapshot()["fen"],
        "claim_draw": False,
    }


def main():
    project_root = Path(__file__).resolve().parents[1]
    results_folder = project_root / "tests" / "simulations"
    results_folder.mkdir(parents=True, exist_ok=True)
    output_file = results_folder / f"minimax_vs_random_depth{DEPTH}.csv"
    results = []

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = None

        for game_number in range(1, GAMES + 1):
            print(f"\nStarting game {game_number}/{GAMES}...", flush=True)
            result = run_game(seed=game_number)
            row = {"game": game_number, **result}

            if writer is None:
                writer = csv.DictWriter(file, fieldnames=list(row))
                writer.writeheader()

            writer.writerow(row)
            file.flush()
            results.append(row)

            print(
                f"Winner: {result['winner']} | "
                f"Reason: {result['reason']} | "
                f"Individual moves: {result['individual_moves']}",
                flush=True,
            )

    print("\nSummary")
    for label in ("minimax", "random", "Draw", "Unfinished"):
        count = sum(row["winner"] == label for row in results)
        print(f"{label}: {count}")

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()