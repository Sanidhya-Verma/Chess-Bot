# Chess-Bot
Chess-Bot project 
run the following commands for establishing dependencies:
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -e ".[dev]"
Check dependencies:
    python -m pip list
Current dependencies:
    chess     1.11.2
    chess-bot 0.0.1   /home/avin_prakash/projects/Chess-Bot
    iniconfig 2.3.1
    numpy     2.5.4
    packaging 26.3
    pip       26.2.2
    pluggy    1.7.0
    Pygments  2.21.0
    pytest    9.1.1
    ruff      0.17.2
Evaluation is from white's prespective

FastApi:
    uv run uvicorn chessbot.api:app -- reload
    "Open in seperate terminal for local host"
    
## Simulation results

All result files are stored in `tests/simulations/`.

| CSV file | Matchup and settings | Recorded results |
|---|---|---|
| [random_results.csv](tests/simulations/random_results.csv) | Random vs random | 10 games: 1 White win, 1 draw, 8 unfinished |
| [stockfish_vs_random.csv](tests/simulations/stockfish_vs_random.csv) | Stockfish vs random | Stockfish won all 10 games |
| [minimax_vs_random_depth4.csv](tests/simulations/minimax_vs_random_depth4.csv) | Raw minimax at depth 4 vs random | Minimax won both games |
| [stockfish_vs_minimax.csv](tests/simulations/stockfish_vs_minimax.csv) | Stockfish vs raw minimax at depth 4 | Stockfish won both games |
| [alpha_beta_vs_random_depth5.csv](tests/simulations/alpha_beta_vs_random_depth5.csv) | Alpha–beta at depth 5 vs random | Alpha–beta won both games |
| [stockfish_vs_alpha_beta_depth5.csv](tests/simulations/stockfish_vs_alpha_beta_depth5.csv) | Stockfish vs alpha–beta at depth 5 | Stockfish won both games |
| [mcts_vs_random_1000iter_1sec.csv](tests/simulations/mcts_vs_random_1000iter_1sec.csv) | MCTS vs random | MCTS won both games|
| [stockfish_vs_mcts_1000iter_1sec.csv](tests/simulations/stockfish_vs_mcts_1000iter_1sec.csv) | Stockfish vs MCTS | Stockfish won both games |
| [mcts_vs_alpha_beta_depth5_1000iter_1sec.csv](tests/simulations/mcts_vs_alpha_beta_depth5_1000iter_1sec.csv) | MCTS vs alpha–beta at depth 5 | Alpha–beta won both games |
