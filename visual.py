import arcade
from typing import Tuple, Dict ,List

class Visualizer(arcade.Window):
    def __init__(self, map_data) -> None:
        super().__init__(title="fly with your ass")
        self.map = map_data
        self.calculate_zone_space()

    def calculate_zone_space(self) -> None:
        first_zone = list(self.map.zones_by_name.values())[0]
        self.min_x, self.min_y = first_zone.position
        self.max_x, self.max_y = first_zone.position
        for zone in self.map.zones_by_name:
            x, y = self.map.zones_by_name[zone].position
            self.min_x = min(self.min_x, x)
            self.min_y = min(self.min_y, y)
            self.max_x = max(self.max_x, x)
            self.max_y = max(self.max_y, y)

    def on_draw(self) -> None:
        self.clear()  
        self.draw_connections()
        self.draw_zones()

    def on_update(self, delta_time: float) -> None:
        pass

    def draw_zones(self) -> None:
        for zone in self.map.zones_by_name.values():
            center_x, center_y = self.zone_to_screen(zone.position)
            color = getattr(arcade.color, zone.color.upper(), arcade.color.HOT_MAGENTA)
            arcade.draw_circle_filled(center_x, center_y, 15, color)

    def draw_connections(self) -> None:
        for connection in self.map.connections_by_name:
            start_x, start_y = self.zone_to_screen(self.map.connections_by_name[connection].zone1.position)
            end_x, end_y = self.zone_to_screen(self.map.connections_by_name[connection].zone2.position)
            arcade.draw_line(start_x, start_y, end_x, end_y, arcade.color.WHITE, 2)


    def zone_to_screen(self, position: Tuple[int, int]) -> Tuple[float, float]:
        x, y = position
        position_x = (x - self.min_x) / (self.max_x - self.min_x)
        screen_x = position_x * self.width

        position_y = (y - self.min_y) / (self.max_y - self.min_y)
        screen_y = position_y * self.height

        return screen_x, screen_y
    
    def build_turn_log(final_drones_paths: Dict[str, List[Tuple[str, int]]]) -> List[Dict[str, str]]:
        turn_log = {}
        for drone_id in final_drones_paths:
            for path in final_drones_paths[drone_id]:
                
