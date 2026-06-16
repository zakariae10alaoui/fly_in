import heapq
from map_cls import Map
from typing import Dict, List, Optional, Tuple , Set

class PathFinder:
    """Handles routing logic using Dijkstra's algorithm."""
    
    def __init__(self, map_data : Map):
        self.map = map_data
        self.zone_distances: Dict[str, float] = {}
        self.previous_zone: Dict[str, Optional[str]] = {}
        self.to_visit: List[Tuple[float, str]] = []
        self.visited : Set = ()

    def setup_dijkstra(self):
        """Initializes the data structures before running the loop."""
        for zone_name in self.map.zones_by_name.keys():
            self.zone_distances[zone_name] = float('inf')
            self.previous_zone[zone_name] = None

        start_name = self.map.start_zone.name
        end_name = self.map.end_zone.name

        self.zone_distances[end_name] = float('inf')
        self.zone_distances[start_name] = 0
        self.previous_zone[start_name] = None
        self.previous_zone[end_name] = None
        
        heapq.heappush(self.to_visit, (0, start_name))
    
    def calculate_short_path(self) -> List[str]:
        """Runs Dijkstra's algorithm and returns the optimal path."""
        
        self.setup_dijkstra()
        
        end_name = self.map.end_zone.name
        while self.to_visit:
            current_cost, current_zone_name = heapq.heappop(self.to_visit)
            print(f"\n--- POP: '{current_zone_name}' (cost={current_cost}) ---")

            if current_zone_name == end_name:
                print(f"  → reached END zone '{end_name}', stopping.")
                break

            if current_cost > self.zone_distances[current_zone_name]:
                print(f"  → outdated entry, skip.")
                continue

            current_zone_obj = self.map.get_zone(current_zone_name)
            if current_zone_obj is None:
                print(f"  → zone '{current_zone_name}' not found, skip.")
                continue

            for  move_cost ,neighbor_zone in self.map.get_neighbors_with_cost(current_zone_obj):
                neighbor_name = neighbor_zone.name
                new_cost = current_cost + float(move_cost)

                print(f"  neighbor '{neighbor_name}': new_cost={new_cost}, known={self.zone_distances[neighbor_name]}")

                if new_cost < self.zone_distances[neighbor_name]:
                    self.zone_distances[neighbor_name] = new_cost
                    self.previous_zone[neighbor_name] = current_zone_name
                    heapq.heappush(self.to_visit, (new_cost, neighbor_name))
                    print(f"    → UPDATED: distances['{neighbor_name}']={new_cost}, previous='{current_zone_name}'")
                    print(f"    → PUSHED: ({new_cost}, '{neighbor_name}') to to_visit")
                else:
                    print(f"    → no update, existing path is cheaper or equal")

        print(f"\n--- FINAL distances: {self.zone_distances} ---")
        print(f"--- FINAL previous:  {self.previous_zone} ---")
        
        
        return self.reverse_path()
    
    def reverse_path(self) -> List[str]:
        """Walks previous_zone backwards to build the path."""
        path: List[str] = []
        current: Optional[str] = self.map.end_zone.name

        while current is not None:
            path.append(current)
            current = self.previous_zone.get(current)

        path.reverse()
        return path