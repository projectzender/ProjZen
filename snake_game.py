import pygame
import random
import sys
from enum import Enum
from collections import deque

pygame.init()

# Constants
CELL = 20
COLS = 32
ROWS = 24
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
HUD_H = 60
SCREEN_W = WIDTH
SCREEN_H = HEIGHT + HUD_H

FPS_BASE = 8

# Colors
BLACK    = (0,   0,   0)
WHITE    = (255, 255, 255)
GREEN    = (50,  205, 50)
D_GREEN  = (0,   140, 0)
RED      = (220, 20,  20)
YELLOW   = (255, 215, 0)
CYAN     = (0,   200, 220)
PURPLE   = (160, 32,  240)
ORANGE   = (255, 140, 0)
GRAY     = (60,  60,  60)
D_GRAY   = (30,  30,  30)
BLUE     = (30,  144, 255)

class Dir(Enum):
    UP    = (0, -1)
    DOWN  = (0,  1)
    LEFT  = (-1, 0)
    RIGHT = (1,  0)

OPPOSITE = {Dir.UP: Dir.DOWN, Dir.DOWN: Dir.UP, Dir.LEFT: Dir.RIGHT, Dir.RIGHT: Dir.LEFT}

class ItemType(Enum):
    FOOD    = "food"
    BONUS   = "bonus"
    SHRINK  = "shrink"
    SPEED   = "speed"
    WALL    = "wall"

ITEM_CFG = {
    ItemType.FOOD:   {"color": RED,    "points": 10,  "symbol": "●", "duration": None},
    ItemType.BONUS:  {"color": YELLOW, "points": 30,  "symbol": "★", "duration": 8},
    ItemType.SHRINK: {"color": CYAN,   "points": 20,  "symbol": "◆", "duration": 10},
    ItemType.SPEED:  {"color": ORANGE, "points": 15,  "symbol": "⚡", "duration": 12},
    ItemType.WALL:   {"color": PURPLE, "points": 0,   "symbol": "■", "duration": 15},
}

class Item:
    def __init__(self, pos, kind, timer=None):
        self.pos = pos
        self.kind = kind
        self.timer = timer
        self.age = 0

    def tick(self, dt):
        if self.timer is not None:
            self.age += dt
            return self.age >= self.timer
        return False

