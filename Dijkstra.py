import heapq
from map_cls import Map
from typing import Dict, List, Optional, Tuple

class PathFinder:
    """Handles routing logic using Dijkstra's algorithm."""
    
    def __init__(self, map_data : Map):
        self.map = map_data
        self.zone_distances: Dict[str, float] = {}
        self.previous_zone: Dict[str, Optional[str]] = {}
        self.to_visit: List[Tuple[float, str]] = []

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

            if current_zone_name == end_name:
                break

            if current_cost > self.zone_distances[current_zone_name]:
                continue

            current_zone_obj = self.map.zones_by_name[current_zone_name]

            for neighbor_zone, move_cost in self.map.get_neighbors_with_cost(current_zone_obj):
                neighbor_name = neighbor_zone.name
                
                new_cost = current_cost + float(move_cost)

                if new_cost < self.zone_distances[neighbor_name]:
                    
                    self.zone_distances[neighbor_name] = new_cost
                    self.previous_zone[neighbor_name] = current_zone_name
                    
                    heapq.heappush(self.to_visit, (new_cost, neighbor_name))
        
        
        return [] 