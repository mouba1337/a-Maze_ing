*This project has been created as part of the 42 curriculum by kraghib and berrabia.*

# A-Maze-Ing

## Description

**A-Maze-Ing** is a configurable maze generator and solver written in Python.
The project generates ASCII mazes based on a configuration file, supports multiple generation algorithms, enforces a special “42” pattern constraint, and computes the shortest path from entry to exit.

The maze can be:
- **Perfect** (only one path between any two cells)
- **Imperfect** (with loops)
- Generated using **DFS (recursive backtracking)** or **Prim’s / BFS-style algorithm**
- Rendered interactively in the terminal with optional path visualization

The project is designed with **reusability** in mind: the maze generation logic lives in a standalone, importable module (`mazegen`) that can be reused in future projects.

---

## Project Structure

```

.
├── Makefile
├── README.md
├── a_maze_ing.py
├── config.txt
└── mazegen/
├── **init**.py
├── generator.py
└── parse.py

````

---

## Instructions

### Requirements
- Python **3.10+**
- Unix-like terminal (for ANSI colors and `clear`)

### Installation

Dependencies are installed automatically via the Makefile:

```bash
make install
````

### Run the Program

```bash
make run
```

or manually:

```bash
python3 a_maze_ing.py config.txt
```

### Debug Mode

```bash
make debug
```

### Clean Cache Files

```bash
make clean
```

### Linting

```bash
make lint
make lint-strict
```

---

## Usage

Once running, an interactive menu is displayed:

```
=== A-MAZE-ING ===
1 - Re-generate a new maze
2 - Show/hide path from entry to exit
3 - Swap maze colors
4 - Quit
```

* **Re-generate** creates a new maze using the same configuration
* **Show/hide path** toggles the shortest path visualization
* **Swap colors** inverts the terminal color scheme
* **Quit** exits the program

---

## Configuration File Format

The maze is fully driven by a configuration file (`config.txt`).

### Required Keys

```txt
width=21
height=15
entry=0,0
exit=20,14
perfect=true
output_file=maze.txt
```

### Optional Keys

```txt
seed=42
algo=dfs
```

### Full Specification

| Key           | Type   | Description              |
| ------------- | ------ | ------------------------ |
| `width`       | int    | Maze width (≥ 9)         |
| `height`      | int    | Maze height (≥ 7)        |
| `entry`       | x,y    | Entry cell coordinates   |
| `exit`        | x,y    | Exit cell coordinates    |
| `perfect`     | bool   | `true` = perfect maze    |
| `output_file` | string | File where maze is saved |
| `seed`        | int    | Random seed (optional)   |
| `algo`        | string | `dfs`, `bfs`, or `prim`  |

 Entry and exit **must not** overlap and **must not be placed on the “42” pattern**.

---

## Maze Generation Algorithms

### Implemented Algorithms

* **DFS (Recursive Backtracking)** — default
* **Prim’s / BFS-style randomized frontier algorithm**

### Chosen Default: DFS

**Why DFS?**

* Simple and reliable
* Produces long corridors and visually pleasing mazes
* Easy to control and extend
* Ideal for animated generation

Prim’s algorithm is also available for users who prefer denser, more uniform mazes.

---

## Maze Solving

* Solving is done using **Breadth-First Search (BFS)**
* Guarantees the **shortest path**
* The solution is:

  * Stored as a direction string (`N`, `E`, `S`, `W`)
  * Reconstructed into a coordinate path
  * Optionally animated in the terminal

---

## Reusable Code

The following parts are **fully reusable**:

### `mazegen.generator.MazeGenerator`

* Standalone maze generation class
* Can be imported and used without the CLI
* Supports custom size, seed, algorithms, rendering
* Exposes:

  * `maze` structure
  * `solved_path`
  * `path_list`

### `mazegen.parse.parse_config`

* Generic config parser with validation
* Can be reused for other config-driven projects

Example reuse:

```python
from mazegen import MazeGenerator, parse_config

config = parse_config("config.txt")
maze = MazeGenerator(config, render=False)
print(maze.solved_path)
```

---

## Advanced Features

* Multiple generation algorithms
* Perfect / imperfect maze toggle
* Animated generation and solving
* ANSI-colored rendering
* Enforced “42” pattern inside the maze
* Deterministic generation via seed
* Exported maze file with solution

---

## Team & Project Management

### Team

* **khalilraghib** — Design, implementation, algorithms, testing

### Planning

* Initial focus on core DFS maze generation
* Early refactor to isolate logic into a reusable module
* Added solver, rendering, and configuration validation
* Extended to support multiple algorithms and loops

### What Worked Well

* Early modular design
* Clear separation between parsing, generation, and UI
* Strong typing and linting improved reliability

### What Could Be Improved

* More maze algorithms (Kruskal, Eller)
* Graphical (non-ASCII) output
* Performance optimizations for very large mazes

### Tools Used

* `make`
* `mypy`
* `flake8`
* Python standard library
* Terminal ANSI rendering

---

## Resources

### Technical References

* Wikipedia – Maze generation algorithms
* DFS / BFS graph traversal
* Breadth-First Search for shortest paths
* Python `deque` documentation

### AI Usage

AI was used as a **development assistant**:

* Clarifying algorithm choices
* Reviewing architecture and typing
* Improving documentation structure
* Ensuring 42 subject compliance

All design decisions, implementation, and validation were done by the project author.

---

## Output Example

```
+---+---+---+---+---+---+---+---+---+
| s   p   p   p   p   p   p   p   p |
+---+---+---+---+---+---+---+---+   +
|   | 4 |           | 4 | 4 | 4 | p |
+   +---+   +   +   +---+---+---+   +
|   | 4 |                   | 4 | p |
+   +---+---+---+   +---+---+---+   +
|   | 4 | 4 | 4 |   | 4 | 4 | 4 | p |
+   +---+---+---+   +---+---+---+   +
|           | 4 |   | 4 |         p |
+---+   +   +---+   +---+---+---+   +
|           | 4 |   | 4 | 4 | 4 | p |
+   +   +   +---+   +---+---+---+   +
|                         e   p   p |
+---+---+---+---+---+---+---+---+---+
```

---

## License

This project is for educational purposes as part of the **42 curriculum**.

