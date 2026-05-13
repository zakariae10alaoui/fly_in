import sys
from typing import List, Dict, Set, Tuple, Any, Optional
from base_cls import CreateZone, CreateConnection
from fly_in import Map


class MapParser:
    """Parses a drone map configuration file and builds a Map object."""

    def __init__(self, filepath: str) -> None:
        """Initialize the parser with the path to the map file.

        Args:
            filepath: Path to the map configuration file.
        """
        self.filepath: str = filepath
        self._map_data: Dict[str, Any] = {}
        self._zones_by_name: Dict[str, CreateZone] = {}
        self._seen_connections: Set[Tuple[str, str]] = set()

    def parse(self) -> Map:
        """Read and parse the full map file, returning a Map object.

        Returns:
            A fully built Map instance.
        """
        content = self._read_file()
        self._parse_lines(content)
        return self._build_map()

    # ------------------------------------------------------------------ #
    #  Private: file reading                                               #
    # ------------------------------------------------------------------ #

    def _read_file(self) -> List[str]:
        """Open and read the map file.

        Returns:
            List of raw lines from the file.
        """
        try:
            with open(self.filepath, 'r') as f:
                return f.readlines()
        except (PermissionError, FileNotFoundError) as e:
            print(f"File error: {e}")
            sys.exit(1)

    # ------------------------------------------------------------------ #
    #  Private: line dispatching                                           #
    # ------------------------------------------------------------------ #

    def _parse_lines(self, content: List[str]) -> None:
        """Iterate over lines and dispatch each to the correct handler.

        Args:
            content: List of raw lines from the file.
        """
        try:
            for index, line in enumerate(content, 1):
                line = line.strip()

                if not line or line.startswith('#'):
                    continue
                if '#' in line:
                    line = line.split('#')[0].strip()

                if ':' not in line:
                    raise ValueError(f"Line {index}: Missing colon separator.")

                prefix, data = line.split(':', 1)
                prefix, data = prefix.strip(), data.strip()

                if "nb_drones" not in self._map_data:
                    if prefix != 'nb_drones':
                        raise ValueError(
                            f"Line {index}: First line must define 'nb_drones'."
                        )
                    try:
                        nb = int(data)
                        if nb <= 0:
                            raise ValueError()
                    except ValueError:
                        raise ValueError(
                            f"Line {index}: 'nb_drones' must be a positive integer."
                        )
                    self._map_data["nb_drones"] = nb
                    continue

                if prefix in ['hub', 'start_hub', 'end_hub']:
                    if prefix in ['start_hub', 'end_hub'] and prefix in self._map_data:
                        raise ValueError(
                            f"Line {index}: Duplicate definition of '{prefix}'."
                        )
                    self._parse_hub(data, prefix, index)

                elif prefix == 'connection':
                    self._parse_connection(data, index)

                else:
                    raise ValueError(f"Line {index}: Unknown prefix '{prefix}'.")

            if 'start_hub' not in self._map_data or 'end_hub' not in self._map_data:
                raise ValueError(
                    "Incomplete map: 'start_hub' and 'end_hub' are both required."
                )

        except ValueError as e:
            print(f"Parsing error: {e}")
            sys.exit(1)

    # ------------------------------------------------------------------ #
    #  Private: hub parsing                                                #
    # ------------------------------------------------------------------ #

    def _parse_hub(self, data_str: str, hub_type: str, line_num: int) -> None:
        """Parse a hub line and store the resulting Zone.

        Args:
            data_str: The part of the line after the prefix colon.
            hub_type: One of 'hub', 'start_hub', 'end_hub'.
            line_num: Current line number for error messages.
        """
        parts = data_str.split()

        if len(parts) < 3:
            raise ValueError(
                f"Line {line_num}: Missing mandatory fields (name, x, y)."
            )

        name = parts[0]
        if '-' in name:
            raise ValueError(
                f"Line {line_num}: Zone name '{name}' cannot contain dashes."
            )
        if name in self._zones_by_name:
            raise ValueError(
                f"Line {line_num}: Duplicate zone name '{name}'."
            )

        try:
            x, y = int(parts[1]), int(parts[2])
        except ValueError:
            raise ValueError(
                f"Line {line_num}: Coordinates must be integers."
            )

        color, zone_type, max_drones = "none", "normal", 1

        if len(parts) >= 4:
            color, zone_type, max_drones = self._parse_zone_metadata(
                parts[3], line_num
            )

        # matches CreateZone(name, x, y, zone_type, max_drones, color)
        zone = CreateZone(name, x, y, zone_type, max_drones, color)

        if hub_type == "hub":
            self._map_data.setdefault("hub", []).append(zone)
        else:
            self._map_data[hub_type] = zone

        self._zones_by_name[name] = zone

    def _parse_zone_metadata(
        self, meta_str: str, line_num: int
    ) -> Tuple[str, str, int]:
        """Parse the metadata block of a zone line.

        Args:
            meta_str: Raw metadata string e.g. '[zone=restricted color=red]'.
            line_num: Current line number for error messages.

        Returns:
            Tuple of (color, zone_type, max_drones).
        """
        if not (meta_str.startswith('[') and meta_str.endswith(']')):
            raise ValueError(
                f"Line {line_num}: Metadata must be enclosed in brackets [...]."
            )

        color, zone_type, max_drones = "none", "normal", 1
        seen_keys: Set[str] = set()

        for item in meta_str.strip('[]').split():
            if '=' not in item:
                raise ValueError(
                    f"Line {line_num}: Metadata must use 'key=value' format."
                )
            key, value = item.split('=', 1)

            if key in seen_keys:
                raise ValueError(
                    f"Line {line_num}: Duplicate metadata key '{key}'."
                )
            seen_keys.add(key)

            if key == 'color':
                color = value
            elif key == 'zone':
                if value not in ['normal', 'blocked', 'restricted', 'priority']:
                    raise ValueError(
                        f"Line {line_num}: Invalid zone type '{value}'."
                    )
                zone_type = value
            elif key == 'max_drones':
                try:
                    max_drones = int(value)
                    if max_drones <= 0:
                        raise ValueError()
                except ValueError:
                    raise ValueError(
                        f"Line {line_num}: 'max_drones' must be a positive integer."
                    )
            else:
                raise ValueError(
                    f"Line {line_num}: Unknown zone metadata key '{key}'."
                )

        return color, zone_type, max_drones

    # ------------------------------------------------------------------ #
    #  Private: connection parsing                                         #
    # ------------------------------------------------------------------ #

    def _parse_connection(self, data: str, line_num: int) -> None:
        """Parse a connection line and store the resulting Connection.

        Args:
            data: The part of the line after 'connection:'.
            line_num: Current line number for error messages.
        """
        parts = data.split()

        if '-' not in parts[0]:
            raise ValueError(
                f"Line {line_num}: Connection must use 'zone1-zone2' format."
            )

        z1_name, z2_name = parts[0].split('-', 1)

        if z1_name not in self._zones_by_name:
            raise ValueError(
                f"Line {line_num}: Unknown zone '{z1_name}'."
            )
        if z2_name not in self._zones_by_name:
            raise ValueError(
                f"Line {line_num}: Unknown zone '{z2_name}'."
            )

        pair: Tuple[str, str] = tuple(sorted((z1_name, z2_name)))  # type: ignore
        if pair in self._seen_connections:
            raise ValueError(
                f"Line {line_num}: Duplicate connection '{z1_name}-{z2_name}'."
            )

        max_link = 1
        if len(parts) == 2:
            max_link = self._parse_connection_metadata(parts[1], line_num)

        # pass actual Zone objects since CreateConnection expects them
        zone_a = self._zones_by_name[z1_name]
        zone_b = self._zones_by_name[z2_name]

        connection = CreateConnection(zone_a, zone_b, max_link)
        self._seen_connections.add(pair)
        self._map_data.setdefault("connections", []).append(connection)

    def _parse_connection_metadata(
        self, meta_str: str, line_num: int
    ) -> int:
        """Parse the metadata block of a connection line.

        Args:
            meta_str: Raw metadata string e.g. '[max_link_capacity=2]'.
            line_num: Current line number for error messages.

        Returns:
            The max_link_capacity value.
        """
        if not (meta_str.startswith('[') and meta_str.endswith(']')):
            raise ValueError(
                f"Line {line_num}: Metadata must be enclosed in brackets [...]."
            )

        try:
            key, value = meta_str.strip('[]').split('=', 1)
        except ValueError:
            raise ValueError(
                f"Line {line_num}: Invalid connection metadata format."
            )

        if key != 'max_link_capacity':
            raise ValueError(
                f"Line {line_num}: Unknown connection metadata key '{key}'."
            )

        try:
            max_link = int(value)
            if max_link <= 0:
                raise ValueError()
        except ValueError:
            raise ValueError(
                f"Line {line_num}: 'max_link_capacity' must be a positive integer."
            )

        return max_link

    # ------------------------------------------------------------------ #
    #  Private: build the final Map object                                 #
    # ------------------------------------------------------------------ #

    def _build_map(self) -> Map:
        """Assemble and return the Map from parsed data.

        Returns:
            A fully constructed Map instance.
        """
        return Map(
            nb_drones=self._map_data["nb_drones"],
            start_zone=self._map_data["start_hub"],
            end_zone=self._map_data["end_hub"],
            zones=self._map_data.get("hub", []),
            connections=self._map_data.get("connections", []),
        )