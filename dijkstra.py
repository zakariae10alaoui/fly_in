import heapq
from map_cls import Map
from typing import Dict, List, Optional, Tuple

class PathFinder:
    """Handles routing logic using Dijkstra's algorithm."""
    
    def __init__(self, map_data: Map):
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
        start_state = (start_name, 0)
        self.zone_distances[start_state] = 0.0
        self.previous_zone[start_state] = None
        
        heapq.heappush(self.to_visit, (0.0, start_state))

    def get_space_time_neighbors(
        self, current_state: Tuple[str, int], engine: 'TheEngine'
    ) -> List[Tuple[float, Tuple[str, int]]]:
        """
        Generates valid next space-time state transitions.
        Returns a list of tuples: (dijkstra_edge_cost, (neighbor_zone_name, next_turn))
        """
        current_zone_name, current_turn = current_state
        next_turn = current_turn + 1
        neighbors: List[Tuple[float, Tuple[str, int]]] = []

        if engine.is_zone_available(current_zone_name, next_turn):
            neighbors.append((1.1, (current_zone_name, next_turn)))
        
        current_zone_obj = self.map.get_zone(current_zone_name)
        physical_neighbors = self.map.get_neighbors_with_cost(current_zone_obj)

        for move_cost, neighbor_zone in physical_neighbors:
            neighbor_name = neighbor_zone.name

            if neighbor_zone.zone_type == "restricted":
                transit_turn = current_turn + 1
                arrival_turn = current_turn + 2

                if not engine.is_link_available(current_zone_name, neighbor_name, current_turn):
                    continue
                if not engine.is_link_available(current_zone_name, neighbor_name, transit_turn):
                    continue

                if not engine.is_zone_available(neighbor_name, arrival_turn):
                    continue

                neighbors.append((move_cost, (neighbor_name, arrival_turn)))

            else: 
                if not engine.is_link_available(current_zone_name, neighbor_name, current_turn):
                    continue
                if not engine.is_zone_available(neighbor_name, next_turn):
                    continue

                neighbors.append((move_cost, (neighbor_name, next_turn)))

        return neighbors
    
    def calculate_short_path(self, engine: 'TheEngine') -> List[Tuple[str, int]]:
        """Runs Dijkstra's algorithm and returns the optimal path."""
        self.setup_dijkstra()
        
        end_name = self.map.end_zone.name
        final_zone_state: Optional[Tuple[str, int]] = None

        while self.to_visit:
            current_cost, current_state = heapq.heappop(self.to_visit)
            current_zone_name, current_turn = current_state

            if current_zone_name == end_name:
                final_zone_state = current_state
                break

            if current_cost > self.zone_distances.get(current_state, float('inf')):
                continue

            for edge_cost, neighbor_state in self.get_space_time_neighbors(current_state, engine):
                new_cost = current_cost + edge_cost

                if new_cost < self.zone_distances.get(neighbor_state, float('inf')):
                    self.zone_distances[neighbor_state] = new_cost
                    self.previous_zone[neighbor_state] = current_state
                    heapq.heappush(self.to_visit, (new_cost, neighbor_state))
        
        if final_zone_state is None:
            return []
            
        return self.reverse_path(final_zone_state)
    
    def reverse_path(self, final_zone_state: Tuple[str, int]) -> List[Tuple[str, int]]:
        """Walks previous_zone backwards to build the final path."""
        path: List[Tuple[str, int]] = []
        current: Optional[Tuple[str, int]] = final_zone_state

        while current is not None:
            path.append(current)
            current = self.previous_zone.get(current)

        path.reverse()
        return path