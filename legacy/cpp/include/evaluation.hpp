#pragma once
#include "board.hpp"

// ============================================================================
// BOARD EVALUATION BLUEPRINT (To be implemented in src/evaluation.cpp)
// ============================================================================
class Evaluation {
public:
    // Returns a score for the current board position from the perspective of side_to_move.
    // Positive = current player is winning. Negative = current player is losing.
    static int evaluate(const Board& board);
};
