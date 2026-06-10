from typing import Tuple
from typing import List, Tuple, Optional , Dict

class CreateZone:
    """Represents a location in the drone network."""
    
    def __init__(
        self, 
        name: str, 
        x: int, 
        y: int, 
        zone_type: Optional[str] = "normal", 
        max_drones: Optional[int] = 1, 
        color: Optional[str] = "none"
    ):
        self.name: str = name  
        self.position: Tuple[int, int] = (x, y) 
        self.color: str = color    
        self.zone_type: str = zone_type 
        self.max_drones: int = max_drones
        self.current_drones: List['CreateDrone'] = []

class CreateConnection:
    """Represents a bidirectional path between two zones."""
    
    def __init__(
        self, 
        zone1: CreateZone, 
        zone2: CreateZone, 
        max_link_capacity: int = 1
    ):
        self.zone1 = zone1
        self.zone2 = zone2 
        self.max_link_capacity: int = max_link_capacity 
        self.current_usage: int = 0 

class CreateDrone:
    """Represents a drone navigating the network."""
    
    def __init__(
        self, 
        drone_id: int, 
        start_zone: CreateZone
    ):
        self.drone_id: int = drone_id 
        self.current_zone: CreateZone = start_zone  
        self.in_transit_to: Optional[CreateZone] = None  
        self.turns_remaining: int = 0  
        self.delivered: bool = False 


class Map:
    """Central object that connects zones, connections, and drones together."""

    def __init__(
        self,
        nb_drones: int,
        start_zone: CreateZone,
        end_zone: CreateZone,
        zones_by_name: Dict[str, CreateZone],
        connections_by_name: Dict[str, CreateConnection],
    ) -> None:
        self.nb_drones = nb_drones
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.zones_by_name = zones_by_name
        self.connections_by_name = connections_by_name
        self.drones: List[CreateDrone] = []

    def get_neighbors_with_cost(self, current_zone: CreateZone) -> List[Tuple[CreateZone, int]]:
        """
        Finds all connected zones and calculates the turn cost to enter them.
        Returns a list of tuples: (NeighborZoneObject, cost_integer)
        """
        neighbors: List[Tuple[CreateZone, int]] = []
        
        for connection in self.connections_by_name.values():
            neighbor_zone = None
            
            if connection.zone1 == current_zone:
                neighbor_zone = connection.zone2
            elif connection.zone2 == current_zone:
                neighbor_zone = connection.zone1
                
            if neighbor_zone:
                cost = 2 if neighbor_zone.zone_type == "restricted" else 1
                
                if neighbor_zone.zone_type != "blocked":
                    neighbors.append((neighbor_zone, cost))
                    
        return neighbors

