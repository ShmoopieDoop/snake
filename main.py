import pygame
from enum import Enum
import random
import os

from pygame.constants import K_DOWN, K_LEFT, K_RIGHT, K_SPACE, K_UP

pygame.init()

WIN_SIZE = (800, 800)
WIN = pygame.display.set_mode(WIN_SIZE)
pygame.display.set_caption("Snake")
run = True
score = 3

SNAKE_HEAD: pygame.Surface = pygame.image.load(os.path.join("Assets", "snakeHead.png"))
SNAKE_STRAIGHT: pygame.Surface = pygame.image.load(
    os.path.join("Assets", "snakeStraight.png")
)
SNAKE_TAIL: pygame.Surface = pygame.image.load(os.path.join("Assets", "snakeTail.png"))
SNAKE_TURN: pygame.Surface = pygame.image.load(os.path.join("Assets", "snakeTurn.png"))
APPLE: pygame.Surface = pygame.image.load(os.path.join("Assets", "apple.png"))


class Directions(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class Cell:
    def __init__(self, coords: tuple[int, int], grid, isDark: bool):
        self.coords = coords
        self.isDark = isDark  # for checkerboard background pattern
        self.rect = pygame.Rect(
            coords[0] / grid.width * WIN_SIZE[0],
            coords[1] / grid.height * WIN_SIZE[1],
            WIN_SIZE[0] / grid.width,
            WIN_SIZE[1] / grid.height,
        )


class Empty(Cell):
    TYPE = 0


class Wall(Cell):
    TYPE = 1


class Body(Cell):
    TYPE = 2

    def __init__(
        self, coords: tuple[int, int], grid, isDark: bool, isHead: bool, direction: int
    ):
        super().__init__(coords, grid, isDark)
        self.isHead = isHead  # TODO: no reason for this to exist
        self.surface: pygame.Surface = SNAKE_STRAIGHT
        self.direction = direction


class Apple(Cell):
    TYPE = 3
    surface: pygame.Surface = APPLE


class Grid(list):
    def __init__(self, size: int):
        """
        The grid is a dynamic 2 dimensional array.
        Board will change based on size of the grid.
        """
        # TODO: automatically scale images to fit the grid
        self.width = size
        self.height = size
        for i in range(self.height):
            self.append([])
            for j in range(self.width):
                isDark = (j % 2 + i % 2) % 2 == 0  # checkerboard pattern
                self[-1].append(Empty((j, i), self, isDark))

    def build_walls(self):  # walls are all cells on edge of the 2d array
        for i in range(self.height):
            for j in range(self.width):
                if i in (0, self.height - 1) or j in (0, self.width - 1):
                    self[i][j] = Wall((j, i), self, self[i][j].isDark)

    def find_empty_cells(self):
        empty_cells = []
        for i, row in enumerate(self):
            for j, cell in enumerate(row):
                if cell.TYPE == Empty.TYPE:
                    empty_cells.append((j, i))
        return empty_cells

    def spawn_apple(self):
        apple_coords = random.choice(self.find_empty_cells())
        apple_cell = self[apple_coords[1]][apple_coords[0]]
        self[apple_coords[1]][apple_coords[0]] = Apple(
            apple_coords, self, apple_cell.isDark
        )

    def draw(self):
        for row in self:
            for cell in row:
                color = "grey" if cell.isDark else "lightGrey"
                if cell.TYPE == Wall.TYPE:
                    color = (125, 125, 125)
                pygame.draw.rect(
                    WIN,
                    color,
                    cell.rect,
                )
                if cell.TYPE in (Body.TYPE, Apple.TYPE):
                    WIN.blit(cell.surface, cell.rect)


class Snake:
    angles = {
        Directions.UP: 0,
        Directions.LEFT: 90,
        Directions.DOWN: 180,
        Directions.RIGHT: 270,
    }

    def __init__(self, start_pos: tuple[int, int], start_len: int, grid: Grid):
        self.start_pos = start_pos
        self.len = start_len
        self.direction = Directions.RIGHT
        self.grid = grid
        self.body_parts: list[Body] = []
        if start_pos[0] < start_len + 1:
            print("Too close to wall")
            quit()
        for i in range(start_pos[0] - start_len, start_pos[0]):  # spawn snake
            coords = (i, start_pos[1])
            part = Body(
                coords,
                grid,
                grid[coords[1]][coords[0]].isDark,
                not (i - start_pos[0]),
                Directions.RIGHT,
            )
            grid[coords[1]][coords[0]] = part
            self.body_parts.append(part)
        self.head = self.grid[start_pos[1]][start_pos[0]]

    def die(self):  # if the program reaches this you suck
        global run
        print("Die!")
        print(f"You scored {score} points")
        run = False

    def angle_head(self):
        head = SNAKE_HEAD.copy()
        head = pygame.transform.rotate(head, self.angles[self.direction])
        self.body_parts[-1].surface = head
        self.body_parts[-2].surface = SNAKE_STRAIGHT

    def angle_turn(self):
        """
        Rotates snakeTurn.png according to the direction of the snake.
        If the snake turned left rotate clockwise to account for that.
        """
        turned_part = self.body_parts[-2]
        og_angle = self.angles[self.body_parts[-3].direction]
        new_angle = self.angles[self.body_parts[-1].direction]
        angle = og_angle
        if (new_angle - og_angle + 360) % 360 == 90:
            # (... + 360) % 360 to account for one case where the turn angle is -270 instead of 90
            angle -= 90
        turn = SNAKE_TURN.copy()
        turn = pygame.transform.rotate(turn, angle)
        turned_part.surface = turn
        self.body_parts[-2].direction = self.body_parts[-1].direction

    def angle_tail(self):
        tail = SNAKE_TAIL.copy()
        tail = pygame.transform.rotate(tail, self.angles[self.body_parts[0].direction])
        self.body_parts[0].surface = tail

    def move(self, turned: bool):
        head_coords = self.body_parts[-1].coords
        tail_coords = self.body_parts[0].coords
        # TODO: very long 'if' stack don't know if possible to shorten
        if self.direction == Directions.UP:
            next_coords = (head_coords[0], head_coords[1] - 1)
        if self.direction == Directions.RIGHT:
            next_coords = (head_coords[0] + 1, head_coords[1])
        if self.direction == Directions.DOWN:
            next_coords = (head_coords[0], head_coords[1] + 1)
        if self.direction == Directions.LEFT:
            next_coords = (head_coords[0] - 1, head_coords[1])
        next_cell_type = self.grid[next_coords[1]][next_coords[0]].TYPE
        next = self.grid[next_coords[1]][next_coords[0]]
        if next_cell_type in (Wall.TYPE, Body.TYPE):
            self.die()  # what a loser
        else:  # create new snake head
            self.head.isHead = False
            self.head = Body(next_coords, self.grid, next.isDark, True, self.direction)
            self.grid[next_coords[1]][next_coords[0]] = self.head
            self.body_parts.append(self.head)
            self.angle_head()
        if next_cell_type == Empty.TYPE:  # remove tail
            self.grid[tail_coords[1]][tail_coords[0]] = Empty(
                (tail_coords[0], tail_coords[1]),
                self.grid,
                self.grid[tail_coords[1]][tail_coords[0]].isDark,
            )
            self.body_parts.pop(0)
            self.angle_tail()
        else:
            # gets here if snake ate an apple.
            # rather than adding a body part just doesn't remove tail
            global score
            score += 1
            self.grid.spawn_apple()
        if turned:
            self.angle_turn()


def is_opposite_direction(new_direction, old_direction):
    opposite_directions = {
        Directions.UP: Directions.DOWN,
        Directions.DOWN: Directions.UP,
        Directions.LEFT: Directions.RIGHT,
        Directions.RIGHT: Directions.LEFT,
    }
    return old_direction == opposite_directions[new_direction]


def main():
    global run
    key_to_direction = {
        K_UP: Directions.UP,
        K_DOWN: Directions.DOWN,
        K_RIGHT: Directions.RIGHT,
        K_LEFT: Directions.LEFT,
    }
    grid = Grid(20)
    grid.build_walls()
    grid.spawn_apple()
    snake = Snake((4, 2), score, grid)
    clock = pygame.time.Clock()
    frame = 0
    can_turn = True
    play = True
    while run:
        if play:
            grid.draw()
            if frame == 10:  # move every 10 frames
                frame = 0
                snake.move(not can_turn)
                can_turn = True
            frame += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_SPACE:
                    play = not play
                if can_turn:
                    if event.key in key_to_direction and not is_opposite_direction(
                        key_to_direction[event.key], snake.direction
                    ):
                        if event.key == K_UP:
                            snake.direction = Directions.UP
                        if event.key == K_RIGHT:
                            snake.direction = Directions.RIGHT
                        if event.key == K_DOWN:
                            snake.direction = Directions.DOWN
                        if event.key == K_LEFT:
                            snake.direction = Directions.LEFT
                        can_turn = False
        clock.tick(60)
        pygame.display.update()


if __name__ == "__main__":
    main()
