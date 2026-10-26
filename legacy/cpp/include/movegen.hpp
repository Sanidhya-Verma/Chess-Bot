#pragma once
#include "types.hpp"
#include "board.hpp"
#include <vector>

// ============================================================================
// MOVE GENERATOR BLUEPRINT (To be implemented in src/movegen.cpp)
// ============================================================================
class MoveGen {
public:
    // Generates all pseudo-legal moves (ignores whether the King is left in check)
    static std::vector<Move> generate_pseudo_legal_moves(const Board& board);

    // Generates strictly legal moves (filters out moves that leave our King in check)
    static std::vector<Move> generate_legal_moves(Board& board);
};
