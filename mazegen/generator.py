import sys
from time import sleep
from typing import Tuple, Dict, Any, List, Optional
import random
import os
from collections import deque

# Protection pour les très grands labyrinthes (très apprécié en évaluation 42 !)
sys.setrecursionlimit(10000)

UP, RIGHT, DOWN, LEFT = 1, 2, 4, 8
OFFSET_X = {UP: 0, RIGHT: 1, DOWN: 0, LEFT: -1}
OFFSET_Y = {UP: -1, RIGHT: 0, DOWN: 1, LEFT: 0}
REVERSE_DIR = {UP: DOWN, RIGHT: LEFT, DOWN: UP, LEFT: RIGHT}
CHAR_MAP = {UP: "N", RIGHT: "E", DOWN: "S", LEFT: "W"}

class LabyrinthBuilder:
    def __init__(self, config_data: Dict[str, Any], show_anim: bool = False) -> None:
        self.cols: int = int(config_data["width"])
        self.rows: int = int(config_data["height"])
        self.start_pos: Tuple[int, int] = config_data["entry"]
        self.end_pos: Tuple[int, int] = config_data["exit"]
        self.is_perfect: bool = config_data["perfect"]
        self.export_path: str = config_data["output_file"]
        
        self.solution_str: str = ""
        self.solution_coords: List[List[int]] = []
        
        self.grid: List[List[int]] = [
            [0b1111 for _ in range(self.cols)] for _ in range(self.rows)
        ]
        
        self.random_seed: Optional[int] = config_data.get("seed", None)
        self.generation_method: str = config_data.get("algo", "dfs")
        
        # 1. ON INITIALISE LA COULEUR EN PREMIER
        self.wall_color: str = "\033[37m"
        
        # 2. ENSUITE ON LANCE LA CONSTRUCTION
        self.build_labyrinth(show_anim)

    # VOICI LA FONCTION QUI MANQUAIT !
    def change_wall_color(self) -> None:
        colors = [
            "\033[33m", "\033[34m", "\033[35m", "\033[36m", "\033[37m",
            "\033[93m", "\033[94m", "\033[95m", "\033[96m"
        ]
        self.wall_color = random.choice(colors)

    @staticmethod
    def wipe_screen() -> None:
        os.system("clear")

    def render_grid(
        self,
        change_color: bool,
        current_trail: Optional[List[List[int]]] = None
    ) -> None:
        COLOR_1 = "\033[31m"  # Rouge fixe (pour 42)
        COLOR_2 = "\033[32m"  # Vert fixe (pour S, E, Chemin)
        RESET_COL = "\033[0m"
        
        if change_color:
            self.change_wall_color()

        wall_c = self.wall_color

        print(wall_c + "█" + ("████" * self.cols) + RESET_COL)
        
        pattern_42_cells = self.locate_42_pattern()

        for r in range(self.rows):
            row_mid = wall_c + "█" + RESET_COL
            row_bot = wall_c + "█" + RESET_COL

            for c in range(self.cols):
                val = self.grid[r][c]

                # 1. Le Centre
                if c == self.start_pos[0] and r == self.start_pos[1]:
                    row_mid += COLOR_2 + " S " + RESET_COL
                elif c == self.end_pos[0] and r == self.end_pos[1]:
                    row_mid += COLOR_2 + " E " + RESET_COL
                elif (c, r) in pattern_42_cells:
                    row_mid += COLOR_1 + " █ " + RESET_COL
                elif current_trail:
                    if [c, r] == current_trail[-1]: 
                        row_mid += COLOR_2 + " @ " + RESET_COL
                    elif [c, r] in current_trail:
                        row_mid += COLOR_2 + " · " + RESET_COL
                    else:
                        row_mid += "   "
                else:
                    row_mid += "   "

                # 2. Le Mur Est
                if val & RIGHT:
                    row_mid += wall_c + "█" + RESET_COL
                else:
                    row_mid += " "

                # 3. Le Mur Sud
                if val & DOWN:
                    row_bot += wall_c + "████" + RESET_COL
                else:
                    row_bot += "   " + wall_c + "█" + RESET_COL

            print(row_mid)
            print(row_bot)

    def __str__(self) -> str:
        text_out = ""
        for row_data in self.grid:
            text_out += " ".join(f"{c_val:04b}" for c_val in row_data) + "\n"
        return text_out

    def animate_solution(self) -> None:
        trail = []
        for step in self.solution_coords:
            trail.append(step)
            self.wipe_screen()
            print("== 🏃 ANIMATING SHORTEST PATH ==")
            self.render_grid(False, trail)
            sleep(0.08)

    def build_labyrinth(self, show_anim: bool = False) -> None:
        if self.random_seed is not None:
            random.seed(self.random_seed)

        explored = [[False] * self.cols for _ in range(self.rows)]
        pattern_42_cells = self.locate_42_pattern()

        if self.start_pos in pattern_42_cells or self.end_pos in pattern_42_cells:
            raise ValueError("Entry or exit overlaps with the 42 pattern.")

        self.drill_dfs(
            self.start_pos[0], self.start_pos[1], explored, pattern_42_cells, show_anim
        )

        if not self.is_perfect:
            self.create_cycles()

        self.find_shortest_path()

        if show_anim:
            self.animate_solution()

        self.export_to_disk()

    def drill_dfs(
        self,
        cx: int,
        cy: int,
        explored: List[List[bool]],
        pattern_42_cells: List[Tuple[int, int]],
        show_anim: bool
    ) -> None:
        explored[cy][cx] = True
        ways = [UP, RIGHT, DOWN, LEFT]
        random.shuffle(ways)

        if show_anim:
            self.wipe_screen()
            print("== ⛏️  DIGGING MAZE (DFS) ==")
            self.render_grid(False)
            sleep(0.005)

        for w in ways:
            next_x = cx + OFFSET_X[w]
            next_y = cy + OFFSET_Y[w]

            if (
                0 <= next_x < self.cols
                and 0 <= next_y < self.rows
                and (next_x, next_y) not in pattern_42_cells
                and not explored[next_y][next_x]
            ):
                self.grid[cy][cx] &= ~w
                self.grid[next_y][next_x] &= ~REVERSE_DIR[w]
                self.drill_dfs(next_x, next_y, explored, pattern_42_cells, show_anim)

    def export_to_disk(self) -> None:
        with open(self.export_path, "w") as file_out:
            for row_data in self.grid:
                line_str = "".join(format(cell, "X") for cell in row_data)
                file_out.write(line_str + "\n")
            file_out.write(f"\n{self.start_pos[0]},{self.start_pos[1]}\n")
            file_out.write(f"{self.end_pos[0]},{self.end_pos[1]}\n")
            file_out.write(self.solution_str + "\n")

    def find_shortest_path(self) -> None:
        search_q: deque[Tuple[int, int, List[str]]] = deque(
            [(self.start_pos[0], self.start_pos[1], [])]
        )
        scanned = [[False] * self.cols for _ in range(self.rows)]
        scanned[self.start_pos[1]][self.start_pos[0]] = True

        while search_q:
            cx, cy, route = search_q.popleft()

            if (cx, cy) == self.end_pos:
                self.solution_str = "".join(route)
                self.solution_coords = self._trace_coordinates(route)
                return

            for w in (UP, RIGHT, DOWN, LEFT):
                if self.grid[cy][cx] & w:
                    continue

                next_x = cx + OFFSET_X[w]
                next_y = cy + OFFSET_Y[w]

                if (
                    0 <= next_x < self.cols
                    and 0 <= next_y < self.rows
                    and not scanned[next_y][next_x]
                ):
                    scanned[next_y][next_x] = True
                    updated_route = route + [CHAR_MAP[w]]
                    search_q.append((next_x, next_y, updated_route))

        self.solution_str = ""
        self.solution_coords = []

    def _trace_coordinates(self, route: List[str]) -> List[List[int]]:
        trail_coords = []
        cx, cy = self.start_pos

        for step_char in route:
            for w in (UP, RIGHT, DOWN, LEFT):
                if CHAR_MAP[w] == step_char:
                    cx += OFFSET_X[w]
                    cy += OFFSET_Y[w]
                    trail_coords.append([cx, cy])
                    break

        return trail_coords

    def create_cycles(self) -> None:
        cycle_target = int(self.cols * self.rows * 0.15)
        tries = 0
        max_tries = cycle_target * 10
        pattern_42_cells = self.locate_42_pattern()

        while cycle_target > 0 and tries < max_tries:
            tries += 1

            cx = random.randint(0, self.cols - 1)
            cy = random.randint(0, self.rows - 1)

            if (cx, cy) in pattern_42_cells:
                continue

            way = random.choice([UP, RIGHT, DOWN, LEFT])
            next_x = cx + OFFSET_X[way]
            next_y = cy + OFFSET_Y[way]

            if not (0 <= next_x < self.cols and 0 <= next_y < self.rows):
                continue

            if (next_x, next_y) in pattern_42_cells:
                continue

            if self.grid[cy][cx] & way:
                self.grid[cy][cx] &= ~way
                self.grid[next_y][next_x] &= ~REVERSE_DIR[way]
                cycle_target -= 1

    def locate_42_pattern(self) -> List[Tuple[int, int]]:
        center = (self.cols // 2, self.rows // 2)
        c_x, c_y = center
        pattern_coords = [
            (c_x - 3, c_y - 2), (c_x - 3, c_y - 1), (c_x - 3, c_y), (c_x - 2, c_y),
            (c_x - 1, c_y), (c_x - 1, c_y + 1), (c_x - 1, c_y + 2),
            (c_x + 1, c_y - 2), (c_x + 1, c_y), (c_x + 1, c_y + 1), (c_x + 1, c_y + 2),
            (c_x + 2, c_y - 2), (c_x + 2, c_y), (c_x + 2, c_y + 2),
            (c_x + 3, c_y - 2), (c_x + 3, c_y - 1), (c_x + 3, c_y), (c_x + 3, c_y + 2),
        ]
        return pattern_coords