*This project has been created as part of the 42 curriculum by zel-alao.*

# fly_in

A drone traffic simulator that routes a fleet of drones across a network
of zones and connections, guaranteeing that no zone or link is ever used
beyond its declared capacity at any given moment in time, and then
replays the result as an animated 2D visualization.

## Description

`fly_in` reads a small text-based map description — a set of named
**zones** (hubs), the **connections** between them, and a number of
drones to route — and computes, for every drone, a collision-free path
from the `start_hub` to the `end_hub`.

The core difficulty of the project is that drones don't move in a
vacuum: a zone can only hold so many drones at once, a link between two
zones can only carry so much traffic at once, and some zones behave
differently (slower to cross, cheaper to cross, or entirely forbidden).
The engine has to find a path for every drone while respecting all of
these constraints simultaneously, turn after turn.

Once every drone has a path, the project opens a window (via the
`arcade` library) that visually replays the whole simulation: zones,
links, drone positions, and how occupancy evolves turn by turn.

In short, the project is split into four responsibilities:

- **Parsing** a map file into an in-memory graph (`map_parsing.py`,
  `map_cls.py`).
- **Pathfinding** a single drone's optimal route through space and time
  (`dijkstra.py`).
- **Orchestrating** all drones one after another, keeping track of who
  reserved what and when (`engine.py`).
- **Visualizing** the resulting schedule (`visual.py`).

## Instructions

### Requirements

- Python 3.10+
- [`arcade`](https://api.arcade.academy/) `3.3.3` (listed in
  `requirements.txt`)

### Installation

```bash
make install
```

This simply runs `pip install -r requirements.txt`.

### Running

```bash
make run
```

By default this runs the simulation on the bundled `config.txt` map. To
run a different map:

```bash
make run MAP=path/to/your_map.txt
```

which is equivalent to:

```bash
python3 fly_in.py path/to/your_map.txt
```

Once the window opens, press **SPACE** to advance to the next turn and
watch the drones move, and **ESC** to close the window.

### Other Makefile targets

| Target        | Description                                              |
|---------------|-----------------------------------------------------------|
| `make debug`  | Runs the program under `pdb` for step-by-step debugging.  |
| `make lint`   | Runs `flake8` and `mypy` (strict, untyped defs disallowed) over the whole codebase. |
| `make clean`  | Removes `__pycache__` and `.mypy_cache` directories.       |

### Map file format

A map file is a plain text file, parsed line by line:

- `nb_drones: <int>` — must be the first meaningful line, sets the
  number of drones to simulate.
- `start_hub: <name> <x> <y> [metadata]` — the drone departure zone.
- `end_hub: <name> <x> <y> [metadata]` — the drone destination zone.
- `hub: <name> <x> <y> [metadata]` — any intermediate zone.
- `connection: <zoneA>-<zoneB> [metadata]` — a bidirectional link
  between two zones.

Metadata is an optional, space-separated `key=value` list wrapped in
brackets:

- For zones: `color=<name>`, `zone=<normal|blocked|restricted|priority>`,
  `max_drones=<int>`.
- For connections: `max_link_capacity=<int>`.

Comments start with `#` and blank lines are ignored.

## Algorithm Choices and Implementation Strategy

### Modeling movement as space-time

Rather than searching a plain graph of zones, the pathfinder searches
a graph of **states**, where each state is a pair `(zone, turn)`. This
"space-time" (or "time-expanded") representation is what makes it
possible to reason about capacity: two drones occupying the same zone
at *different* turns is fine, but the same zone at the *same* turn is
only allowed up to that zone's `max_drones`. The same idea applies to
links and `max_link_capacity`.

From any state `(zone, turn)`, a drone can:

- **Wait** in place, moving to `(zone, turn + 1)`, as long as the zone
  is still available at the next turn.
- **Move** to a neighboring zone, moving to `(neighbor, turn + 1)` for
  a `normal` or `priority` neighbor, or `(neighbor, turn + 2)` for a
  `restricted` neighbor (it takes an extra turn to cross, and both
  turns spent on the connecting link must be free). `blocked` zones are
  never offered as a neighbor at all.

