#pragma once
#include "types.hpp"
#include "board.hpp"

// ============================================================================
// AI SEARCH BLUEPRINT (To be implemented in src/search.cpp)
// ============================================================================
class Search {
public:
    // Uses Minimax + Alpha-Beta Pruning to find the best move within the time limit (3000 ms = 3 seconds)
    static Move find_best_move(Board& board, int max_depth, int time_limit_ms = 3000);
};
