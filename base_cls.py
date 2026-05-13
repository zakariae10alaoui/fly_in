from typing import Tuple
from typing import List, Tuple, Optional

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
        self.neighbors: List['CreateConnection'] = []

class CreateConnection:
    """Represents a bidirectional path between two zones."""
    
    def __init__(
        self, 
        zone1: CreateZone, 
        zone2: CreateZone, 
        max_link_capacity: int = 1
    ):
        self.zones: Tuple[CreateZone, CreateZone] = (zone1, zone2)  
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