### Dijkstra over the space-time graph

`PathFinder` (`dijkstra.py`) runs a classic Dijkstra's algorithm on top
of that state graph, using a binary heap (`heapq`) as the priority
queue. Edge costs are not uniform: `priority` zones are cheaper to
enter (`0.9`), `restricted` zones are more expensive (`2.0`, reflecting
the extra turn), waiting in place has a small penalty (`1.1`, so the
algorithm prefers making progress over stalling when both are
otherwise valid), and `normal` moves cost `1.0`. This lets the search
naturally favor the fastest, least congested route rather than a
purely shortest-hop one.

### Sequential (greedy) multi-drone scheduling

Solving optimal *joint* routing for every drone at once is
computationally expensive, so `TheEngine` (`engine.py`) uses a simpler,
practical strategy: drones are routed **one at a time**, in order. Each
drone's Dijkstra search takes the *current* reservation state into
account (through `is_zone_available` / `is_link_available`), so it will
naturally route around zones and links that earlier drones have
already booked at a given turn. Once a drone's path is found, its zone
and link usage for every turn along that path is immediately reserved
(`reserve_zone` / `reserve_link`), so the next drone's search sees an
up-to-date picture of the network.

This greedy, first-come-first-served approach doesn't guarantee a
globally optimal schedule for the whole fleet, but it guarantees that
every drone that finds a path is guaranteed collision- and
capacity-safe with respect to all previously scheduled drones, and it
keeps the algorithm fast and simple to reason about.

### Map validation

Before any pathfinding happens, `Map.is_solvable()` runs a quick
breadth-first search from the start zone to confirm the end zone is
even reachable, so obviously impossible maps fail fast with a clear
error message instead of silently producing empty results.

## Visual Representation

The visualization (`visual.py`) is built on top of `arcade.Window` and
serves two purposes: making the simulation's result tangible, and
making it easy to spot *why* a particular routing decision was made.

- **Zones** are drawn as colored circles (using the zone's declared
  `color`, defaulting to a very visible fallback for typos or unknown
  colors), positioned automatically from the grid coordinates in the
  map file and scaled to fill the window. Each zone displays two live
  labels: the current occupancy versus its capacity (e.g. `2/3`) above
  the circle, and its zone type (e.g. `[restricted]`) below it — so
  congestion and special zones are visible at a glance.
- **Connections** are drawn as straight lines between the zones they
  join, giving an immediate view of the network's topology.
- **Drones** are drawn as small circles that smoothly interpolate
  between their previous and current position over the course of a
  turn's animation, rather than jumping instantly — this makes
  simultaneous drone movement across the network much easier to follow
  visually, including drones that are mid-flight on a `restricted` link
  spanning two turns.
- **Turn navigation** is manual: pressing `SPACE` advances the
  simulation by one turn (and only if a next turn actually exists),
  which lets the user inspect each step of the schedule at their own
  pace instead of watching a fixed-speed playback. A HUD text element
  in the top-right corner always shows the current turn out of the
  total number of turns.
- Internally, `build_turn_log` converts each drone's raw
  `(zone, turn)` path into a per-turn "who is where" snapshot,
  including an explicit in-transit state (`zoneA-zoneB`) for the extra
  turn spent crossing a `restricted` link, and pads each drone's
  entry at its final zone for any remaining turns so that drones which
  arrive early are still shown correctly once the last drone lands.

Together, these choices turn a purely textual scheduling result into an
interactive, readable animation of the whole fleet's journey.

## Resources

### Classic references

- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html) —
  the priority queue used by the Dijkstra implementation.
- [Arcade library documentation](https://api.arcade.academy/) —
- [dikjstar youtube video ](https://youtu.be/XB4MIexjvY0?si=mQKQSfa8MX8mkjGw) —



### AI usage

An AI assistant (Claude, by Anthropic) was used during this project as
a coding aid, specifically for:

- **Linting clean-up**: reformatting existing, already-working code to
  fix `flake8` line-length (`E501`) violations and `mypy` type errors
  (e.g. narrowing `Optional` types, fixing a `Tuple` type inference
  issue), without changing program logic.
