import pygame, random, sys

pygame.init()

CELL, COLS, ROWS = 20, 30, 20
W, H = COLS * CELL, ROWS * CELL
screen = pygame.display.set_mode((W, H + 40))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 24, bold=True)

def new_food(snake):
    while True:
        pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
        if pos not in snake:
            return pos

def draw(snake, food, score, speed):
    screen.fill((20, 20, 20))
    # Grid
    for x in range(COLS):
        for y in range(ROWS):
            pygame.draw.rect(screen, (40, 40, 40), (x*CELL, y*CELL+40, CELL, CELL), 1)
    # Food
    fx, fy = food
    pygame.draw.rect(screen, (220, 50, 50), (fx*CELL+2, fy*CELL+42, CELL-4, CELL-4), border_radius=4)
    # Snake
    for i, (x, y) in enumerate(snake):
        green = 200 if i == 0 else 120
        pygame.draw.rect(screen, (50, green, 50), (x*CELL+2, y*CELL+42, CELL-4, CELL-4), border_radius=4)
    # HUD
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, W, 40))
    screen.blit(font.render(f"Score: {score}   Speed: {speed}", True, (255, 255, 255)), (10, 8))
    pygame.display.flip()

def main():
    snake = [(COLS//2, ROWS//2), (COLS//2-1, ROWS//2), (COLS//2-2, ROWS//2)]
    direction = (1, 0)
    food = new_food(snake)
    score, speed = 0, 8
    grow = False

    DIRS = {
        pygame.K_UP: (0,-1), pygame.K_w: (0,-1),
        pygame.K_DOWN: (0,1), pygame.K_s: (0,1),
        pygame.K_LEFT: (-1,0), pygame.K_a: (-1,0),
        pygame.K_RIGHT: (1,0), pygame.K_d: (1,0),
    }

    while True:
        clock.tick(speed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                nd = DIRS.get(event.key)
                if nd and (nd[0] + direction[0], nd[1] + direction[1]) != (0, 0):
                    direction = nd

        hx, hy = snake[0]
        nx, ny = (hx + direction[0]) % COLS, (hy + direction[1]) % ROWS
        if (nx, ny) in snake:
            # Game over — wait for restart
            screen.blit(font.render("GAME OVER  R=restart", True, (255, 80, 80)),
                        (W//2 - 140, H//2))
            pygame.display.flip()
            while True:
                e = pygame.event.wait()
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                    main(); return

        snake.insert(0, (nx, ny))
        if (nx, ny) == food:
            score += 10
            speed = 8 + score // 50
            food = new_food(snake)
        else:
            snake.pop()

        draw(snake, food, score, speed)

main()
