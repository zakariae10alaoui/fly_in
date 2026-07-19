# try:
#     with open("config.txt",'r') as config_file:
#         content = config_file.readlines()
#         print(content)
# except (PermissionError , FileNotFoundError) as e:
#     print(e)
# line = "end_hub: goal 10 10 [color=yellow] #comment".split('#')[0].strip()
# print(line)
# map_data = {}
# map_data.setdefault("connections").append("trrr")
# print(map_data["connections"])

# same corrconate

# same connection zonex zonex

# color single word
# line = " ltltltl: ltltltltee333:444"
# line = line.split(':', 1)
# print(line)


# pair = tuple(sorted(("roof1", "roof2"))) 
# print(pair)
# pair = tuple(sorted(("roof2", "roof1"))) 
# print(pair)

# neighbors problem in map class
# t = float("inf")
# if t > 100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000:
#     print("true")
# else:
#     print("false")

# import heapq
# tt = []

# heapq.heappush(tt, (43,5))
# heapq.heappush(tt, (43,56))
# print(tt)
# heapq.heappush(tt, (43,54))
# print(tt)
# print(heapq.heappop(tt))

# tt = [1,2,3,4,5]
# tt.reverse()

# print(tt)





#    while self.to_visit:
#             current_cost, current_zone_name = heapq.heappop(self.to_visit)
#             print(f"\n--- POP: '{current_zone_name}' (cost={current_cost}) ---")

#             if current_zone_name == end_name:
#                 print(f"  → reached END zone '{end_name}', stopping.")
#                 break

#             if current_cost > self.zone_distances[current_zone_name]:
#                 print(f"  → outdated entry, skip.")
#                 continue

#             current_zone_obj = self.map.get_zone(current_zone_name)
#             if current_zone_obj is None:
#                 print(f"  → zone '{current_zone_name}' not found, skip.")
#                 continue

#             for  move_cost ,neighbor_zone in self.map.get_neighbors_with_cost(current_zone_obj):
#                 neighbor_name = neighbor_zone.name
#                 new_cost = current_cost + float(move_cost)

#                 print(f"  neighbor '{neighbor_name}': new_cost={new_cost}, known={self.zone_distances[neighbor_name]}")

#                 if new_cost < self.zone_distances[neighbor_name]:
#                     self.zone_distances[neighbor_name] = new_cost
#                     self.previous_zone[neighbor_name] = current_zone_name
#                     heapq.heappush(self.to_visit, (new_cost, neighbor_name))
#                     print(f"    → UPDATED: distances['{neighbor_name}']={new_cost}, previous='{current_zone_name}'")
#                     print(f"    → PUSHED: ({new_cost}, '{neighbor_name}') to to_visit")
#                 else:
#                     print(f"    → no update, existing path is cheaper or equal")

#         print(f"\n--- FINAL distances: {self.zone_distances} ---")
#         print(f"--- FINAL previous:  {self.previous_zone} ---")


x  = min(-1,0)
print(x)