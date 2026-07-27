from typing import Dict, Tuple , List
from map_cls import Map

class TheEngine:
    def __init__(self,map : Map) -> None:
        self.map = map
        self.zone_bookings: Dict[Tuple[str, int], int] = {}
        self.link_bookings: Dict[Tuple[str, str, int], int] = {}
        self.final_drones_paths = {}

    def get_link_key(self, zone_a: str, zone_b: str, turn: int) -> Tuple[str, str, int]:
        """
        Normalizes connection identifiers alphabetically so that direction 
        (A->B or B->A) maps to the exact same reservation slot on a specific turn.
        """
        if zone_a < zone_b:
            return (zone_a, zone_b, turn)
        return (zone_b, zone_a, turn)

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        """Increments the scheduled drone count for a specific zone and turn."""
        key = (zone_name, turn)
        self.zone_bookings[key] = self.zone_bookings.get(key, 0) + 1

    def reserve_link(self, zone_a: str, zone_b: str, turn: int) -> None:
        """Increments the scheduled traffic count for a connection link at a specific turn."""
        key = self.get_link_key(zone_a, zone_b, turn)
        self.link_bookings[key] = self.link_bookings.get(key, 0) + 1

    def is_zone_available(self, zone_name: str, turn: int) -> bool:
        """
        Returns True if the zone has space available at the given turn.
        Returns False if the zone is already full.
        """
        if zone_name == self.map.start_zone.name or zone_name == self.map.end_zone.name:  
            return True
            
        key = (zone_name, turn)
        current_capacity = self.zone_bookings.get(key, 0)
        
        if current_capacity < self.map.zones_by_name[zone_name].max_drones:
            return True
        
        return False
    
    def is_link_available(self, zone_a: str, zone_b: str, turn: int) -> bool:
        """
        Returns True if the connection link has available capacity at the given turn.
        """
        booking_key = self.get_link_key(zone_a, zone_b, turn)
        current_traffic = self.link_bookings.get(booking_key, 0)
        
        forward_key = f"{zone_a}-{zone_b}"
        
        if forward_key in self.map.connections_by_name:
            connection_obj = self.map.connections_by_name[forward_key]
        else:
            backward_key = f"{zone_b}-{zone_a}"
            connection_obj = self.map.connections_by_name[backward_key]
            
        max_capacity = connection_obj.max_link_capacity
        
        return current_traffic < max_capacity
    
    def drive_all_drones(self, pathfinder: 'PathFinder') -> None:
        """
        Iterates through drones one by one, finds their safe space-time path, 
        and immediately updates reservations.
        """
        for drone in self.map.drones:
            safe_path = pathfinder.calculate_short_path(self)
            
            if not safe_path:
                print(f"Warning: No valid safe path found for {drone.drone_id}!")
                continue
                
            self.final_drones_paths[drone.drone_id] = safe_path
            
            for i in range(len(safe_path)):
                current_zone, current_turn = safe_path[i]
                
                self.reserve_zone(current_zone,current_turn)
                
                if i < len(safe_path) - 1:
                    next_zone, next_turn = safe_path[i + 1]
                    if current_zone != next_zone:
                        gap = next_turn - current_turn
                        for t in range(gap):
                            self.reserve_link(current_zone, next_zone, current_turn + t)
