import pygame
from enum import Enum
import random
import os

from pygame.constants import K_DOWN, K_LEFT, K_RIGHT, K_UP

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


class Directions(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class Cell:
    def __init__(self, coords: tuple[int, int], grid, isDark: bool):
        self.coords = coords
        self.isDark = isDark
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

    def __init__(self, coords: tuple[int, int], grid, isDark: bool, isHead: bool):
        super().__init__(coords, grid, isDark)
        self.isHead = isHead
        self.surface: pygame.Surface = SNAKE_STRAIGHT


class Apple(Cell):
    TYPE = 3


class Grid(list):
    def __init__(self, size: int):
        self.width = size
        self.height = size
        for i in range(self.height):
            self.append([])
            for j in range(self.width):
                isDark = (j % 2 + i % 2) % 2 == 0
                self[-1].append(Empty((j, i), self, isDark))

    def build_walls(self):
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
        self[apple_coords[1]][apple_coords[0]] = Apple(
            apple_coords, self, self[apple_coords[1]][apple_coords[0]].isDark
        )

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
                    color = "grey" if cell.isDark else "lightGrey"
                elif cell.TYPE == Wall.TYPE:
                    color = (125, 125, 125)
                elif cell.TYPE == Body.TYPE:
                    WIN.blit(cell.surface, cell.rect)
                    continue
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
            part = Body(
                coords, grid, grid[coords[1]][coords[0]].isDark, not (i - start_pos[0])
            )
            grid[coords[1]][coords[0]] = part
            self.body_parts.append(part)
        self.head = self.grid[start_pos[1]][start_pos[0]]

    def die(self):
        global run
        print("Die!")
        print(f"You scored {score} points")
        run = False

    def angle_head(self):
        angles = {
            Directions.UP: 0,
            Directions.LEFT: 90,
            Directions.DOWN: 180,
            Directions.RIGHT: 270,
        }
        head = SNAKE_HEAD.copy()
        head = pygame.transform.rotate(head, angles[self.direction])
        self.body_parts[-1].surface = head
        self.body_parts[-2].surface = SNAKE_STRAIGHT

    def angle_turn(self):
        pass

    def move(self, turned: bool):
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
        next = self.grid[next_coords[1]][next_coords[0]]
        if next_cell_type in (
            Wall.TYPE,
            Body.TYPE,
        ):
            self.die()
        else:
            self.head.isHead = False
            self.head = Body(next_coords, self.grid, next.isDark, True)
            self.grid[next_coords[1]][next_coords[0]] = self.head
            self.body_parts.append(self.head)
            self.angle_head()
        if next_cell_type == Empty.TYPE:
            self.grid[tail_coords[1]][tail_coords[0]] = Empty(
                (tail_coords[0], tail_coords[1]),
                self.grid,
                self.grid[tail_coords[1]][tail_coords[0]].isDark,
            )
            self.body_parts.pop(0)
        else:
            global score
            score += 1
            self.grid.spawn_apple()


def main():
    global run
    opposite_directions = {
        Directions.UP: Directions.DOWN,
        Directions.DOWN: Directions.UP,
        Directions.LEFT: Directions.RIGHT,
        Directions.RIGHT: Directions.LEFT,
    }
    grid = Grid(20)
    grid.build_walls()
    grid.spawn_apple()
    snake = Snake((4, 2), score, grid)
    clock = pygame.time.Clock()
    frame = 0
    can_turn = True
    turned = False
    while run:
        grid.draw()
        if frame == 10:
            frame = 0
            snake.move(turned)
            can_turn = True
            turned = False
        frame += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if can_turn:
                    if event.key == K_UP:
                        if snake.direction != opposite_directions[Directions.UP]:
                            snake.direction = Directions.UP
                            can_turn = False
                            turned = True
                    if event.key == K_RIGHT:
                        if snake.direction != opposite_directions[Directions.RIGHT]:
                            snake.direction = Directions.RIGHT
                            can_turn = False
                            turned = True
                    if event.key == K_DOWN:
                        if snake.direction != opposite_directions[Directions.DOWN]:
                            snake.direction = Directions.DOWN
                            can_turn = False
                            turned = True
                    if event.key == K_LEFT:
                        if snake.direction != opposite_directions[Directions.LEFT]:
                            snake.direction = Directions.LEFT
                            can_turn = False
                            turned = True
        clock.tick(60)
        pygame.display.update()


if __name__ == "__main__":
    main()
