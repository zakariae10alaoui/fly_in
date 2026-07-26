import arcade
from typing import Tuple, Dict ,List

class Visualizer(arcade.Window):
    def __init__(self, map_data) -> None:
        super().__init__(title="fly with your ass" ,resizable=True)
        self.map = map_data
        self.current_turn = 0
        self.is_moving = False
        self.move_progress: float = 0.0
        self.move_duration: float = 0.5
        self.previous_positions = {}
        self.turn_log = {}
        self.maximize()
        self.calculate_zone_space()
        self.turn_text = arcade.Text(f"Turn: {self.current_turn}", self.width - 100,self.height - 30 , arcade.color.WHITE , 16)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

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
            self.draw_drones()
            self.draw_hud()

    def on_update(self, delta_time: float) -> None:
        if self.is_moving:
            self.move_progress += delta_time / self.move_duration
            if self.move_progress >= 1.0:
                self.move_progress = 1.0
                self.is_moving = False  

    def on_resize(self, width, height):
        self.turn_text.x, self.turn_text.y = width - 100,height - 30

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if arcade.key.ESCAPE == symbol:
            self.close()
        if arcade.key.SPACE == symbol:
            if not self.is_moving and self.current_turn < max(self.turn_log):
                self.previous_positions = self.turn_log[self.current_turn]   
                self.current_turn += 1
                self.turn_text.text = f"Turn: {self.current_turn}"
                self.move_progress = 0.0
                self.is_moving = True


    def draw_drones(self) -> None:
        if self.current_turn not in self.turn_log:
            return

        for drone_id, current_location in self.turn_log[self.current_turn].items():

            if current_location in self.map.connections_by_name:
                connection = self.map.connections_by_name[current_location]
                x1, y1 = self.zone_to_screen(connection.zone1.position)
                x2, y2 = self.zone_to_screen(connection.zone2.position)
                target_x = (x1 + x2) / 2
                target_y = (y1 + y2) / 2
            else:
                target_zone = self.map.zones_by_name[current_location]
                target_x, target_y = self.zone_to_screen(target_zone.position)

            if self.current_turn == 0 or drone_id not in self.previous_positions:
                draw_x, draw_y = target_x, target_y
            else:
                prev_location = self.previous_positions[drone_id]
                if prev_location in self.map.connections_by_name:
                    prev_conn = self.map.connections_by_name[prev_location]
                    px1, py1 = self.zone_to_screen(prev_conn.zone1.position)
                    px2, py2 = self.zone_to_screen(prev_conn.zone2.position)
                    start_x = (px1 + px2) / 2
                    start_y = (py1 + py2) / 2
                else:
                    prev_zone = self.map.zones_by_name[prev_location]
                    start_x, start_y = self.zone_to_screen(prev_zone.position)

                draw_x = start_x + (target_x - start_x) * self.move_progress
                draw_y = start_y + (target_y - start_y) * self.move_progress

            arcade.draw_circle_filled(draw_x, draw_y, 8, arcade.color.WHITE)

    def draw_hud(self) -> None:
        self.turn_text.draw()
        # arcade.draw_text(f"Turn: {self.current_turn}", self.width - 100, self.height - 30, arcade.color.WHITE, 16)

    def draw_zones(self) -> None:
        if self.current_turn not in self.turn_log:
            return

        for zone in self.map.zones_by_name.values():
            center_x, center_y = self.zone_to_screen(zone.position)
            color = getattr(arcade.color, zone.color.upper(), arcade.color.HOT_MAGENTA)
            arcade.draw_circle_filled(center_x, center_y, 15, color)

    def draw_connections(self) -> None:
        for connection in self.map.connections_by_name:
            start_x, start_y = self.zone_to_screen(self.map.connections_by_name[connection].zone1.position)
            end_x, end_y = self.zone_to_screen(self.map.connections_by_name[connection].zone2.position)
            arcade.draw_line(start_x, start_y, end_x, end_y, arcade.color.BLACK, 2)



    def zone_to_screen(self, position: Tuple[int, int]) -> Tuple[float, float]:
        x, y = position
        margin = 40

        if self.max_x == self.min_x:
            screen_x = self.width / 2
        else:
            position_x = (x - self.min_x) / (self.max_x - self.min_x)
            usable_width = self.width - (2 * margin)
            screen_x = margin + (position_x * usable_width)

        if self.max_y == self.min_y:
            screen_y = self.height / 2
        else:
            position_y = (y - self.min_y) / (self.max_y - self.min_y)
            usable_height = self.height - (2 * margin)
            screen_y = margin + (position_y * usable_height)

        return screen_x, screen_y
    
    def build_turn_log(self, final_drones_paths: Dict[str, List[Tuple[str, int]]]) -> Dict[int, Dict[str, str]]:
        for drone_id, path in final_drones_paths.items():
            first_zone, first_turn = path[0]
            self.turn_log.setdefault(first_turn, {})[drone_id] = first_zone

            for step in range(len(path) - 1):
                from_zone, from_turn = path[step]
                to_zone, to_turn = path[step + 1]
                gap = to_turn - from_turn

                if gap == 1:
                    self.turn_log.setdefault(to_turn, {})[drone_id] = to_zone

                elif gap == 2:
                    if f"{from_zone}-{to_zone}" in self.map.connections_by_name:
                        connection_name = f"{from_zone}-{to_zone}"
                    else:
                        connection_name = f"{to_zone}-{from_zone}"
                    self.turn_log.setdefault(from_turn + 1, {})[drone_id] = connection_name
                    self.turn_log.setdefault(to_turn, {})[drone_id] = to_zone


    def format_turn_log(self) -> str:
        lines = []
            
        for turn in range(len(self.turn_log)):
            current_turn = self.turn_log[turn]
            prev_turn = self.turn_log[turn - 1] if turn > 0 else {}
            movements = []
            movements.append(f"TURN : {turn}")
            for drone, location in current_turn.items():
                    if prev_turn.get(drone) != location:
                        movements.append(f"D{drone}-{location}")

            line = " ".join(movements)
            lines.append(line)

        return "\n".join(lines)