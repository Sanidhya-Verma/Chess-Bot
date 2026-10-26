#include "../include/movegen.hpp"

std::vector<Move> MoveGen::generate_pseudo_legal_moves(const Board& board) {
    std::vector<Move> moves;
    // TODO  Loop over all 64 squares and generate moves for Pawns, Knights, Bishops, Rooks, Queens, Kings.
    return moves;
}

std::vector<Move> MoveGen::generate_legal_moves(Board& board) {
    std::vector<Move> legal_moves;
    // TODO  Call generate_pseudo_legal_moves(), make each move, check if in_check(), and undo_move().
    return legal_moves;
}