class Snake:
    def __init__(self):
        cx, cy = COLS // 2, ROWS // 2
        self.body = deque([(cx, cy), (cx - 1, cy), (cx - 2, cy)])
        self.direction = Dir.RIGHT
        self.queued_dir = Dir.RIGHT
        self.grow_pending = 0
        self.alive = True

    def set_dir(self, d):
        if d != OPPOSITE.get(self.direction):
            self.queued_dir = d

    def step(self, walls):
        self.direction = self.queued_dir
        dx, dy = self.direction.value
        hx, hy = self.body[0]
        nx, ny = (hx + dx) % COLS, (hy + dy) % ROWS

        if (nx, ny) in walls:
            self.alive = False
            return None

        if (nx, ny) in list(self.body)[:-1]:
            self.alive = False
            return None

        tail = self.body[-1]
        self.body.appendleft((nx, ny))
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
        return tail

    def shrink(self, n=3):
        for _ in range(min(n, len(self.body) - 1)):
            self.body.pop()

    @property
    def head(self):
        return self.body[0]

    def occupies(self, pos):
        return pos in self.body


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Snake — Complex Edition")
        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("monospace", 32, bold=True)
        self.font_md = pygame.font.SysFont("monospace", 20, bold=True)
        self.font_sm = pygame.font.SysFont("monospace", 14)
        self.reset()

    def reset(self):
        self.snake = Snake()
        self.items = []
        self.walls = set()
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.speed_boost = False
        self.speed_timer = 0.0
        self.step_acc = 0.0
        self.paused = False
        self.game_over = False
        self.flash = []          # [(text, color, ttl)]
        self._spawn_food()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _free_pos(self):
        occupied = set(self.snake.body) | self.walls | {i.pos for i in self.items}
        choices = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in occupied]
        return random.choice(choices) if choices else None

    def _spawn_food(self):
        pos = self._free_pos()
        if pos:
            self.items.append(Item(pos, ItemType.FOOD))

    def _maybe_spawn_special(self):
        counts = {k: 0 for k in ItemType}
        for it in self.items:
            counts[it.kind] += 1

        if counts[ItemType.BONUS] == 0 and random.random() < 0.25:
            pos = self._free_pos()
            if pos:
                self.items.append(Item(pos, ItemType.BONUS, timer=ITEM_CFG[ItemType.BONUS]["duration"]))

        if counts[ItemType.SHRINK] == 0 and len(self.snake.body) > 6 and random.random() < 0.15:
            pos = self._free_pos()
            if pos:
                self.items.append(Item(pos, ItemType.SHRINK, timer=ITEM_CFG[ItemType.SHRINK]["duration"]))

        if counts[ItemType.SPEED] == 0 and random.random() < 0.2:
            pos = self._free_pos()
            if pos:
                self.items.append(Item(pos, ItemType.SPEED, timer=ITEM_CFG[ItemType.SPEED]["duration"]))

        if self.level >= 3 and counts[ItemType.WALL] == 0 and random.random() < 0.12:
            pos = self._free_pos()
            if pos:
                self.items.append(Item(pos, ItemType.WALL, timer=ITEM_CFG[ItemType.WALL]["duration"]))

    def _apply_item(self, item):
        k = item.kind
        pts = ITEM_CFG[k]["points"] * self.level
        self.score += pts
        color = ITEM_CFG[k]["color"]

        if k == ItemType.FOOD:
            self.snake.grow_pending += 1
            self.food_eaten += 1
            self._flash(f"+{pts}", color)
            if self.food_eaten % 5 == 0:
                self._level_up()
            self._maybe_spawn_special()
            self._spawn_food()

        elif k == ItemType.BONUS:
            self.snake.grow_pending += 2
            self._flash(f"BONUS +{pts}!", color)

        elif k == ItemType.SHRINK:
            self.snake.shrink(3)
            self._flash(f"SHRINK +{pts}", color)

        elif k == ItemType.SPEED:
            self.speed_boost = True
            self.speed_timer = 5.0
            self._flash(f"SPEED! +{pts}", color)

        elif k == ItemType.WALL:
            self.walls.add(item.pos)
            self._flash("WALL PLACED!", color)

    def _level_up(self):
        self.level += 1
        self._flash(f"LEVEL {self.level}!", WHITE)

    def _flash(self, text, color):
        self.flash.append([text, color, 1.5])

    # ── step ─────────────────────────────────────────────────────────────────

    def _fps(self):
        return FPS_BASE + (self.level - 1) * 1.5 + (4 if self.speed_boost else 0)

    def tick(self, dt):
        if self.paused or self.game_over:
            return

        # Speed boost timer
        if self.speed_boost:
            self.speed_timer -= dt
            if self.speed_timer <= 0:
                self.speed_boost = False

        # Expire timed items
        expired = []
        for it in self.items:
            if it.tick(dt):
                expired.append(it)
        for it in expired:
            self.items.remove(it)
            if it.kind == ItemType.WALL and it.pos in self.walls:
                self.walls.discard(it.pos)

        # Flash timers
        self.flash = [[t, c, ttl - dt] for t, c, ttl in self.flash if ttl - dt > 0]

        # Move snake on interval
        step_interval = 1.0 / self._fps()
        self.step_acc += dt
        while self.step_acc >= step_interval:
            self.step_acc -= step_interval
            self._move_snake()
            if self.game_over:
                break

    def _move_snake(self):
        self.snake.step(self.walls)
        if not self.snake.alive:
            self.game_over = True
            return

        head = self.snake.head
        hit = [it for it in self.items if it.pos == head]
        for it in hit:
            self.items.remove(it)
            self._apply_item(it)

    # ── draw ─────────────────────────────────────────────────────────────────

    def _cell_rect(self, x, y):
        return pygame.Rect(x * CELL, y * CELL + HUD_H, CELL, CELL)

    def draw(self):
        self.screen.fill(D_GRAY)

        # Grid
        for x in range(COLS):
            for y in range(ROWS):
                r = self._cell_rect(x, y)
                pygame.draw.rect(self.screen, GRAY, r, 1)

        # Walls
        for wx, wy in self.walls:
            r = self._cell_rect(wx, wy)
            pygame.draw.rect(self.screen, PURPLE, r)
            pygame.draw.rect(self.screen, WHITE, r, 1)

        # Items
        for it in self.items:
            cfg = ITEM_CFG[it.kind]
            r = self._cell_rect(*it.pos)
            pygame.draw.rect(self.screen, cfg["color"], r.inflate(-2, -2))
            pygame.draw.rect(self.screen, WHITE, r.inflate(-2, -2), 1)
            # Pulsing outline for timed items
            if it.timer is not None:
                ratio = 1 - it.age / it.timer
                alpha_r = r.inflate(int(4 * ratio), int(4 * ratio))
                pygame.draw.rect(self.screen, cfg["color"], alpha_r, 2)

        # Snake
        body = list(self.snake.body)
        for i, (bx, by) in enumerate(body):
            r = self._cell_rect(bx, by)
            if i == 0:
                color = WHITE
            else:
                t = i / max(len(body) - 1, 1)
                color = (int(D_GREEN[0] + (GREEN[0] - D_GREEN[0]) * (1 - t)),
                         int(D_GREEN[1] + (GREEN[1] - D_GREEN[1]) * (1 - t)),
                         int(D_GREEN[2] + (GREEN[2] - D_GREEN[2]) * (1 - t)))
            pygame.draw.rect(self.screen, color, r.inflate(-2, -2), border_radius=4)

        # HUD
        hud = pygame.Rect(0, 0, SCREEN_W, HUD_H)
        pygame.draw.rect(self.screen, BLACK, hud)
        pygame.draw.line(self.screen, GRAY, (0, HUD_H), (SCREEN_W, HUD_H), 2)

        score_surf = self.font_lg.render(f"Score: {self.score}", True, WHITE)
        level_surf = self.font_md.render(f"Lvl {self.level}", True, YELLOW)
        len_surf   = self.font_md.render(f"Len {len(self.snake.body)}", True, GREEN)
        boost_surf = self.font_md.render("SPEED!", True, ORANGE) if self.speed_boost else None

        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(level_surf, (SCREEN_W - 120, 8))
        self.screen.blit(len_surf,   (SCREEN_W - 120, 32))
        if boost_surf:
            self.screen.blit(boost_surf, (SCREEN_W // 2 - boost_surf.get_width() // 2, 18))

        # Flash messages
        for i, (text, color, ttl) in enumerate(reversed(self.flash[-5:])):
            surf = self.font_md.render(text, True, color)
            self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2,
                                    HUD_H + 8 + i * 22))

        # Overlays
        if self.paused:
            self._overlay("PAUSED", "P to resume")
        if self.game_over:
            self._overlay("GAME OVER", f"Score: {self.score}   R to restart")

        pygame.display.flip()

    def _overlay(self, title, sub):
        surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 160))
        self.screen.blit(surf, (0, 0))
        t = self.font_lg.render(title, True, WHITE)
        s = self.font_md.render(sub, True, YELLOW)
        self.screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, SCREEN_H // 2 - 30))
        self.screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2, SCREEN_H // 2 + 10))

    # ── main loop ────────────────────────────────────────────────────────────

    def run(self):
        DIR_KEYS = {
            pygame.K_UP: Dir.UP, pygame.K_w: Dir.UP,
            pygame.K_DOWN: Dir.DOWN, pygame.K_s: Dir.DOWN,
            pygame.K_LEFT: Dir.LEFT, pygame.K_a: Dir.LEFT,
            pygame.K_RIGHT: Dir.RIGHT, pygame.K_d: Dir.RIGHT,
        }
        while True:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in DIR_KEYS:
                        self.snake.set_dir(DIR_KEYS[event.key])
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            self.tick(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
