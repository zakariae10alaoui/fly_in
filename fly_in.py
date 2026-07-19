import sys
import arcade


from map_parsing import MapParser  
from visual import Visualizer
from engine import TheEngine
from dijkstra import PathFinder

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <filename>")
        sys.exit(1)

    # 1. Parse your game map
    game_map = MapParser(sys.argv[1]).parse_now()

    print(f"Total Drones to Route: {game_map.nb_drones}")
    print("-" * 50)
    
    # 2. Instantiate both your Engine and your Pathfinder
    engine = TheEngine(game_map)
    solution = PathFinder(game_map)

    # 3. Process all drones sequentially
    print("🚀 Running space-time routing...")
    engine.drive_all_drones(solution)
    print("-" * 50)

    # 4. Find how many turns it took for ALL drones to finish
    total_turns_needed = 0
    
    for drone_key, safe_path in engine.final_drones_paths.items():
        if safe_path:
            # Grab the turn number from the very last (zone_name, turn) tuple in the path
            last_zone, finish_turn = safe_path[-1]
            print(f"🛸 {drone_key} arrived at {last_zone} on Turn {finish_turn}")
            
            # The total time is whenever the absolute latest drone finishes
            if finish_turn > total_turns_needed:
                total_turns_needed = finish_turn
        else:
            print(f"⚠️ {drone_key} could not find a safe path!")

    print("=" * 50)
    print(f"🏁 ALL DRONES REACHED THE DESTINATION IN: {total_turns_needed} TURNS")
    print("=" * 50)
    
    picasso = Visualizer(game_map)
    arcade.run()

if __name__ == "__main__":
    main()