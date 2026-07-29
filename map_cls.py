from typing import List, Tuple, Optional, Dict


class CreateZone:
    """Represents a location in the drone network."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        max_drones: int = 1,
        color: str = "none",
    ) -> None:
        """Initialize a new zone."""
        self.name: str = name
        self.position: Tuple[int, int] = (x, y)
        self.color: str = color
        self.zone_type: str = zone_type
        self.max_drones: int = max_drones


class CreateConnection:
    """Represents a bidirectional path between two zones."""

    def __init__(
        self, zone1: CreateZone, zone2: CreateZone, max_link_capacity: int = 1
    ) -> None:
        """Initialize a connection between two zones."""
        self.zone1: CreateZone = zone1
        self.zone2: CreateZone = zone2
        self.max_link_capacity: int = max_link_capacity


class CreateDrone:
    """Represents a drone navigating the network."""

    def __init__(self, drone_id: int, start_zone: CreateZone) -> None:
        """Initialize a drone with its starting zone."""
        self.drone_id: int = drone_id
        self.current_zone: CreateZone = start_zone


class Map:
    """Central object that connects zones, connections, and drones together."""

    def __init__(
        self,
        nb_drones: int,
        start_zone: CreateZone,
        end_zone: CreateZone,
        zones_by_name: Dict[str, CreateZone],
        connections_by_name: Dict[str, CreateConnection],
        drones: List[CreateDrone],
    ) -> None:
        """Initialize the map with its components."""
        self.nb_drones: int = nb_drones
        self.start_zone: CreateZone = start_zone
        self.end_zone: CreateZone = end_zone
        self.zones_by_name: Dict[str, CreateZone] = zones_by_name
        self.connections_by_name: Dict[
            str, CreateConnection
        ] = connections_by_name
        self.drones: List[CreateDrone] = drones

    def get_neighbors_with_cost(
        self, current_zone: CreateZone
    ) -> List[Tuple[float, CreateZone]]:
        """
        Find all connected zones and calculate the turn cost to enter them.

        Returns:
            A list of tuples containing (cost_float, NeighborZoneObject).
        """
        neighbors: List[Tuple[float, CreateZone]] = []
        for connection in self.connections_by_name.values():
            neighbor_zone = None
            if connection.zone1.name == current_zone.name:
                neighbor_zone = connection.zone2
            elif connection.zone2.name == current_zone.name:
                neighbor_zone = connection.zone1

            if neighbor_zone:
                if neighbor_zone.zone_type == "blocked":
                    continue
                if neighbor_zone.zone_type == "restricted":
                    cost = 2.0
                elif neighbor_zone.zone_type == "priority":
                    cost = 0.9
                else:
                    cost = 1.0
                neighbors.append((cost, neighbor_zone))

        return neighbors

    def is_solvable(self) -> bool:
        """Check if there is any valid path from start_zone to end_zone."""
        visited = {self.start_zone.name}
        queue = [self.start_zone]
        while queue:
            current = queue.pop(0)
            for _, neighbor in self.get_neighbors_with_cost(current):
                if neighbor.name not in visited:
                    visited.add(neighbor.name)
                    if neighbor.name == self.end_zone.name:
                        return True
                    queue.append(neighbor)
        return self.end_zone.name in visited

    def get_zone(self, name: str) -> Optional[CreateZone]:
        """Look up any zone by name, including start and end zones."""
        if self.start_zone.name == name:
            return self.start_zone
        if self.end_zone.name == name:
            return self.end_zone
        return self.zones_by_name.get(name)
