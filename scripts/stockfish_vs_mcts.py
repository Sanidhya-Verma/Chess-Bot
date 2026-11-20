import csv
import sys
from pathlib import Path
from time import perf_counter
from chessbot.mcts import mcts_search

import chess.engine

from chessbot.game import Game


def run_game(engine, seed, move_limit=300):
    game = Game()
    game_token = object()
    stockfish_colour = "White" if seed % 2 else "Black"

    players = {
        "White": "stockfish" if stockfish_colour == "White" else "mcts",
        "Black": "stockfish" if stockfish_colour == "Black" else "mcts",
    }
    thinking_time = {"White": 0.0, "Black": 0.0}
    move_counts = {"White": 0, "Black": 0}
    moves_played = 0

    while moves_played < move_limit:
        if game.board_copy().is_game_over(claim_draw=True):
            break
        side = game.turn()
        board = game.board_copy()

        start = perf_counter()
        if players[side] == "stockfish":
            response = engine.play(
                board,
                chess.engine.Limit(time=0.1),
                game=game_token,
            )
            move = response.move
        else:
            move = mcts_search(board,iterations = 1000,time_limit=1.0)

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

    outcome = game.board_copy().outcome(claim_draw=True)
    if outcome is None:
        result = "Unfinished"
    elif outcome.winner is None:
        result = "Draw"
    else:
        result = "White" if outcome.winner else "Black"
    winner = players[result] if result in players else result

    return {
        "seed": seed,
        "mcts_iterations_limit": 1000,
        "mcts_time_limit_seconds": 1.0,
        "white_player": players["White"],
        "black_player": players["Black"],
        "result": result,
        "winner": winner,
        "reason": outcome.termination.name if outcome else "MOVE_LIMIT",
        "individual_moves": moves_played,
        "move_limit": move_limit,
        "white_moves": move_counts["White"],
        "black_moves": move_counts["Black"],
        "white_seconds": thinking_time["White"],
        "black_seconds": thinking_time["Black"],
        "final_fen": game.snapshot()["fen"],
        "stockfish_version": engine.id.get("name", "unknown"),
        "stockfish_seconds_per_move": 0.1,
        "stockfish_threads": 1,
        "stockfish_hash_mb": 64,
        "stockfish_skill_level": 20,
        "claim_draw": True,
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            'Usage: python scripts/stockfish_vs_mcts.py "path_to_stockfish.exe"'
        )

    engine_path = Path(sys.argv[1])
    if not engine_path.is_file():
        raise SystemExit(f"Stockfish executable not found: {engine_path}")

    project_root = Path(__file__).resolve().parents[1]
    results_folder = project_root / "tests" / "simulations"
    results_folder.mkdir(parents=True, exist_ok=True)
    output_file = results_folder / "stockfish_vs_mcts_1000iter_1sec.csv"
    results = []

    with chess.engine.SimpleEngine.popen_uci(str(engine_path)) as engine:
        engine.configure({
            "Threads": 1,
            "Hash": 64,
            "Skill Level": 20,
            "UCI_LimitStrength": False,
        })

        with output_file.open("w", newline="", encoding="utf-8") as file:
            writer = None

            for game_number in range(1, 3):
                print(f"Starting game {game_number}/2...", flush=True)
                result = run_game(engine, seed=game_number)
                row = {"game": game_number, **result}
                results.append(row)

                if writer is None:
                    writer = csv.DictWriter(file, fieldnames=list(row))
                    writer.writeheader()

                writer.writerow(row)
                file.flush()

                print(
                    f"Winner: {result['winner']} | "
                    f"Reason: {result['reason']} | "
                    f"Individual moves: {result['individual_moves']}",
                    flush=True,
                )

    print("\nSummary")
    for label in ("stockfish", "mcts", "Draw", "Unfinished"):
        count = sum(row["winner"] == label for row in results)
        print(f"{label}: {count}")

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()