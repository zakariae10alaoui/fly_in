import sys
import arcade

from map_parsing import MapParser
from visual import Visualizer
from engine import TheEngine
from dijkstra import PathFinder


def main() -> None:
    """Initialize the pipeline, find the solutions, and begin visualization."""
    if len(sys.argv) != 2:
        print("Usage: python3 fly_in.py <filename>")
        sys.exit(1)

    try:
        game_map = MapParser(sys.argv[1]).parse_now()

        if not game_map.is_solvable():
            raise ValueError("This map is not solvable go out")

        engine = TheEngine(game_map)
        solution = PathFinder(game_map)

        engine.drive_all_drones(solution)

        picasso = Visualizer(game_map)
        picasso.build_turn_log(engine.final_drones_paths)
        print(picasso.format_turn_log())

        arcade.run()

    except (ValueError, KeyboardInterrupt) as e:
        print(f"{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
