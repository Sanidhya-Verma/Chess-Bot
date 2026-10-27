## Backend testing
Added tests in:
- tests/test_evaluation.py — 8 tests
- tests/test_api.py — 5 tests

### Evaluation checks:
- Starting position scores zero.
- An extra white pawn scores +100.
- An extra black pawn scores -100.
- Kings-only position scores zero.
- Evaluation does not change the board position.
- Checkmate scores have the correct sign for each side.
- Stalemate scores zero.

### API checks:
- Health endpoint responds successfully.
- Starting position returns 20 legal moves.
- Invalid FEN is rejected.
- Evaluation endpoint returns the expected material score.
- Board endpoint correctly reports stalemate.

### Run these test on Windows terminal
.venv\Scripts\python.exe -m pytest tests/test_evaluation.py tests/test_api.py -v

### Latest result : 13 passed, 2 warnings

Known configuration warning:
Pytest reports "Unknown config option: license".
The license entry is currently under the pytest configuration section.

Engine benchmarking has not been performed yet.
