from typing import Dict, Tuple

class TheEngine:
    def __init__(self) -> None:
        self.zone_bookings: Dict[Tuple[str, int], int] = {}
        
        self.link_bookings: Dict[Tuple[str, str, int], int] = {}

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

    def release_zone(self, zone_name: str, turn: int) -> None:
        """Decrements the scheduled drone count, cleaning up the key if it drops to 0."""
        key = (zone_name, turn)
        if key in self.zone_bookings:
            self.zone_bookings[key] -= 1
            if self.zone_bookings[key] <= 0:
                del self.zone_bookings[key]

    def reserve_link(self, zone_a: str, zone_b: str, turn: int) -> None:
        """Increments the scheduled traffic count for a connection link at a specific turn."""
        key = self.get_link_key(zone_a, zone_b, turn)
        self.link_bookings[key] = self.link_bookings.get(key, 0) + 1

    def release_link(self, zone_a: str, zone_b: str, turn: int) -> None:
        """Decrements the scheduled traffic count for a connection link, cleaning up keys at 0."""
        key = self.get_link_key(zone_a, zone_b, turn)
        if key in self.link_bookings:
            self.link_bookings[key] -= 1
            if self.link_bookings[key] <= 0:
                del self.link_bookings[key]