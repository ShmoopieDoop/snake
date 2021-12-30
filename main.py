import pygame
from enum import Enum
import random

from pygame.constants import K_DOWN, K_LEFT, K_RIGHT, K_UP

WIN_SIZE = (800, 800)
WIN = pygame.display.set_mode(WIN_SIZE)
run = True
score = 3


class Directions(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class Cell:
    def __init__(self, coords: tuple[int, int], grid):
        self.coords = coords
        self.rect = pygame.Rect(
            coords[0] / grid.width * WIN_SIZE[0] + 1,
            coords[1] / grid.height * WIN_SIZE[1] + 1,
            WIN_SIZE[0] / grid.width - 1,
            WIN_SIZE[1] / grid.height - 1,
        )


class Empty(Cell):
    TYPE = 0


class Wall(Cell):
    TYPE = 1


class Body(Cell):
    TYPE = 2


class Apple(Cell):
    TYPE = 3


class Grid(list):
    def __init__(self, size: int):
        self.width = size
        self.height = size
        for i in range(self.height):
            self.append([Empty((j, i), self) for j in range(self.width)])

    def build_walls(self):
        for i in range(self.height):
            for j in range(self.width):
                if i in (0, self.height - 1) or j in (0, self.width - 1):
                    self[i][j] = Wall((j, i), self)

    def find_empty_cells(self):
        empty_cells = []
        for i, row in enumerate(self):
            for j, cell in enumerate(row):
                if cell.TYPE == Empty.TYPE:
                    empty_cells.append((j, i))
        return empty_cells

    def spawn_apple(self):
        apple_coords = random.choice(self.find_empty_cells())
        self[apple_coords[1]][apple_coords[0]] = Apple(apple_coords, self)

    def draw(self):
        for i in range(self.width):
            pygame.draw.line(
                WIN,
                "grey",
                (((i + 1) / self.width) * WIN_SIZE[0], 0),
                (((i + 1) / self.width) * WIN_SIZE[0], WIN_SIZE[1]),
            )
        for i in range(self.height):
            pygame.draw.line(
                WIN,
                "grey",
                (0, ((i + 1) / self.width) * WIN_SIZE[1]),
                (WIN_SIZE[0], (((i + 1) / self.width) * WIN_SIZE[1])),
            )
        for row in self:
            for cell in row:
                if cell.TYPE == Empty.TYPE:
                    color = "black"
                elif cell.TYPE == Wall.TYPE:
                    color = "grey"
                elif cell.TYPE == Body.TYPE:
                    color = "green"
                elif cell.TYPE == Apple.TYPE:
                    color = "red"
                pygame.draw.rect(
                    WIN,
                    color,
                    cell.rect,
                )


class Snake:
    def __init__(self, start_pos: tuple[int, int], start_len: int, grid: Grid):
        self.start_pos = start_pos
        self.len = start_len
        self.direction = Directions.RIGHT
        self.grid = grid
        self.body_parts: list[Body] = []
        if start_pos[0] < start_len + 1:
            print("Too close to wall")
            quit()
        for i in range(start_pos[0] - start_len, start_pos[0]):
            coords = (i, start_pos[1])
            part = Body(coords, grid)
            grid[coords[1]][coords[0]] = part
            self.body_parts.append(part)

    def die(self):
        global run
        print("Die!")
        print(f"You scored {score} points")
        run = False

    def move(self):
        head_coords = self.body_parts[-1].coords
        tail_coords = self.body_parts[0].coords
        if self.direction == Directions.UP:
            next_coords = (head_coords[0], head_coords[1] - 1)
        if self.direction == Directions.RIGHT:
            next_coords = (head_coords[0] + 1, head_coords[1])
        if self.direction == Directions.DOWN:
            next_coords = (head_coords[0], head_coords[1] + 1)
        if self.direction == Directions.LEFT:
            next_coords = (head_coords[0] - 1, head_coords[1])
        next_cell_type = self.grid[next_coords[1]][next_coords[0]].TYPE
        if next_cell_type in (
            Wall.TYPE,
            Body.TYPE,
        ):
            self.die()
        else:
            new_head = Body(next_coords, self.grid)
            self.grid[next_coords[1]][next_coords[0]] = new_head
            self.body_parts.append(new_head)
        if next_cell_type == Empty.TYPE:
            self.grid[tail_coords[1]][tail_coords[0]] = Empty(
                (tail_coords[0], tail_coords[1]), self.grid
            )
            self.body_parts.pop(0)
        else:
            global score
            score += 1
            self.grid.spawn_apple()


def main():
    global run
    grid = Grid(20)
    grid.build_walls()
    grid.spawn_apple()
    snake = Snake((4, 2), score, grid)
    clock = pygame.time.Clock()
    frame = 0
    can_turn = True
    while run:
        grid.draw()
        if frame == 10:
            frame = 0
            snake.move()
            can_turn = True
        frame += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if can_turn:
                    if event.key == K_UP:
                        snake.direction = (
                            Directions.UP
                            if snake.direction != Directions.DOWN
                            else snake.direction
                        )
                        can_turn = False
                    if event.key == K_RIGHT:
                        snake.direction = (
                            Directions.RIGHT
                            if snake.direction != Directions.LEFT
                            else snake.direction
                        )
                        can_turn = False
                    if event.key == K_DOWN:
                        snake.direction = (
                            Directions.DOWN
                            if snake.direction != Directions.UP
                            else snake.direction
                        )
                        can_turn = False
                    if event.key == K_LEFT:
                        snake.direction = (
                            Directions.LEFT
                            if snake.direction != Directions.RIGHT
                            else snake.direction
                        )
                        can_turn = False
        clock.tick(60)
        pygame.display.update()


if __name__ == "__main__":
    main()
