#include <iostream>
#include "../include/board.hpp"
#include "../include/movegen.hpp"
#include "../include/evaluation.hpp"
#include "../include/search.hpp"

int main() {
    std::cout << "=== Chess-Bot Engine Initialized ===\n";

    Board board;
    board.print();

    // TODO: Add game loop so a human can play against the AI in the terminal!
    return 0;
}
