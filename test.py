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

import heapq
tt = []

heapq.heappush(tt, (43,5))
heapq.heappush(tt, (43,56))
print(tt)
heapq.heappush(tt, (43,54))
print(tt)
print(heapq.heappop(tt))