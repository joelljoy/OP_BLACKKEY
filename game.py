import pygame
import sys
from enum import Enum
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
GRID_SIZE = 40
FPS = 60

# Colors (Neon Cyber Theme)
BLACK = (5, 5, 15)
DARK_BLUE = (10, 15, 35)
NEON_BLUE = (0, 200, 255)
NEON_CYAN = (0, 255, 255)
NEON_RED = (255, 50, 50)
NEON_YELLOW = (255, 255, 0)
NEON_GREEN = (0, 255, 100)
NEON_ORANGE = (255, 140, 0)
WHITE = (255, 255, 255)


class CellType(Enum):
    EMPTY = 0
    WALL = 1
    PATH = 2
    GATE = 3
    POWER_NODE = 4
    BULB_NODE = 5
    EXIT = 8


class Entity:
    def __init__(self, x, y, color, size=15):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.glow_offset = 0

    def draw(self, screen, offset_x, offset_y):
        screen_x = self.x * GRID_SIZE + offset_x + GRID_SIZE // 2
        screen_y = self.y * GRID_SIZE + offset_y + GRID_SIZE // 2

        # Draw glow effect
        glow_size = self.size + abs(int(self.glow_offset))
        glow_color = tuple(max(0, c - 100) for c in self.color)
        pygame.draw.circle(screen, glow_color, (screen_x, screen_y), glow_size)
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)

        # Update glow animation
        self.glow_offset = (self.glow_offset + 0.3) % 10 - 5


