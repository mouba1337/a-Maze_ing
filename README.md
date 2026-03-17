This project has been created as part of the 42 curriculum by mhend, eanass. ￼

Description
A-Maze-ing is a Python-based procedural maze generator and solver. It parses a configuration file to construct a labyrinth of specified dimensions, optionally ensuring it is a "perfect" maze (only one valid path from start to finish). The project features a built-in terminal visualizer with step-by-step animation, shortest-path calculation, and a reusable Python package architecture. It also embeds a mandatory "42" shape inside the generated walls!￼
+3

Instructions
1. Installation
We recommend using a virtual environment to avoid conflicts.￼

Bash
￼
python3 -m virtualenv env
source env/bin/activate
make install
2. Execution
To run the main program with the visualizer, pass the configuration file as the only argument:￼
+1

Bash
￼
python3 a_maze_ing.py config.txt
3. Linting and Cleanup

Bash
￼
make lint   # Runs flake8 and strict mypy checks
make clean  # Removes __pycache__, .mypy_cache, and build artifacts
Configuration File Format
The program requires a text file containing KEY=VALUE pairs. Lines starting with # are ignored as comments.￼
+1


WIDTH: Maze width (number of columns).￼
+1


HEIGHT: Maze height (number of rows).￼
+1


ENTRY: Start coordinates x,y.￼
+1


EXIT: End coordinates x,y.￼
+1


OUTPUT_FILE: Name of the hexadecimal text file to export the maze to.￼
+1

PERFECT: True or False. If True, generates a maze with a single unique path.￼
+1


seed (Optional): Integer to guarantee reproducibility of the maze.￼

Algorithm Choices

Generation: We chose a Randomized Depth-First Search (DFS) algorithm. We chose this because DFS naturally creates deep, winding corridors with a high "branching factor," which provides the classic, difficult aesthetic expected from a labyrinth.
Solving: We chose Breadth-First Search (BFS). We chose this because BFS explores the grid layer-by-layer, guaranteeing that the path it finds is the mathematically shortest route between the entry and exit.￼
+1

Code Reusability (Using the mazegen package)
Our maze generation logic is completely isolated in the mazegen package, which can be built into a .whl file and installed via pip in any future project.￼
+2


How to instantiate and use it: ￼

Python
￼
from mazegen.generator import MazeGenerator

# 1. Pass custom parameters via a dictionary
config = {
    "width": 15,
    "height": 15,
    "entry": (0, 0),
    "exit": (14, 14),
    "perfect": True,
    "output_file": "my_maze.txt",
    "seed": 42
}

# 2. Instantiate and run the generator
generator = MazeGenerator(config)
generator.build_labyrinth()

# 3. Access the generated structure and solution
maze_grid = generator.grid             # 2D list of bitmask integers
shortest_path = generator.solution_str # String of 'N', 'S', 'E', 'W'
print(f"Path to exit: {shortest_path}")
Team & Project Management

Roles: mhend focused primarily on the core algorithm logic (DFS/BFS), grid mathematics, and Python packaging/virtual environments. eanass focused on the configuration parsing, error handling, and the terminal ANSI visualizer/animation engine. (Note: Feel free to swap/edit these roles!)￼


Anticipated Planning vs. Reality: We originally planned to build the visualizer last. However, we realized quickly that debugging the DFS algorithm was impossible without seeing the maze, so we shifted the visualizer to week 1.￼


What Worked Well: Pair programming the coordinate logic saved us from off-by-one errors.￼


What Could Be Improved: We underestimated how strict mypy typing and Python packaging (pyproject.toml) would be, which caused delays near the deadline.￼


Tools Used: Git for version control, VS Code, make for automation, virtualenv for environment isolation, and build/setuptools for .whl packaging.￼

Resources & AI Usage

Classic Resources: We utilized GeeksforGeeks and various YouTube tutorials to deeply understand graph theory concepts (specifically DFS and BFS traversal). Peer learning was heavily used to validate our coordinate math and test our edge cases.￼


AI Usage: AI (LLM) was utilized primarily as a technical assistant to overcome specific toolchain hurdles. Specifically, AI was used to understand modern Python pyproject.toml configuration, to resolve obscure mypy strict type-hinting errors, and to learn how to properly isolate flake8 linting within a Makefile to avoid scanning virtual environment files. AI was not used to write the core algorithmic logic.