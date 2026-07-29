import arcade
from typing import Tuple, Dict, List
from map_cls import Map


class Visualizer(arcade.Window):
    """Arcade Window class for rendering the map and drone movements."""

    def __init__(self, map_data: Map) -> None:
        """Initialize the visualizer window and HUD text."""
        super().__init__(title="Fly With Your mind", resizable=True)
        self.map: "Map" = map_data
        self.current_turn: int = 0
        self.is_moving: bool = False
        self.move_progress: float = 0.0
        self.max_turn: int = 0
        self.move_duration: float = 0.5
        self.previous_positions: Dict[int, str] = {}
        self.turn_log: Dict[int, Dict[int, str]] = {}
        self.maximize()
        self.calculate_zone_space()

        self.turn_text = arcade.Text(
            f"Turn: {self.current_turn}",
            self.width - 150,
            self.height - 30,
            arcade.color.WHITE,
            16,
        )

        self.zone_top_labels: Dict[str, arcade.Text] = {}
        self.zone_type_labels: Dict[str, arcade.Text] = {}

        for zone_name, zone in self.map.zones_by_name.items():
            self.zone_top_labels[zone_name] = arcade.Text(
                f"0/{zone.max_drones}",
                0,
                0,
                arcade.color.WHITE,
                9,
                bold=True,
            )
            self.zone_type_labels[zone_name] = arcade.Text(
                f"[{zone.zone_type}]",
                0,
                0,
                arcade.color.LIGHT_GRAY,
                10,
                anchor_x="center",
                anchor_y="top",
            )

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def calculate_zone_space(self) -> None:
        """Calculate the bounds of the map to center the view."""
        first_zone = list(self.map.zones_by_name.values())[0]
        self.min_x, self.min_y = first_zone.position
        self.max_x, self.max_y = first_zone.position

        for zone in self.map.zones_by_name.values():
            x, y = zone.position
            self.min_x = min(self.min_x, x)
            self.min_y = min(self.min_y, y)
            self.max_x = max(self.max_x, x)
            self.max_y = max(self.max_y, y)

    def on_draw(self) -> None:
        """Render the screen elements."""
        self.clear()
        self.draw_connections()
        self.draw_zones()
        self.draw_drones()
        self.draw_hud()

    def on_update(self, delta_time: float) -> None:
        """Update animation frames based on delta time."""
        if self.is_moving:
            self.move_progress += delta_time / self.move_duration
            if self.move_progress >= 1.0:
                self.move_progress = 1.0
                self.is_moving = False

    def on_resize(self, width: int, height: int) -> None:
        """Adjust HUD position upon window resize."""
        self.turn_text.x = width - 150
        self.turn_text.y = height - 30

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle user keyboard input."""
        if arcade.key.ESCAPE == symbol:
            self.close()

        if arcade.key.SPACE == symbol:
            max_turn = max(self.turn_log.keys(), default=0)
            if not self.is_moving and self.current_turn < max_turn:
                self.previous_positions = self.turn_log[self.current_turn]
                self.current_turn += 1
                self.turn_text.text = (
                    f"Turn: {self.current_turn} / {max_turn}"
                )
                self.move_progress = 0.0
                self.is_moving = True

    def get_current_occupancy(self) -> Dict[str, int]:
        """Calculate drone count per zone/connection in the current turn."""
        counts: Dict[str, int] = {}
        if self.current_turn in self.turn_log:
            for location in self.turn_log[self.current_turn].values():
                counts[location] = counts.get(location, 0) + 1
        return counts

    def draw_drones(self) -> None:
        """Interpolate and draw the drone circles."""
        if self.current_turn not in self.turn_log:
            return

        current_turn_data = self.turn_log[self.current_turn]
        for drone_id, current_location in current_turn_data.items():
            if current_location in self.map.connections_by_name:
                connection = self.map.connections_by_name[current_location]
                x1, y1 = self.zone_to_screen(connection.zone1.position)
                x2, y2 = self.zone_to_screen(connection.zone2.position)
                target_x = (x1 + x2) / 2
                target_y = (y1 + y2) / 2
            else:
                target_zone = self.map.zones_by_name[current_location]
                target_x, target_y = self.zone_to_screen(
                    target_zone.position
                )

            not_moved_yet = (
                self.current_turn == 0
                or drone_id not in self.previous_positions
            )
            if not_moved_yet:
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

                x_diff = (target_x - start_x) * self.move_progress
                y_diff = (target_y - start_y) * self.move_progress
                draw_x = start_x + x_diff
                draw_y = start_y + y_diff

            arcade.draw_circle_filled(draw_x, draw_y, 8, arcade.color.WHITE)

    def draw_hud(self) -> None:
        """Render the Heads Up Display elements."""
        self.turn_text.draw()

    def draw_zones(self) -> None:
        """Render the zone hubs and their textual labels."""
        occupancy = self.get_current_occupancy()
        for zone_name, zone in self.map.zones_by_name.items():
            center_x, center_y = self.zone_to_screen(zone.position)
            color = getattr(
                arcade.color, zone.color.upper(), arcade.color.HOT_MAGENTA
            )
            arcade.draw_circle_filled(center_x, center_y, 15, color)

            current_drones = occupancy.get(zone_name, 0)

            top_label = self.zone_top_labels[zone_name]
            top_label.text = f"{current_drones}/{zone.max_drones}"
            top_label.x = center_x
            top_label.y = center_y + 20
            top_label.draw()

            type_label = self.zone_type_labels[zone_name]
            type_label.x = center_x
            type_label.y = center_y - 25
            type_label.draw()

    def draw_connections(self) -> None:
        """Render the link paths connecting the zones."""
        for connection in self.map.connections_by_name.values():
            z1_pos = connection.zone1.position
            start_x, start_y = self.zone_to_screen(z1_pos)
            z2_pos = connection.zone2.position
            end_x, end_y = self.zone_to_screen(z2_pos)

            arcade.draw_line(
                start_x, start_y, end_x, end_y, arcade.color.BLACK, 2
            )

    def zone_to_screen(
        self, position: Tuple[int, int]
    ) -> Tuple[float, float]:
        """Convert logical grid coordinates to pixel screen coordinates."""
        x, y = position
        margin = 60

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

    def build_turn_log(
        self, final_drones_paths: Dict[int, List[Tuple[str, int]]]
    ) -> None:
        """Populate the turn_log with chronological steps for all drones."""

        if final_drones_paths:
            max_turn = max(
                path[-1][1] for path in final_drones_paths.values() if path
            )

        for drone_id, path in final_drones_paths.items():
            if not path:
                continue

            first_zone, first_turn = path[0]
            self.turn_log.setdefault(first_turn, {})[drone_id] = first_zone

            for step in range(len(path) - 1):
                from_zone, from_turn = path[step]
                to_zone, to_turn = path[step + 1]
                gap = to_turn - from_turn

                if gap == 1:
                    self.turn_log.setdefault(to_turn, {})[drone_id] = to_zone
                elif gap == 2:
                    conn_name = f"{from_zone}-{to_zone}"
                    if conn_name in self.map.connections_by_name:
                        connection_name = conn_name
                    else:
                        connection_name = f"{to_zone}-{from_zone}"

                    self.turn_log.setdefault(from_turn + 1, {})[
                        drone_id
                    ] = connection_name

                    self.turn_log.setdefault(to_turn, {})[drone_id] = to_zone

            last_zone, last_turn = path[-1]
            for t in range(last_turn + 1, max_turn + 1):
                self.turn_log.setdefault(t, {})[drone_id] = last_zone

    def format_turn_log(self) -> str:
        """Format the chronological move actions into a string payload."""
        lines = []
        for turn in range(len(self.turn_log)):
            current_turn = self.turn_log[turn]
            prev_turn = self.turn_log[turn - 1] if turn > 0 else {}
            movements = []

            for drone, location in current_turn.items():
                if prev_turn.get(drone) != location:
                    movements.append(f"D{drone}-{location}")

            lines.append(" ".join(movements))
        return "\n".join(lines)
