import sys
from typing import List, Dict, Set, Tuple, Any
from base_cls import CreateZone, CreateConnection


map_data: Dict[str, Any] = {}
zones_name: Set[str] = set()
seen_connections: Set[Tuple[str, str]] = set()

def parsing_hubs(data_str: str, hub_type: str, line_num: int) -> None:
    """Parses a hub definition and creates a Zone object."""
    second_part = data_str.split()

    if len(second_part) < 3:
        raise ValueError(f"Line {line_num}: Missing mandatory data (name, x, y).")

    name = second_part[0]
    if '-' in name:
        raise ValueError(f"Line {line_num}: Invalid zone name '{name}'. Names cannot contain dashes.")
    
    if name in zones_name:
        raise ValueError(f"Line {line_num}: Duplicate zone name '{name}'.")
    
    try:
        x, y = int(second_part[1]), int(second_part[2])
    except ValueError:
        raise ValueError(f"Line {line_num}: Coordinates must be integers.")

   
    color, zone_type, max_drones = "none", "normal", 1

    if len(second_part) == 4:
        meta_str = second_part[3]
        if not (meta_str.startswith("[") and meta_str.endswith("]")):
            raise ValueError(f"Line {line_num}: Metadata must be enclosed in brackets [...].")
        
        meta_items = meta_str.strip("[]").split()
        seen_keys = set()

        for item in meta_items:
            if '=' not in item:
                raise ValueError(f"Line {line_num}: Metadata items must use 'key=value' format.")
            key, value = item.split('=')
            
            if key in seen_keys:
                raise ValueError(f"Line {line_num}: Duplicate metadata key '{key}'.")
            seen_keys.add(key)

            if key == 'color':
                color = value
            elif key == 'zone':
                if value not in ['normal', 'blocked', 'restricted', 'priority']:
                    raise ValueError(f"Line {line_num}: Invalid zone type '{value}'.")
                zone_type = value
            elif key == 'max_drones':
                try:
                    max_drones = int(value)
                    if max_drones <= 0:
                        raise ValueError(f"Line {line_num}: 'max_drones' must be a positive integer.")
                except ValueError:
                    raise ValueError(f"Line {line_num}: 'max_drones' must be an integer.")

    
    hub = CreateZone(name, (x, y), color, max_drones, zone_type)
    if hub_type == "hub":
        map_data.setdefault("hub", []).append(hub)
    else:
        map_data[hub_type] = hub
    
    zones_name.add(name)



# if len(sys.argv) < 2:
#     print("Usage: python script.py <map_file>")
#     sys.exit(1)

try:
    with open("config.txt", 'r') as f:
        content = f.readlines()
except (PermissionError, FileNotFoundError) as e:
    print(f"File error: {e}")
    sys.exit(1)

try:
    for index, line in enumerate(content, 1):
        line = line.strip()
        
        if not line or line.startswith('#'):
            continue
        if "#" in line:
            line = line.split('#')[0].strip()
        
        if ':' not in line:
            raise ValueError(f"Line {index}: Missing colon separator.")
        
        prefix, data = line.split(':', 1)
        prefix, data = prefix.strip(), data.strip()

        
        if "nb_drones" not in map_data:
            if prefix != 'nb_drones':
                raise ValueError(f"Line {index}: The first line must define 'nb_drones'.")
            map_data["nb_drones"] = int(data)
            continue

        if prefix in ['hub', 'start_hub', 'end_hub']:
            if prefix in ['start_hub', 'end_hub'] and prefix in map_data:
                raise ValueError(f"Line {index}: Duplicate definition of {prefix}.")
            parsing_hubs(data, prefix, index)

        elif prefix == 'connection':
            parts = data.split()
            if '-' not in parts[0]:
                raise ValueError(f"Line {index}: Connection must use 'zone1-zone2' format.")
            
            z1, z2 = parts[0].split('-')
            if z1 not in zones_name or z2 not in zones_name:
                raise ValueError(f"Line {index}: Connection references undefined zone(s).")
            
            
            pair = tuple(sorted((z1, z2)))
            if pair in seen_connections:
                raise ValueError(f"Line {index}: Duplicate connection definition.")
            
            max_link = 1
            if len(parts) == 2:
                try:
                    val = parts[1].strip("[]").split('=')[1]
                    max_link = int(val)
                    if max_link <= 0:
                        raise ValueError(f"Line {index}: 'max_link_capacity' must be positive.")
                except (IndexError, ValueError):
                    raise ValueError(f"Line {index}: Invalid capacity metadata format.")

            connection = CreateConnection(z1, z2, max_link)
            seen_connections.add(pair)
            map_data.setdefault("connections", []).append(connection)

    
    if 'start_hub' not in map_data or 'end_hub' not in map_data:
        raise ValueError("Incomplete map: 'start_hub' and 'end_hub' are both required.")

except ValueError as e:
    print(f"Parsing error: {e}")
    sys.exit(1)

if map_data:
    print(map_data["nb_drones"])
    print(map_data["start_hub"])
    print(map_data["end_hub"])
    print(map_data["connections"])
else :
    print("nothing")