import sys
import random
from typing import Tuple, Dict, Any, List, Callable, Optional
from collections import deque

# Protection pour les très grands labyrinthes


UP, RIGHT, DOWN, LEFT = 1, 2, 4, 8
OFFSET_X = {UP: 0, RIGHT: 1, DOWN: 0, LEFT: -1}
OFFSET_Y = {UP: -1, RIGHT: 0, DOWN: 1, LEFT: 0}
REVERSE_DIR = {UP: DOWN, RIGHT: LEFT, DOWN: UP, LEFT: RIGHT}
CHAR_MAP = {UP: "N", RIGHT: "E", DOWN: "S", LEFT: "W"}


class MazeGenerator:
    def __init__(self, config_data: Dict[str, Any]) -> None:
        self.cols: int = int(config_data["width"])
        self.rows: int = int(config_data["height"])
        self.start_pos: Tuple[int, int] = config_data["entry"]
        self.end_pos: Tuple[int, int] = config_data["exit"]
        self.is_perfect: bool = config_data["perfect"]
        self.export_path: str = config_data["output_file"]
        self.random_seed: Optional[int] = config_data.get("seed", None)

        self.solution_str: str = ""
        self.solution_coords: List[List[int]] = []

        # Grille pleine par défaut (0b1111 = tous les murs fermés)
        self.grid: List[List[int]] = [
            [0b1111 for _ in range(self.cols)] for _ in range(self.rows)
        ]

    def __str__(self) -> str:
        text_out = ""
        for row_data in self.grid:
            text_out += " ".join(f"{c_val:04b}" for c_val in row_data) + "\n"
        return text_out

    def build_labyrinth(self, render_callback: Optional[Callable] = None) -> None:
        if self.random_seed is not None:
            random.seed(self.random_seed)

        pattern_42_cells = self.locate_42_pattern()

        if self.start_pos in pattern_42_cells or self.end_pos in pattern_42_cells:
            raise ValueError("Entry or exit overlaps with the 42 pattern.")

        explored = [[False] * self.cols for _ in range(self.rows)]
        self.drill_dfs(self.start_pos[0], self.start_pos[1], explored, pattern_42_cells, render_callback)

        if not self.is_perfect:
            self.create_cycles(pattern_42_cells)

        self.find_shortest_path()
        self.export_to_disk()

    def drill_dfs(
        self,
        cx: int,
        cy: int,
        explored: List[List[bool]],
        pattern_42_cells: List[Tuple[int, int]],
        render_callback: Optional[Callable],
    ) -> None:
        explored[cy][cx] = True
        ways = [UP, RIGHT, DOWN, LEFT]
        random.shuffle(ways)

        if render_callback:
            render_callback(self)

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
                self.drill_dfs(next_x, next_y, explored, pattern_42_cells, render_callback)

    def _safe_to_break(self, cx: int, cy: int, way: int) -> bool:
        """
        Anti-Zone 3x3: Empêche la création d'espaces vides de 2x2.
        Ce qui garantit mathématiquement qu'aucun espace de 3x3 ne sera créé.
        """
        next_x = cx + OFFSET_X[way]
        next_y = cy + OFFSET_Y[way]

        def no_wall(x: int, y: int, d: int) -> bool:
            if x < 0 or x >= self.cols or y < 0 or y >= self.rows:
                return False
            return (self.grid[y][x] & d) == 0

        if way in (RIGHT, LEFT):
            if no_wall(cx, cy, UP) and no_wall(next_x, next_y, UP) and no_wall(cx, cy - 1, way):
                return False
            if no_wall(cx, cy, DOWN) and no_wall(next_x, next_y, DOWN) and no_wall(cx, cy + 1, way):
                return False
        elif way in (UP, DOWN):
            if no_wall(cx, cy, LEFT) and no_wall(next_x, next_y, LEFT) and no_wall(cx - 1, cy, way):
                return False
            if no_wall(cx, cy, RIGHT) and no_wall(next_x, next_y, RIGHT) and no_wall(cx + 1, cy, way):
                return False
        return True

    def create_cycles(self, pattern_42_cells: List[Tuple[int, int]]) -> None:
        cycle_target = int(self.cols * self.rows * 0.15)
        tries = 0
        max_tries = cycle_target * 10

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
                if self._safe_to_break(cx, cy, way):
                    self.grid[cy][cx] &= ~way
                    self.grid[next_y][next_x] &= ~REVERSE_DIR[way]
                    cycle_target -= 1

    def find_shortest_path(self) -> None:
        search_q: deque[Tuple[int, int, List[str]]] = deque([(self.start_pos[0], self.start_pos[1], [])])
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

                if 0 <= next_x < self.cols and 0 <= next_y < self.rows and not scanned[next_y][next_x]:
                    scanned[next_y][next_x] = True
                    search_q.append((next_x, next_y, route + [CHAR_MAP[w]]))

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

    def export_to_disk(self) -> None:
        with open(self.export_path, "w") as file_out:
            for row_data in self.grid:
                line_str = "".join(format(cell, "X") for cell in row_data)
                file_out.write(line_str + "\n")
            file_out.write(f"\n{self.start_pos[0]},{self.start_pos[1]}\n")
            file_out.write(f"{self.end_pos[0]},{self.end_pos[1]}\n")
            file_out.write(self.solution_str + "\n")

    def locate_42_pattern(self) -> List[Tuple[int, int]]:
        if self.cols < 9 or self.rows < 7:
            return []
        center = (self.cols // 2, self.rows // 2)
        c_x, c_y = center
        return [
            (c_x - 3, c_y - 2), (c_x - 3, c_y - 1), (c_x - 3, c_y), (c_x - 2, c_y),
            (c_x - 1, c_y), (c_x - 1, c_y + 1), (c_x - 1, c_y + 2),
            (c_x + 1, c_y - 2), (c_x + 1, c_y), (c_x + 1, c_y + 1), (c_x + 1, c_y + 2),
            (c_x + 2, c_y - 2), (c_x + 2, c_y), (c_x + 2, c_y + 2),
            (c_x + 3, c_y - 2), (c_x + 3, c_y - 1), (c_x + 3, c_y), (c_x + 3, c_y + 2),
        ]