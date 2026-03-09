import os
import random
from sys import argv
from time import sleep
from typing import Dict, Any, List, Optional

# On importe les bons noms !
from mazegen import MazeGenerator
from mazegen import load_maze_config

class MazeRenderer:
    def __init__(self, generator: MazeGenerator):
        self.generator = generator
        self.wall_color = "\033[37m"
        self.color_1 = "\033[31m"  # Rouge (pour 42)
        self.color_2 = "\033[32m"  # Vert (pour S, E, Chemin)
        self.reset_col = "\033[0m"

    def change_wall_color(self) -> None:
        colors = ["\033[33m", "\033[34m", "\033[35m", "\033[36m", "\033[37m", "\033[93m", "\033[94m"]
        self.wall_color = random.choice(colors)

    def wipe_screen(self) -> None:
        os.system("clear")

    def render_grid(self, current_trail: Optional[List[List[int]]] = None) -> None:
        wall_c = self.wall_color
        print(wall_c + "█" + ("████" * self.generator.cols) + self.reset_col)

        pattern_42_cells = self.generator.locate_42_pattern()
        RIGHT, DOWN = 2, 4

        for r in range(self.generator.rows):
            row_mid = wall_c + "█" + self.reset_col
            row_bot = wall_c + "█" + self.reset_col

            for c in range(self.generator.cols):
                val = self.generator.grid[r][c]

                # 1. Le Centre
                if c == self.generator.start_pos[0] and r == self.generator.start_pos[1]:
                    row_mid += self.color_2 + " S " + self.reset_col
                elif c == self.generator.end_pos[0] and r == self.generator.end_pos[1]:
                    row_mid += self.color_2 + " E " + self.reset_col
                elif (c, r) in pattern_42_cells:
                    row_mid += self.color_1 + " █ " + self.reset_col
                elif current_trail:
                    if [c, r] == current_trail[-1]:
                        row_mid += self.color_2 + " . " + self.reset_col
                    elif [c, r] in current_trail:
                        row_mid += self.color_2 + " @ " + self.reset_col
                    else:
                        row_mid += "   "
                else:
                    row_mid += "   "

                # 2. Le Mur Est
                if val & RIGHT:
                    row_mid += wall_c + "█" + self.reset_col
                else:
                    row_mid += " "

                # 3. Le Mur Sud
                if val & DOWN:
                    row_bot += wall_c + "████" + self.reset_col
                else:
                    row_bot += "   " + wall_c + "█" + self.reset_col

            print(row_mid)
            print(row_bot)

    def animate_generation(self, generator_instance: MazeGenerator) -> None:
        """ Callback appelé par MazeGenerator pour l'animation """
        self.wipe_screen()
        print("== ⛏️  DIGGING MAZE (DFS) ==")
        self.render_grid()
        sleep(0.005)

    def animate_solution(self) -> None:
        trail = []
        for step in self.generator.solution_coords:
            trail.append(step)
            self.wipe_screen()
            print("== 🏃 ANIMATING SHORTEST PATH ==")
            self.render_grid(trail)
            sleep(0.08)

# --- LE MENU PRINCIPAL ---
if __name__ == "__main__":
    if len(argv) != 2:
        print("Usage: python a_maze_ing.py <config_file>")
        exit(1)

    try:
        config: Dict[str, Any] = load_maze_config(argv[1])
    except Exception as e:
        print(f"A_MAZE_ING: Config/Error occurred: {e}")
        exit(1)

    try:
        generator = MazeGenerator(config)
        renderer = MazeRenderer(generator)
        
        # On passe la fonction d'animation au générateur
        generator.build_labyrinth(render_callback=renderer.animate_generation)

        choices: List[str] = ["1", "2", "3", "4"]
        i: str = "1"
        show_path: bool = False

        renderer.wipe_screen() 
        renderer.render_grid()

        while i != "4":
            print("\n=== A-MAZE-ING ===")
            print("1 - Re-generate a new maze")
            print("2 - Show/hide path from entry to exit")
            print("3 - Change maze colors randomly")
            print("4 - Quit")
            i = input("Choice? (1-4): ")

            while i not in choices:
                print("Invalid choice")
                i = input("Choice? (1-4): ")

            if i == "1":
                renderer.wipe_screen()
                generator = MazeGenerator(config)
                renderer = MazeRenderer(generator)
                generator.build_labyrinth(render_callback=renderer.animate_generation)
                show_path = False
                renderer.wipe_screen()
                renderer.render_grid()

            elif i == "2":
                show_path = not show_path
                renderer.wipe_screen()
                if show_path:
                    renderer.animate_solution()
                else:
                    renderer.render_grid()

            elif i == "3":
                renderer.change_wall_color()
                renderer.wipe_screen()
                if show_path:
                    renderer.render_grid(generator.solution_coords)
                else:
                    renderer.render_grid()

    except Exception as e:
        print(f"A_MAZE_ING: an error occurred: {e}")
        exit(1)