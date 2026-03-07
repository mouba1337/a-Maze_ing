from time import sleep
from typing import Tuple, Dict, Any, List, Optional
import random
import os
from collections import deque

UP, RIGHT, DOWN, LEFT = 1, 2, 4, 8
OFFSET_X = {UP: 0, RIGHT: 1, DOWN: 0, LEFT: -1}
OFFSET_Y = {UP: -1, RIGHT: 0, DOWN: 1, LEFT: 0}
REVERSE_DIR = {UP: DOWN, RIGHT: LEFT, DOWN: UP, LEFT: RIGHT}
CHAR_MAP = {UP: "N", RIGHT: "E", DOWN: "S", LEFT: "W"}

class LabyrinthBuilder:
    def __init__(self, config_data: Dict[str, Any], show_anim: bool = False) -> None:
        # On utilise exactement les clés générées par le parsing de ton peer
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
        
        self.build_labyrinth(show_anim)

    @staticmethod
    def wipe_screen() -> None:
        # Utilisation de clear pour éviter les bugs de scrolling sur les petits terminaux
        os.system("clear")

    def render_grid(
        self,
        invert_colors: bool,
        current_trail: Optional[List[List[int]]] = None
    ) -> None:
        COLOR_1 = "\033[31m"
        COLOR_2 = "\033[32m"
        RESET_COL = "\033[0m"
        
        if invert_colors:
            COLOR_1, COLOR_2 = COLOR_2, COLOR_1

        WALL_BLOCK = "█"
        print(WALL_BLOCK + ("████" * self.cols))
        
        pattern_42_cells = self.locate_42_pattern()

        for r in range(self.rows):
            row_mid = WALL_BLOCK
            row_bot = WALL_BLOCK

            for c in range(self.cols):
                val = self.grid[r][c]

                if c == self.start_pos[0] and r == self.start_pos[1]:
                    row_mid += COLOR_2 + " S " + RESET_COL
                elif c == self.end_pos[0] and r == self.end_pos[1]:
                    row_mid += COLOR_2 + " E " + RESET_COL
                elif (c, r) in pattern_42_cells:
                    row_mid += COLOR_1 + " 4 " + RESET_COL
                elif current_trail:
                    if [c, r] == current_trail[-1]: 
                        row_mid += COLOR_2 + " @ " + RESET_COL
                    elif [c, r] in current_trail:
                        row_mid += COLOR_2 + " · " + RESET_COL
                    else:
                        row_mid += "   "
                else:
                    row_mid += "   "

                if val & RIGHT:
                    row_mid += WALL_BLOCK
                else:
                    row_mid += " "

                if val & DOWN:
                    row_bot += "████"
                else:
                    row_bot += "   " + WALL_BLOCK

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
