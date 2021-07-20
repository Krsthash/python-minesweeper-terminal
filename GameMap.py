#!/usr/bin/env python
"""
Map generator and functions.
"""
import random


class GameMap:
    def __init__(self, cols: int, rows: int, mines: int):
        self.cols = cols
        self.rows = rows
        self.mines = mines
        self.mines_left = mines
        self.move_count = 0
        self.first_move = 0
        # Creating the grid
        self.grid = [[" " for _ in range(cols)] for _ in range(rows)]
        # Creating the visible map
        self.vmap = [["░" for _ in range(cols)] for _ in range(rows)]

    def generate_mines(self):
        mines_left = self.mines
        while True:
            for rows in self.grid:
                for i in range(len(rows)):
                    if random.randint(0, 10) == 10:  # 10% chance for a mine to be generated in a square
                        rows[i] = "X"
                        mines_left -= 1
                        if mines_left == 0:
                            return

    def generate_pointers(self):
        """
        Fill the whole grid with correct mine counts.
        """
        for y in range(self.rows):
            for x in range(self.cols):
                mines_num = 0
                if self.grid[y][x] == "X":
                    continue
                surrounding_squares = self.surrounding_tiles(y, x)  # Get a list of surrounding squares
                for square in surrounding_squares:
                    if square[2] == "X":
                        mines_num += 1
                self.grid[y][x] = mines_num  # Write the mine count on the square

    def pointer_status(self, y, x):
        """
        Check a single square's surrounding mine count.
        """
        mines_num = 0
        if self.grid[y][x] == "X":
            return
        # Checking if surrounding tiles have mines in them
        mines = self.surrounding_tiles(y, x)
        for mine in mines:
            if mine[2] == "X":
                mines_num += 1
        return mines_num

    def move_first_mine(self, y, x):  # Move the mine into a corner.
        count = 0
        while True:  # Try to place the X in a corner, if it's occupied check the square to its right.
            if self.grid[0][count] != "X":
                self.grid[0][count] = "X"
                # self.vmap[y][x] = 0
                self.grid[y][x] = 0
                self.generate_pointers()
                break
            else:
                count += 1
        self.generate_pointers()  # Generate new mine counts for every square.

    def clear_tile(self, y, x):
        if self.first_move == 0:
            self.first_move = 1  # Set the value to 1 meaning the first move has been played.
            mine = 0
            for square in self.surrounding_tiles(y, x):  # Check if there is a mine in the surrounding squares.
                if square[2] == "X":
                    mine = 1  # There is a mine on the first move!
                    self.move_first_mine(square[0], square[1])
            if self.grid[y][x] == "X":
                mine = 1  # There is a mine on the first move!
                self.move_first_mine(y, x)
            if mine == 1:
                if self.grid[y][x] == 0:
                    self.open_zeros(y, x)
                    return
                else:
                    self.vmap[y][x] = self.grid[y][x]
        if self.grid[y][x] == "X":
            return 0  # Game lost
        elif self.grid[y][x] == 0:
            self.open_zeros(y, x)  # If you cleared a zero, open all zeros that are touching it.
        else:
            self.vmap[y][x] = self.grid[y][x]  # Open the square.

    def win_check(self):  # Check if the last square was opened and the game won (ran after every move).
        self.move_count += 1  # Edit the value to show a move has been made.
        number_of_open_tiles = 0
        number_of_tiles = self.rows * self.cols
        for rows in self.vmap:
            for cols in rows:
                if cols != "░" and cols != "X":
                    number_of_open_tiles += 1
        if number_of_tiles - number_of_open_tiles == self.mines:
            return 1

    def mark(self, y, x):
        if self.vmap[y][x] == "░":
            self.vmap[y][x] = "X"
            self.mines_left -= 1
        else:
            return 0

    def unmark(self, y, x):
        if self.vmap[y][x] == "X":
            self.vmap[y][x] = "░"
            self.mines_left += 1
        else:
            print("You can't unflag that square!")

    def adjacent(self, y, x):  # Open all squares around a specified square (ignoring flagged squares).
        if isinstance(self.vmap[y][x], int):  # Check if the square you want to open is empty.
            tile = self.vmap[y][x]
            adjacent_vsquares = self.surrounding_vtiles(y, x)
            adjacent_squares = self.surrounding_tiles(y, x)
            number_of_mines = 0
            for square in adjacent_vsquares:
                number_of_mines += square.count("X")
            if not number_of_mines == tile:
                # If the number of mines marked next to the tile is more or less than
                # needed, you will not be able to open it.
                return 1
            for square in adjacent_vsquares:
                if square[2] == "X":
                    if not self.grid[square[0]][square[1]] == "X":  # Check if the marked mines are correctly marked
                        return 0
            for square in adjacent_squares:
                if square[2] == 0:
                    self.open_zeros(square[0], square[1])
                self.vmap[square[0]][square[1]] = self.grid[square[0]][square[1]]
            return

    def surrounding_vtiles(self, y, x):  # Get all visible (opened) squares around a specified square.
        dic = []
        directions = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]  # Directions to check for.
        for dx in directions:
            try:
                if y + dx[0] < 0 or x + dx[1] < 0:  # If the coordinates are negative (a corner), ignore it.
                    continue
                dic.append([y + dx[0], x + dx[1], self.vmap[y + dx[0]][x + dx[1]]])  # y, x, square_status
            except IndexError:  # If the square we are checking is out of bounds, ignore it.
                pass
        return dic

    def surrounding_tiles(self, y, x):  # Get all squares (including unopened squares) around a specified square.
        dic = []
        directions = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]  # Directions to check for.
        for dx in directions:
            try:
                if y + dx[0] < 0 or x + dx[1] < 0:  # If the coordinates are negative (a corner), ignore it.
                    continue
                dic.append([y + dx[0], x + dx[1], self.grid[y + dx[0]][x + dx[1]]])  # y, x, square_status
            except IndexError:  # If the square we are checking is out of bounds, ignore it.
                pass
        return dic

    def open_zeros(self, y, x):  # Open squares that touch a zero mine square.
        to_be_processed = [[y, x, 0]]
        processed = []
        while True:
            for zero in to_be_processed:
                to_be_processed.remove(zero)
                processed.append(zero)
                for tile in self.surrounding_tiles(zero[0], zero[1]):  # Check all surrounding squares.
                    self.vmap[tile[0]][tile[1]] = self.grid[tile[0]][tile[1]]
                    if tile[2] == 0:  # If the square is zero, check all surrounding tiles in the next iteration.
                        if tile not in processed:
                            to_be_processed.append(tile)
            if len(to_be_processed) <= 0:  # Once there is no more zeros to open, return.
                return


if __name__ == '__main__':
    pass
