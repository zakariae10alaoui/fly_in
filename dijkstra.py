import heapq
from map_cls import Map
from typing import Dict, List, Optional, Tuple , Set

class PathFinder:
    """Handles routing logic using Dijkstra's algorithm."""
    
    def __init__(self, map_data : Map):
        self.map = map_data
        self.zone_distances: Dict[Tuple[str, int], float] = {}
        self.previous_zone: Dict[Tuple[str, int], Optional[Tuple[str, int]]] = {}
        self.to_visit: List[Tuple[float, Tuple[str, int]]] = []

    def setup_dijkstra(self):
        """Initializes the data structures before running the loop."""
        self.to_visit = []
        self.zone_distances.clear()
        self.previous_zone.clear()

        start_name = self.map.start_zone.name

        self.zone_distances[start_name] = 0
        self.previous_zone[start_name] = None

        
        heapq.heappush(self.to_visit, (0, start_name))
    
    def calculate_short_path(self) -> List[str]:
        """Runs Dijkstra's algorithm and returns the optimal path."""
        
        self.setup_dijkstra()
        
        end_name = self.map.end_zone.name
        final_destination_state: Optional[Tuple[str, int]] = None
        target_found = False

        while self.to_visit:
            current_cost, current_state = heapq.heappop(self.to_visit)
            current_zone_name, current_turn = current_state

            if current_zone_name == end_name:
                final_destination_state = current_state
                break

            if current_zone_name == end_name:
                final_destination_state = current_state
                break

            if current_cost > self.zone_distances.get(current_state, float('inf')):
                continue

            current_zone_obj = self.map.get_zone(current_zone_name)
 
            for move_cost , neighbor_zone in self.map.get_neighbors_with_cost(current_zone_obj):
                neighbor_name = neighbor_zone.name
                arrival_turn = current_turn + move_cost
                neighbor_state = (neighbor_name, arrival_turn)

                if not engine.is_link_available(current_zone_name, neighbor_name, current_turn, 1):
                    continue
                if not engine.is_zone_available(neighbor_name, arrival_turn, 1):
                    continue
                
                new_cost = current_cost + move_cost

                if new_cost < self.zone_distances.get(neighbor_state, float('inf')):
                    self.zone_distances[neighbor_state] = new_cost
                    self.previous_zone[neighbor_state] = current_state
                    heapq.heappush(self.to_visit, (new_cost, neighbor_state))
                    
            wait_state = (current_zone_name, current_turn + 1)
            if engine.is_zone_available(current_zone_name, current_turn + 1, 1):
                new_cost = current_cost + 1
                if new_cost < self.zone_distances.get(wait_state, float('inf')):
                    self.zone_distances[wait_state] = new_cost
                    self.previous_zone[wait_state] = current_state
                    heapq.heappush(self.to_visit, (new_cost, wait_state))
        
        if final_destination_state is None:
            return []
            
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