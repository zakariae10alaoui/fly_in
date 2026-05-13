from typing import List, Dict, Optional, Tuple
from base_cls import CreateZone, CreateConnection, CreateDrone


class Map:
    """Central object that connects zones, connections, and drones together."""

    def __init__(
        self,
        nb_drones: int,
        start_zone: CreateZone,
        end_zone: CreateZone,
        zones: List[CreateZone],
        connections: List[CreateConnection],
    ) -> None:
        self.nb_drones: int = nb_drones
        self.start_zone: CreateZone = start_zone
        self.end_zone: CreateZone = end_zone
        self.zones: List[CreateZone] = zones 
        self.connections: List[CreateConnection] = connections
        self.drones: List[CreateDrone] = []
        self.zones_by_name: Dict[str, CreateZone] = {}
