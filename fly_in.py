import sys
from map_parsing import MapParser


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <filename>")
        sys.exit(1)

    game_map = MapParser(sys.argv[1]).parse_now()

    print(game_map.nb_drones)
    print("-"* 50)
    print(game_map.start_zone.name)
    print("-"* 50)

    print(game_map.end_zone.name)
    print("-"* 50)

    print(game_map.zones_by_name.keys())
    print("-"* 50)

    print(game_map.connections_by_name.keys())


if __name__ == "__main__":
    main()