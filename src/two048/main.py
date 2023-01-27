from __future__ import annotations

import random
from collections.abc import Iterable
from enum import Enum
from typing import Literal

DirectionString = Literal["up", "down", "left", "right"]


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class Tile:
    def __init__(self, value: int) -> None:
        self.value = value

    def double(self, game: Two048 | None = None):
        """Used by the game to double the value of the tile. You should not use this function yourself."""
        self.value *= 2
        if game is not None:
            game.score += self.value

    def __repr__(self) -> str:
        return f"{self.value}"

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Tile):
            return self.value == __o.value
        if isinstance(__o, int):
            return self.value == __o
        raise TypeError(f"Cannot compare Tile with {type(__o)}")


class Movement:
    """
    Represent a movement of a Tile.
    """

    def __init__(
        self, from_: tuple[int, int], to: tuple[int, int], merged: bool
    ) -> None:
        self.from_ = from_
        self.to = to
        self.merged = merged

    def __repr__(self) -> str:
        return f"{self.from_} move to {self.to}. Merged: {self.merged}"


class MovementManager:
    def __init__(self, *args: Movement) -> None:
        self.movements: list[Movement] = list(args)
        self.hash_find = {mvmt.to: mvmt for mvmt in self.movements}

    def add_movement(self, value: Movement) -> None:
        """Add a new movement in the current set of movements.
        Each tiles should only have one movement, from the start to the destination. No "sequenced" movements.

        Args:
            value: The movement to append.
        """
        if (tile := self.hash_find.get(value.from_, None)) is not None:
            # If a movement exist already (i.e. it is sequenced), edit the already stored movement.
            tile.to = value.to
            tile.merged = value.merged
        else:
            self.movements.append(value)
            self.hash_find[value.to] = value

    def add_movements(self, values: Iterable[Movement]) -> None:
        """Add a list of movements. See add_movement for more details.

        Args:
            values: An stack of movements.
        """
        for move in values:
            self.add_movement(move)

    def __repr__(self) -> str:
        return "\n".join(str(move) for move in self.movements)

    def __bool__(self) -> bool:
        return self.movements != []


