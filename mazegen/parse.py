import sys
from typing import Tuple, Dict, Any, Set


def check_bounds(
    point: Tuple[int, int],
    width: int,
    height: int,
    label: str,
) -> None:
    """Ensures a given coordinate point is within the maze grid."""
    x, y = point
    if x < 0 or y < 0:
        raise ValueError(f"[{label}] Error: Coordinates"
                         f"cannot be negative -> {point}")
    if x >= width or y >= height:
        raise ValueError(
            f"[{label}] Error: Position {point} exceeds"
            f"maze dimensions {width}x{height}"
        )


def _parse_tuple(coord_string: str, label: str) -> Tuple[int, int]:
    """"
    Converts a comma-separated string into acoordinate tuple safely.
    """
    elements = coord_string.split(",")
    if len(elements) != 2:
        raise ValueError(
            f"[{label}] Error: Expected 'x,y' format, got '{coord_string}'"
        )
    try:
        return int(elements[0]), int(elements[1])
    except ValueError:
        raise ValueError(f"[{label}] Error: Coordinate"
                         "values must be integers.")


def load_maze_config(filepath: str) -> Dict[str, Any]:
    """Reads, parses, and validates the A-Maze-ing configuration file."""
    expected_keys: Set[str] = {
        "width",
        "height",
        "entry",
        "exit",
        "perfect",
        "output_file",
    }
    allowed_extras: Set[str] = {"seed", "algo"}

    parsed_data: Dict[str, Any] = {}

    # Safely open and read the file
    try:
        with open(filepath, mode="r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise ValueError("Fatal: Could not locate config"
                         f"file at '{filepath}'")

    # Process each line
    for raw_text in lines:
        clean_text = raw_text.strip()

        # Ignore empty lines and comments
        if not clean_text or clean_text.startswith("#"):
            continue

        if "=" not in clean_text:
            raise ValueError("Syntax Error: Missing '='"
                             f"in line -> {clean_text}")

        left_part, right_part = clean_text.split("=", 1)
        cfg_key = left_part.strip().lower()

        if cfg_key in parsed_data:
            raise ValueError(f"Duplicate entry found for key: {cfg_key}")

        parsed_data[cfg_key] = right_part.strip()

    # Validate key presence using sets and the walrus operator (:=)
    keys_present = set(parsed_data.keys())
    if missing := expected_keys - keys_present:
        raise ValueError(f"Missing required configuration keys: {missing}")
    if invalid := keys_present - expected_keys - allowed_extras:
        raise ValueError(f"Unrecognized configuration keys: {invalid}")

    # Typecast and validate dimensions
    try:
        parsed_data["width"] = int(parsed_data["width"])
        parsed_data["height"] = int(parsed_data["height"])
    except ValueError:
        raise ValueError("Type Error: 'WIDTH' and"
                         "'HEIGHT' must be integers.")

    if parsed_data["width"] <= 0 or parsed_data["height"] <= 0:
        raise ValueError("Value Error: Dimensions must be"
                         "greater than zero.")

    # Handle the 42 pattern warning
    if parsed_data["width"] < 9 or parsed_data["height"] < 7:
        print(
            "Warning: Maze is too small to render the '42'"
            "pattern (min 9x7).",
            file=sys.stderr,
        )

    # Typecast and validate coordinates
    start_pt = _parse_tuple(str(parsed_data["entry"]), "ENTRY")
    end_pt = _parse_tuple(str(parsed_data["exit"]), "EXIT")

    if start_pt == end_pt:
        raise ValueError("Logic Error: ENTRY and EXIT cannot"
                         "be the same cell.")

    check_bounds(
        start_pt, parsed_data["width"], parsed_data["height"], "ENTRY"
    )
    check_bounds(
        end_pt, parsed_data["width"], parsed_data["height"], "EXIT"
    )
    parsed_data["entry"] = start_pt
    parsed_data["exit"] = end_pt

    # Boolean conversion for perfect flag
    perf_string = str(parsed_data["perfect"]).strip().lower()
    if perf_string not in ("true", "false"):
        raise ValueError("Type Error: 'PERFECT' must be"
                         "strictly 'True' or 'False'.")
    parsed_data["perfect"] = perf_string == "true"

    # Handle optional seed safely
    if "seed" in parsed_data:
        try:
            parsed_data["seed"] = int(parsed_data["seed"])
        except ValueError:
            raise ValueError("Type Error: 'SEED' must be a valid integer.")

    return parsed_data
