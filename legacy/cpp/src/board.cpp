#include "../include/board.hpp"
#include <iostream>

Board::Board() {
    load_fen();
}

void Board::load_fen(const std::string& fen) {
    // TODO Parse the FEN string and fill squares[64], side_to_move, castling_rights, etc.
}

void Board::print() const {
    // TODO  Loop through ranks 8 down to 1 and print the board to the terminal.
    std::cout << "[Board::print() not implemented yet]\n";
}

void Board::make_move(const Move& move) {
    // TODO Save UndoState to history, move the piece on squares[], and update turn/castling.
}

void Board::undo_move() {
    // TODO Pop the last UndoState from history and restore the board.
}

bool Board::is_square_attacked(int sq, int attacker_color) const {
    // TODO  Check if 'sq' is attacked by pawns, knights, king, rooks/queens, or bishops/queens.
    return false;
}

bool Board::in_check(int color) const {
    // TODO  Find the king of 'color' and call is_square_attacked().
    return false;
}

std::string Board::sq_to_string(int sq) {
    // TODO  Convert square index (0-63) to string like "e2".
    return "a1";
}