class Two048:
    score: int
    moves: int
    board: list[list[Tile]]

    def __init__(self) -> None:
        self.reset()
        self.spawn_tile()

    def reset(self):
        """Reset the game"""
        self.score = 0
        self.moves = 0
        self.board = self.generate_empty_board()

    def generate_empty_board(self) -> list[list[Tile]]:
        """Generate an empty board.

        Returns:
            A new empty board filled with Tile(0)
        """
        return [[Tile(0) for _ in range(4)] for __ in range(4)]

    def get_empty_positions(self) -> list[tuple[int, int]]:
        """Get a list of the empty positions. This is managed by the game : you should not use it.

        Returns:
            A list of empty positions
        """
        return [
            (i, j) for i in range(4) for j in range(4) if self.board[i][j].value == 0
        ]

    def spawn_tile(self):
        """Spawn a new tile on the board. This is managed by the game : you should not use it."""
        valid_positions: list[tuple[int, int]] = self.get_empty_positions()
        spawn_position = random.choice(valid_positions)
        (new_tile,) = random.sample([Tile(2), Tile(4)], counts=[9, 1], k=1)
        self.board[spawn_position[0]][spawn_position[1]] = new_tile

    def play(self, direction: Direction | DirectionString) -> list[Movement]:
        """Use this fonction to play the game. Use a direction with Direction or "up", "down", "left", "right".

        Args:
            direction: The direction you want to play. Can be "up", "down", "left" or "right", or a Direction enum.

        Returns:
            The list of movements made. Including merges. Useful if you need to do animations.
        """
        if isinstance(direction, str):
            direction = Direction(direction)

        movements_manager = MovementManager()
        movements_manager.add_movements(self._move_without_merge(direction))
        movements_manager.add_movements(self._merge(direction))
        movements_manager.add_movements(self._move_without_merge(direction))

        if movements_manager:
            self.spawn_tile()
            self.moves += 1

        return movements_manager.movements

    def is_over(self) -> bool:
        """To know if then game is over

        Returns:
            True if it is gameover, False otherwise.
        """
        for direction in Direction:
            if (
                len(self._move_without_merge(direction, False)) != 0
                or len(self._merge(direction, False)) != 0
            ):
                return False
        return True

    def _apply_movements(self, movements: Iterable[Movement]):
        """Apply a list of movements to the board.

        Args:
            movements: A list of movements
        """
        for mvmt in movements:
            if mvmt.merged:
                self.board[mvmt.to[0]][mvmt.to[1]].double(self)
                self.board[mvmt.from_[0]][mvmt.from_[1]] = Tile(0)
            else:
                self.board[mvmt.to[0]][mvmt.to[1]] = self.board[mvmt.from_[0]][
                    mvmt.from_[1]
                ]
                self.board[mvmt.from_[0]][mvmt.from_[1]] = Tile(0)

    def _move_without_merge(
        self, direction: Direction, apply: bool = True
    ) -> list[Movement]:
        """Move the tiles within the direction given, without merging them.
        Return a list of the movements made.

        Args:
            direction: the direction to move
            apply: if the board should be edited or not. Allow to check if the game is ended.

        Returns:
            the list of movements made
        """
        match direction:
            case Direction.UP:
                ordered_check = ((j, i, j) for j in range(4) for i in range(4))

                def new_pos(i: int, j: int, av: int):
                    return (i - av, j)

            case Direction.DOWN:
                ordered_check = ((j, i, j) for j in range(4) for i in range(3, -1, -1))

                def new_pos(i: int, j: int, av: int):
                    return (i + av, j)

            case Direction.LEFT:
                ordered_check = ((i, i, j) for i in range(4) for j in range(4))

                def new_pos(i: int, j: int, av: int):
                    return (i, j - av)

            case Direction.RIGHT:
                ordered_check = ((i, i, j) for i in range(4) for j in range(3, -1, -1))

                def new_pos(i: int, j: int, av: int):
                    return (i, j + av)

        movements: list[Movement] = []
        available_moves: list[int] = [0] * 4

        for cl, i, j in ordered_check:
            if self.board[i][j].value == 0:
                available_moves[cl] += 1
            else:
                if available_moves[cl] != 0:
                    movements.append(
                        Movement((i, j), new_pos(i, j, available_moves[cl]), False)
                    )

        if apply:
            self._apply_movements(movements)
        return movements

    def _merge(self, direction: Direction, apply: bool = True) -> list[Movement]:
        """Merge the tiles within the direction given. Hole may be present after merge. It is necessary to call _move_without_merge after this function.
        Return a list of the movements made.

        Args:
            direction: the direction to merge
            apply: if the board should be edited or not. Allow to check if the game is ended.


        Returns:
            the list of movements made
        """
        match direction:
            case Direction.UP:
                ordered_check = (((i, j) for i in range(4)) for j in range(4))
            case Direction.DOWN:
                ordered_check = (((i, j) for i in range(3, -1, -1)) for j in range(4))
            case Direction.LEFT:
                ordered_check = (((i, j) for j in range(4)) for i in range(4))
            case Direction.RIGHT:
                ordered_check = (((i, j) for j in range(3, -1, -1)) for i in range(4))

        movements: list[Movement] = []
        for group in ordered_check:
            prev: tuple[int, int] | None = None
            moved: bool = False
            for i, j in group:
                if prev is None:
                    prev = (i, j)
                    continue
                if not moved and self.board[prev[0]][prev[1]] == self.board[i][j] != 0:
                    movements.append(Movement((i, j), prev, True))
                    moved = True
                else:
                    moved = False
                prev = (i, j)

        if apply:
            self._apply_movements(movements)

        return movements

    def __repr__(self) -> str:
        display = (
            "Score : {score}\n"
            "|-------------------------------|\n"
            "| {:^5} | {:^5} | {:^5} | {:^5} |\n"
            "|-------------------------------|\n"
            "| {:^5} | {:^5} | {:^5} | {:^5} |\n"
            "|-------------------------------|\n"
            "| {:^5} | {:^5} | {:^5} | {:^5} |\n"
            "|-------------------------------|\n"
            "| {:^5} | {:^5} | {:^5} | {:^5} |\n"
            "⌞_______________________________」⌟\n"
        ).format(
            score=self.score,
            *[
                (tile.value if tile.value != 0 else "")
                for row in self.board
                for tile in row
            ],
        )
        return display


if __name__ == "__main__":
    game: Two048 = Two048()

    while game.is_over() is False:
        print(game)
        direction: Direction = {
            "\x1b[A": Direction.UP,
            "\x1b[B": Direction.DOWN,
            "\x1b[D": Direction.LEFT,
            "\x1b[C": Direction.RIGHT,
        }[input("Direction : ")]
        game.play(direction)

    print(game)
    print("Game over ! Score :", game.score)