class Virus(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, NEON_RED, 12)
        self.active = False
        self.path = []
        self.move_cooldown = 0
        self.move_delay = 18  # Slightly slower for better balance

    def activate(self):
        self.active = True

    def find_path_to_player(self, player_x, player_y, grid, gates):
        if not self.active:
            return

        queue = deque([(self.x, self.y, [])])
        visited = {(self.x, self.y)}

        while queue:
            x, y, path = queue.popleft()

            if x == player_x and y == player_y:
                self.path = path
                return

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy

                if not (0 <= nx < len(grid[0]) and 0 <= ny < len(grid)):
                    continue
                if (nx, ny) in visited:
                    continue

                cell = grid[ny][nx]
                is_walkable = False

                # FIX: Virus can walk on everything except Walls and Closed Gates
                if cell != CellType.WALL and cell != CellType.EMPTY:
                    if cell == CellType.GATE:
                        # Only walkable if open
                        for gate in gates:
                            if gate["x"] == nx and gate["y"] == ny and gate["open"]:
                                is_walkable = True
                                break
                    else:
                        is_walkable = True

                if is_walkable:
                    visited.add((nx, ny))
                    queue.append((nx, ny, path + [(nx, ny)]))

        self.path = []

    def move(self, grid, gates):
        if not self.active or not self.path:
            return

        self.move_cooldown += 1
        if self.move_cooldown >= self.move_delay:
            self.move_cooldown = 0
            if self.path:
                next_pos = self.path.pop(0)
                self.x, self.y = next_pos


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("HACKING PROTOCOL - FINAL FIX")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 18)

        self.current_level = 0
        self.levels = self.create_levels()
        self.load_level(self.current_level)

    def create_levels(self):
        # Level 1: Tutorial
        level1 = {
            "name": "LEVEL 1: INITIALIZATION",
            "grid": [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 2, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 8, 1],
                [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 4, 1, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
            ],
            "player_start": (1, 1),
            "viruses": [],
            "gates": [{"x": 11, "y": 3, "open": False, "link_id": 1}],
            "power_nodes": [{"x": 5, "y": 5}],
            "bulb_nodes": [{"x": 8, "y": 3, "link_id": 1}],
        }

        # Level 2: Split Stream
        level2 = {
            "name": "LEVEL 2: SPLIT STREAM",
            "grid": [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 4, 2, 2, 2, 1, 2, 2, 2, 2, 2, 5, 1, 0, 1],
                [1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 0, 1],
                [1, 0, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 1, 1, 1, 3, 1, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 4, 1, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 8, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ],
            "player_start": (6, 3),
            "viruses": [(12, 6)],
            "gates": [{"x": 6, "y": 4, "open": False, "link_id": 1}],
            "power_nodes": [{"x": 1, "y": 1}, {"x": 6, "y": 5}],
            "bulb_nodes": [{"x": 11, "y": 1, "link_id": 1}],
        }

        # Level 3: FIXED - S-Shape Snake Layout
        # No more isolated islands. One continuous winding path.
        level3 = {
            "name": "LEVEL 3: THE SNAKE",
            "grid": [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [
                    1,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    4,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    5,
                    1,
                    0,
                    1,
                ],  # Top: Start -> Right. Power(7,1). Bulb(15,1).
                [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 0, 1],
                [
                    1,
                    2,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    3,
                    1,
                    0,
                    1,
                ],  # Gate 1 at (15,3)
                [1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 1],
                [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 0, 1],
                [
                    1,
                    5,
                    2,
                    2,
                    2,
                    2,
                    2,
                    4,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    1,
                    0,
                    1,
                ],  # Middle: Left <- Right. Bulb(1,6). Power(7,6).
                [1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                [
                    1,
                    0,
                    0,
                    3,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                ],  # Gate 2 at (3,8)
                [1, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [
                    1,
                    0,
                    0,
                    2,
                    2,
                    2,
                    4,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    8,
                    1,
                    1,
                ],  # Bottom: Left -> Right. Power(6,11). Exit.
                [1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ],
            "player_start": (1, 1),
            "viruses": [
                (14, 6),  # Patrols Middle Lane
                (10, 11),  # Patrols Bottom Lane
            ],
            "gates": [
                {"x": 15, "y": 3, "open": False, "link_id": 1},
                {"x": 3, "y": 8, "open": False, "link_id": 2},
            ],
            # 3 Power nodes for 2 gates. One extra for safety.
            "power_nodes": [
                {"x": 7, "y": 1},  # Top (For Gate 1)
                {"x": 7, "y": 6},  # Middle (For combat or Gate 2)
                {"x": 6, "y": 11},  # Bottom (Safety/Combat)
            ],
            "bulb_nodes": [
                {"x": 15, "y": 1, "link_id": 1},  # Opens Gate 1 (Top Right)
                {"x": 1, "y": 6, "link_id": 2},  # Opens Gate 2 (Middle Left)
            ],
        }

        return [level1, level2, level3]

    def load_level(self, level_index):
        level = self.levels[level_index]
        self.grid = []
        for y, row in enumerate(level["grid"]):
            grid_row = []
            for x, val in enumerate(row):
                if val == 0:
                    cell = CellType.EMPTY
                elif val == 1:
                    cell = CellType.WALL
                elif val == 2:
                    cell = CellType.PATH
                elif val == 3:
                    cell = CellType.GATE
                elif val == 4:
                    cell = CellType.POWER_NODE
                elif val == 5:
                    cell = CellType.BULB_NODE
                elif val == 8:
                    cell = CellType.EXIT
                else:
                    cell = CellType.PATH
                grid_row.append(cell)
            self.grid.append(grid_row)

        px, py = level["player_start"]
        self.player = Entity(px, py, NEON_CYAN, 15)
        self.player_has_power = False
        self.viruses = [Virus(vx, vy) for vx, vy in level["viruses"]]
        self.gates = [g.copy() for g in level["gates"]]
        self.power_nodes = [p.copy() for p in level["power_nodes"]]
        self.bulb_nodes = [b.copy() for b in level["bulb_nodes"]]
        self.level_name = level["name"]
        self.level_complete = False
        self.game_over = False
        self.message = ""
        self.message_timer = 0

    def show_message(self, text, duration=120):
        self.message = text
        self.message_timer = duration

    def check_virus_collision(self):
        # iterate over a COPY to avoid index errors
        for virus in self.viruses[:]:
            if virus.x == self.player.x and virus.y == self.player.y:
                if self.player_has_power:
                    self.viruses.remove(virus)
                    self.player_has_power = False
                    self.player.color = NEON_CYAN
                    self.show_message("ANTIVIRUS DESTROYED", 90)
                else:
                    self.game_over = True
                    self.show_message("SYSTEM COMPROMISED", 240)

    def move_player(self, dx, dy):
        if self.level_complete or self.game_over:
            return

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if (
            new_x < 0
            or new_x >= len(self.grid[0])
            or new_y < 0
            or new_y >= len(self.grid)
        ):
            return

        cell = self.grid[new_y][new_x]

        if cell == CellType.EMPTY or cell == CellType.WALL:
            return

        for gate in self.gates:
            if gate["x"] == new_x and gate["y"] == new_y and not gate["open"]:
                self.show_message("GATE LOCKED - FIND SWITCH", 60)
                return

        self.player.x = new_x
        self.player.y = new_y

        # Handle Power
        for node in self.power_nodes[:]:
            if node["x"] == new_x and node["y"] == new_y:
                self.player_has_power = True
                self.power_nodes.remove(node)
                self.player.color = NEON_YELLOW
                self.show_message("POWER ACQUIRED", 90)
                for virus in self.viruses:
                    virus.activate()

        # Handle Bulbs
        for bulb in self.bulb_nodes:
            if bulb["x"] == new_x and bulb["y"] == new_y:
                if self.player_has_power:
                    gate_opened = False
                    for gate in self.gates:
                        if gate["link_id"] == bulb["link_id"] and not gate["open"]:
                            gate["open"] = True
                            gate_opened = True

                    if gate_opened:
                        self.player_has_power = False
                        self.player.color = NEON_CYAN
                        self.show_message("GATE UNLOCKED - POWER CONSUMED", 90)
                    elif any(
                        g["link_id"] == bulb["link_id"] and g["open"]
                        for g in self.gates
                    ):
                        pass
                else:
                    linked_gate_closed = False
                    for gate in self.gates:
                        if gate["link_id"] == bulb["link_id"] and not gate["open"]:
                            linked_gate_closed = True
                    if linked_gate_closed:
                        self.show_message("NEEDS POWER TO ACTIVATE", 60)

        if cell == CellType.EXIT:
            self.level_complete = True
            self.show_message("SYSTEM BREACHED!", 180)

        self.check_virus_collision()

    def update(self):
        for virus in self.viruses[:]:
            if virus.active:
                virus.find_path_to_player(
                    self.player.x, self.player.y, self.grid, self.gates
                )
                virus.move(self.grid, self.gates)
                self.check_virus_collision()

    def draw_grid(self):
        offset_x = (SCREEN_WIDTH - len(self.grid[0]) * GRID_SIZE) // 2
        offset_y = 80

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                screen_x = x * GRID_SIZE + offset_x
                screen_y = y * GRID_SIZE + offset_y

                if cell != CellType.EMPTY and cell != CellType.WALL:
                    center_x = screen_x + GRID_SIZE // 2
                    center_y = screen_y + GRID_SIZE // 2
                    pygame.draw.rect(
                        self.screen, NEON_BLUE, (center_x - 2, center_y - 2, 4, 4)
                    )
                    for dx, dy in [(0, 1), (1, 0)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < len(row) and 0 <= ny < len(self.grid):
                            if self.grid[ny][nx] not in [CellType.EMPTY, CellType.WALL]:
                                pygame.draw.line(
                                    self.screen,
                                    NEON_BLUE,
                                    (center_x, center_y),
                                    (
                                        center_x + dx * GRID_SIZE,
                                        center_y + dy * GRID_SIZE,
                                    ),
                                    1,
                                )

                if cell == CellType.EXIT:
                    pygame.draw.circle(
                        self.screen,
                        NEON_GREEN,
                        (screen_x + GRID_SIZE // 2, screen_y + GRID_SIZE // 2),
                        18,
                    )
                    pygame.draw.circle(
                        self.screen,
                        BLACK,
                        (screen_x + GRID_SIZE // 2, screen_y + GRID_SIZE // 2),
                        12,
                    )
                    text = self.small_font.render("EXIT", True, NEON_GREEN)
                    self.screen.blit(
                        text,
                        (screen_x + GRID_SIZE // 2 - 15, screen_y + GRID_SIZE // 2 - 6),
                    )

        for bulb in self.bulb_nodes:
            screen_x = bulb["x"] * GRID_SIZE + offset_x + GRID_SIZE // 2
            screen_y = bulb["y"] * GRID_SIZE + offset_y + GRID_SIZE // 2
            is_active = any(
                gate["link_id"] == bulb["link_id"] and gate["open"]
                for gate in self.gates
            )
            color = NEON_GREEN if is_active else NEON_ORANGE
            pygame.draw.rect(
                self.screen, color, (screen_x - 10, screen_y - 10, 20, 20), 2
            )
            id_text = self.small_font.render(str(bulb["link_id"]), True, color)
            self.screen.blit(id_text, (screen_x - 4, screen_y - 6))

        for node in self.power_nodes:
            screen_x = node["x"] * GRID_SIZE + offset_x + GRID_SIZE // 2
            screen_y = node["y"] * GRID_SIZE + offset_y + GRID_SIZE // 2
            for i in range(3):
                size = 18 - i * 5
                alpha_color = tuple(max(0, c - i * 60) for c in NEON_YELLOW)
                pygame.draw.circle(self.screen, alpha_color, (screen_x, screen_y), size)

        for gate in self.gates:
            screen_x = gate["x"] * GRID_SIZE + offset_x + GRID_SIZE // 2
            screen_y = gate["y"] * GRID_SIZE + offset_y + GRID_SIZE // 2
            color = NEON_GREEN if gate["open"] else NEON_RED
            if not gate["open"]:
                pygame.draw.rect(
                    self.screen, color, (screen_x - 16, screen_y - 16, 32, 32), 3
                )
                pygame.draw.line(
                    self.screen,
                    color,
                    (screen_x - 12, screen_y - 12),
                    (screen_x + 12, screen_y + 12),
                    3,
                )
                pygame.draw.line(
                    self.screen,
                    color,
                    (screen_x + 12, screen_y - 12),
                    (screen_x - 12, screen_y + 12),
                    3,
                )
                id_text = self.small_font.render(str(gate["link_id"]), True, WHITE)
                self.screen.blit(id_text, (screen_x - 3, screen_y - 6))
            else:
                pygame.draw.circle(self.screen, color, (screen_x, screen_y), 5)

        for virus in self.viruses:
            virus.draw(self.screen, offset_x, offset_y)
        self.player.draw(self.screen, offset_x, offset_y)

        if self.player_has_power:
            screen_x = self.player.x * GRID_SIZE + offset_x + GRID_SIZE // 2
            screen_y = self.player.y * GRID_SIZE + offset_y + GRID_SIZE // 2
            pygame.draw.circle(self.screen, NEON_YELLOW, (screen_x, screen_y), 22, 1)

    def draw_ui(self):
        title = self.large_font.render(self.level_name, True, NEON_CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(title, title_rect)

        status_y = SCREEN_HEIGHT - 80
        if self.player_has_power:
            status = self.font.render("POWER: CHARGED", True, NEON_YELLOW)
        else:
            status = self.font.render("POWER: EMPTY", True, NEON_CYAN)
        self.screen.blit(status, (20, status_y))

        controls = self.small_font.render(
            "WASD: MOVE | R: RESTART | N: NEXT LEVEL", True, WHITE
        )
        self.screen.blit(controls, (20, SCREEN_HEIGHT - 30))

        if self.message_timer > 0:
            msg = self.font.render(self.message, True, NEON_YELLOW)
            msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130))
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, DARK_BLUE, bg_rect)
            pygame.draw.rect(self.screen, NEON_CYAN, bg_rect, 2)
            self.screen.blit(msg, msg_rect)
            self.message_timer -= 1

        if self.level_complete:
            self.draw_overlay("ACCESS GRANTED", NEON_GREEN, "Press N for next level")
        if self.game_over:
            self.draw_overlay("ACCESS DENIED", NEON_RED, "Press R to restart")

    def draw_overlay(self, main_text, color, sub_text):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        text_surf = self.large_font.render(main_text, True, color)
        text_rect = text_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        )
        self.screen.blit(text_surf, text_rect)
        sub_surf = self.font.render(sub_text, True, WHITE)
        sub_rect = sub_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        )
        self.screen.blit(sub_surf, sub_rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.load_level(self.current_level)
                    elif event.key == pygame.K_n and self.level_complete:
                        if self.current_level < len(self.levels) - 1:
                            self.current_level += 1
                            self.load_level(self.current_level)
                    if not self.level_complete and not self.game_over:
                        if event.key in (pygame.K_w, pygame.K_UP):
                            self.move_player(0, -1)
                        elif event.key in (pygame.K_s, pygame.K_DOWN):
                            self.move_player(0, 1)
                        elif event.key in (pygame.K_a, pygame.K_LEFT):
                            self.move_player(-1, 0)
                        elif event.key in (pygame.K_d, pygame.K_RIGHT):
                            self.move_player(1, 0)
            self.update()
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
