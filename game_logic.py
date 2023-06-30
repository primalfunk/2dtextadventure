from collections import defaultdict, deque
import itertools
import logging
import random

class GameMap:
    def __init__(self, rooms_data, grid_width, grid_height, data_loader):
        self.data_loader = data_loader
        self.max_retries = 10
        self.target_rooms = grid_width * grid_height
        self.rooms = []
        self.room_clusters = {}
        self.rooms_data = rooms_data
        self.player = Player()
        self.player_start_room = None
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.dx = {"north": 0, "south": 0, "east": 1, "west": -1}
        self.dy = {"north": -1, "south": 1, "east": 0, "west": 0}
        self.directions = {
        "north": (0, -1, "south"),
        "south": (0, 1, "north"),
        "east": (1, 0, "west"),
        "west": (-1, 0, "east"),
        }
        self.room_to_cluster_map = {}
        self.mst = set()
        self.frontier_positions = set()
        self.adj_cycle = self.init_cycle("adjectives")
        self.name_cycle = self.init_cycle("name")
        self.scenery_cycle = self.init_cycle("scenery")
        self.atmosphere_cycle = self.init_cycle("atmosphere")
        self.room_dict = {(x, y): None  for x in range(grid_width) for y in range(grid_height)}

    def init_cycle(self, field):
        logging.debug(f"Init_cycle called for {field}.")
        all_items = [data[field] for data in self.rooms_data]
        flattened_items = [item for sublist in all_items for item in sublist]
        random.shuffle(flattened_items)
        return itertools.cycle(flattened_items)

    def add_placeables(self, all_rooms):
        placeable_methods = [
            self.generate_key,
            self.generate_lock,
            self.generate_weapon,
            self.generate_armor,
            self.generate_character,
            self.generate_character
        ]
        game_data = {
            "key_item": random.choice(self.data_loader.data["elements"]["puzzle_items"]),
            "lock_item": random.choice(self.data_loader.data["elements"]["puzzle_items"]),
            "weapon": random.choice(self.data_loader.data["elements"]["weapons"]),
            "armor": random.choice(self.data_loader.data["elements"]["armor"]),
            "enemy": random.choice(self.data_loader.data["elements"]["characters"]),
            "ally": random.choice(self.data_loader.data["elements"]["characters"])
        }
        placeable_data = [
            game_data["key_item"],
            game_data["lock_item"],
            game_data["weapon"],
            game_data["armor"],
            (game_data["enemy"], 1, True),
            (game_data["ally"], 1, False)
        ]
        placeable_attributes = ["key_item", "lock_item", "weapon", "armor", "enemy", "ally"]
        if not all_rooms:
            logging.error("No rooms were generated. Cannot place items.")
            raise RuntimeError("No rooms were generated. Cannot place items.")
        possible_locations = all_rooms.copy()
        if self.player_start_room in possible_locations:
            possible_locations.remove(self.player_start_room)
        for method, data, attr in zip(placeable_methods, placeable_data, placeable_attributes):
            room = random.choice(possible_locations)
            if isinstance(data, tuple):
                placeable = method(*data)
            else:
                placeable = method(data)
            setattr(room, attr, placeable)
            logging.debug(f"Placeable method, data, attribute, room: {method}, {data}, {attr}, {room}")
            
            possible_locations.remove(room)
        logging.debug(self.render_map())
    
    def add_room(self, room, x=None, y=None, cluster_id=None):
        logging.debug(f"Trying to add room at position ({x},{y}) and cluster_id: {cluster_id}")
        if x is None or y is None:
            x, y = self.find_free_random_position()
        elif not self.is_position_free(x, y):
            raise Exception(f"Position {x}, {y} is not free.")
        room.x = x
        room.y = y
        room.cluster_id = cluster_id
        self.room_dict[(x, y)] = room
        self.rooms.append(room)
        if cluster_id is not None:
            if cluster_id in self.room_clusters:
                self.room_clusters[cluster_id].append(room)
            else:
                self.room_clusters[cluster_id] = [room]
            self.room_to_cluster_map[room] = cluster_id
        if (x,y) in self.positions:
            self.positions.remove((x, y))
        return room

    def calculate_direction(self, room1, room2):
        x1, y1 = room1.grid_position
        x2, y2 = room2.grid_position
        if x1 == x2:
            if y2 < y1:
                return "north"
            else:
                return "south"
        elif y1 == y2:
            if x2 < x1:
                return "west"
            else:
                return "east"
        else:
            raise ValueError("Rooms are not adjacent.")

    def calculate_distance(self, room1, room2):
        if isinstance(room1, Room):
            pos1 = (room1.x, room1.y)
        else:
            pos1 = room1

        if isinstance(room2, Room):
            pos2 = (room2.x, room2.y)
        else:
            pos2 = room2

        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        distance = dx + dy
        return distance

    def closest_rooms_between_clusters(self, cluster_id1, cluster_id2):
        cluster1 = self.room_clusters[cluster_id1]
        cluster2 = self.room_clusters[cluster_id2]

        min_distance = float('inf')
        closest_room1, closest_room2 = None, None
        for room1 in cluster1:
            for room2 in cluster2:
                distance = self.calculate_distance(room1, room2)
                if distance < min_distance and self.rooms_are_adjacent(room1, room2):  # New condition
                    min_distance = distance
                    closest_room1, closest_room2 = room1, room2

        return closest_room1, closest_room2

    def rooms_are_adjacent(self, room1, room2):
        return abs(room1.x - room2.x) + abs(room1.y - room2.y) == 1  # Return True only if rooms are adjacent

    def connect_clusters(self):
        edges = []
        logging.debug(f"Clusters: {self.room_clusters.keys()}")
        for cluster1 in self.room_clusters.keys():
            for cluster2 in self.room_clusters.keys():
                if cluster1 != cluster2:
                    dist = self.distance_between_clusters(cluster1, cluster2)
                    edges.append((dist, cluster1, cluster2))
        edges.sort()
        logging.debug(f"Edges: {edges}")
        self.mst = set()
        sets = {c: {c} for c in self.room_clusters.keys()}
        logging.debug(f"Sets: {sets}")
        for edge in edges:
            dist, cluster1, cluster2 = edge
            if sets[cluster1] != sets[cluster2]:
                self.mst.add(edge)
                union = sets[cluster1].union(sets[cluster2])
                for c in union:
                    sets[c] = union
            cluster2: logging.debug(f"Edge data: {dist}, {cluster1}, {cluster2}")
        for edge in self.mst:
            dist, cluster1, cluster2 = edge
            if self.are_clusters_adjacent(cluster1, cluster2):
                self.connect_cluster(cluster1, cluster2)

    def are_clusters_adjacent(self, cluster1_id, cluster2_id):
        cluster1 = self.room_clusters[cluster1_id]
        cluster2 = self.room_clusters[cluster2_id]
        for room1 in cluster1:
            for room2 in cluster2:
                if self.are_rooms_adjacent(room1, room2):
                    return True
        return False

    def are_rooms_adjacent(self, room1, room2):
        dx = abs(room1.x - room2.x)
        dy = abs(room1.y - room2.y)

        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

    def connect_cluster(self, cluster_id1, cluster_id2):
        room_pairs = self.possible_room_pairs_between_clusters(cluster_id1, cluster_id2)
        for room1, room2 in room_pairs:
            logging.info(f"Connecting clusters, room 1 {room1.x}, {room1.y} and room 2 {room2.x}, {room2.y}.")
            direction = self.get_direction(room1, room2)
            if self.connect_rooms(room1, room2, direction):
                return
            else:
                logging.error(f"Failed to connect the clusters.")

    def connect_rooms(self, room1, room2, direction):
        logging.info(f"Trying to connect room1 at ({room1.x}, {room1.y}) to room2 at ({room2.x}, {room2.y}) in the {direction} direction.")
        opposite = self.opposite_direction(direction)
        if self.is_connected(room1, room2):
            logging.info(f"Rooms at ({room1.x}, {room1.y}) and ({room2.x}, {room2.y}) are already connected.")
            return
        room1.connected_rooms[direction] = room2
        room2.connected_rooms[opposite] = room1
        pos1 = (room1.x, room1.y)
        pos2 = (room2.x, room2.y)
        self.room_dict[pos1].connected_rooms[direction] = self.room_dict[pos2]
        self.room_dict[pos2].connected_rooms[opposite] = self.room_dict[pos1]
        logging.info(f"Rooms at ({room1.x}, {room1.y}) and ({room2.x}, {room2.y}) have been connected.")
        return True

    def create_and_place_items(self, all_rooms):
        item_types = ["armor", "weapon", "enemy", "ally", "key_item", "lock_item"]
        possible_locations = all_rooms.copy()  # Copy the list so we don't modify the original
        possible_locations.remove(self.player_start_room)  # Remove player's starting room from possible locations
        for item_type in item_types:
            item = self.create_item(item_type)  # Assuming you have a method for item creation
            room = random.choice(possible_locations)  # Choose a random room from the possible locations
            room.add_item(item)  # Add the item to the chosen room
            possible_locations.remove(room)

    def create_cluster(self, room_type, cluster_id):
        self.frontier_positions.clear()
        logging.info(f"Attempting to create cluster {cluster_id} with room type {room_type}")
        start_position = self.find_free_random_position(start_center=cluster_id == 0)
        logging.debug(f"Start position found: {start_position}")
        if start_position is None:
            logging.error("Failed to find a free random position.")
            return False
        start_room = self.generate_room(room_type, *start_position)
        self.add_room(start_room, *start_position, cluster_id)
        logging.info(f"Start room for cluster {cluster_id} created at {start_position}")
        self.frontier_positions = list(self.get_free_adjacent_positions(start_position, cluster_id))
        logging.info(f"Initial frontier positions for cluster {cluster_id}: {self.frontier_positions}")
        rooms_in_cluster = 1
        cluster_target = random.randint(3, 8)
        while self.frontier_positions and rooms_in_cluster < cluster_target:
            # Choose the first position in the list (frontier_positions)
            logging.debug(f"Current state of frontier_positions: {bool(self.frontier_positions)}")
            logging.debug(f"Current number of rooms in cluster: {rooms_in_cluster}")
            logging.debug(f"Target number of rooms in cluster: {cluster_target}")
            position = self.frontier_positions.pop(0)
            new_room = self.generate_room(room_type, *position)
            self.add_room(new_room, *position, cluster_id)
            rooms_in_cluster += 1
            logging.debug(f"Added room at {position}. Rooms in cluster: {rooms_in_cluster}")

            new_positions = self.get_free_adjacent_positions(position, cluster_id)
            self.frontier_positions.extend(new_positions)
            logging.info(f"Updated frontier positions for cluster {cluster_id}: {self.frontier_positions}")
        logging.info(f"Cluster creation result: {rooms_in_cluster >= 1}")
        return rooms_in_cluster >= 1
    
    def distance_between_clusters(self, cluster_id1, cluster_id2):
        cluster1 = self.room_clusters[cluster_id1]
        cluster2 = self.room_clusters[cluster_id2]
        min_distance = float('inf')
        for room1 in cluster1:
            for room2 in cluster2:
                distance = self.calculate_distance(room1, room2)
                min_distance = min(distance, min_distance)

        return min_distance

    def distance_to_cluster(self, position, cluster_id):
        x, y = position
        cluster = self.room_clusters[cluster_id]
        min_distance = min(self.calculate_distance((x, y), (room.x, room.y)) for room in cluster)
        return min_distance

    def favor_square_cluster(self, current_pos, visited_positions):
        dx_min = min(pos[0] for pos in visited_positions)
        dx_max = max(pos[0] for pos in visited_positions)
        dy_min = min(pos[1] for pos in visited_positions)
        dy_max = max(pos[1] for pos in visited_positions)

        width = dx_max - dx_min
        height = dy_max - dy_min

        if width > height:
            favored_directions = ["north", "south"]
        else:
            favored_directions = ["east", "west"]

        return favored_directions

    def find_adjacent_cluster(self, cluster_id, cluster_rooms):
        adjacent_cluster_id = None
        min_distance = float('inf')
        closest_room1, closest_room2 = None, None
        for room1 in cluster_rooms:
            for room2 in self.rooms:
                if room2 in cluster_rooms or room2 in room1.connected_rooms.values() or self.room_to_cluster_map[room2] == cluster_id:
                    continue
                distance = self.calculate_distance(room1, room2)
                if distance < min_distance:
                    min_distance = distance
                    closest_room1, closest_room2 = room1, room2
                    adjacent_cluster_id = self.room_to_cluster_map[room2]
        return adjacent_cluster_id, closest_room1, closest_room2

    def find_adjacent_rooms(self, cluster_rooms1, cluster_rooms2):
        adjacent_rooms = set()
        for room1 in cluster_rooms1:
            x1, y1 = room1.x, room1.y
            for dx, dy, _ in self.directions.values():
                x2, y2 = x1 + dx, y1 + dy
                if 0 <= x2 < self.grid_width and 0 <= y2 < self.grid_height:
                    room2 = self.grid[x2][y2]
                    if room2 in cluster_rooms2:
                        adjacent_rooms.add((room1, room2))
        return adjacent_rooms

    def find_closest_cluster(self, current_cluster_id, current_cluster_rooms):
        min_distance = float('inf')
        closest_cluster_id = None
        closest_room = None
        closest_room_in_current_cluster = None
        for cluster_id, cluster_rooms in self.room_clusters.items():
            if cluster_id != current_cluster_id:
                for room1 in current_cluster_rooms:
                    for room2 in cluster_rooms:
                        distance = abs(room1.x - room2.x) + abs(room1.y - room2.y)
                        if distance < min_distance:
                            min_distance = distance
                            closest_cluster_id = cluster_id
                            closest_room = room2
                            closest_room_in_current_cluster = room1
        return closest_cluster_id, closest_room, closest_room_in_current_cluster
    
    def find_closest_rooms(self, rooms1, rooms2):
        closest_distance = float('inf')
        closest_room1 = None
        closest_room2 = None
        for room1 in rooms1:
            for room2 in rooms2:
                distance = self.calculate_distance(room1, room2)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_room1 = room1
                    closest_room2 = room2
        return closest_room1, closest_room2

    def find_free_position_near_existing_room(self):
        room_positions = [(room.x, room.y) for room in self.rooms]
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if (x, y) in room_positions:
                    continue
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if (x + dx, y + dy) in room_positions:
                        free_space = 0
                        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            if (x + dx + ddx, y + dy + ddy) not in room_positions:
                                free_space += 1
                        if free_space >= 2:
                            return x, y
        raise Exception("Could not find free position near existing room")

    def find_free_position_next_to_room(self, room):
        max_range = max(self.grid_width, self.grid_height)
        for dx in range(-max_range, max_range + 1):
            for dy in range(-max_range, max_range + 1):
                x, y = room.x + dx, room.y + dy
                if self.is_position_free(x, y):
                    return x, y
        raise Exception("Could not find free position next to room")

    def find_free_random_position(self, start_center=False):
        logging.debug(f"Finding free random position. Start center: {start_center}")
        if start_center:
            x, y = self.grid_width // 2, self.grid_height // 2
            logging.debug(f"Checking position: ({x}, {y})")
            if self.is_position_free(x, y):
                return (x, y)
        elif self.frontier_positions:
            for position in random.sample(self.frontier_positions, len(self.frontier_positions)):
                logging.debug(f"Checking position: {position}")
                if self.is_position_free(*position):
                    return position
        else:
            free_positions = [pos for pos in self.positions if self.is_position_free(*pos)]
            if free_positions:
                return random.choice(free_positions)
        logging.debug("No free random position found.")
        return None
        
    def find_room_not_in_list(self, room_list):
        available_rooms = [room for room in self.rooms if room not in room_list]
        if available_rooms:
            return random.choice(available_rooms)
        else:
            raise Exception("No available rooms to place item/character.")

    def find_room_with_free_connection(self, room):
        if room is None:
            return False
        free_directions = [direction for direction in room.available_connections() 
                           if self.is_position_free(*room.get_position_in_direction(direction))]
        return len(free_directions) > 0
    
    def generate_key(self, key_data):
        return Key(key_data["key_item"], key_data["lock_item"])

    def generate_lock(self, lock_data):
        return Lock(lock_data["lock_item"], lock_data["key_item"])

    def generate_healing(self, healing_data):
        return Healing(healing_data["type"], healing_data["stats"]["hp"])

    def generate_weapon(self, weapon_data):
        return Weapon(weapon_data["type"], weapon_data["stats"]["damage"])

    def generate_armor(self, armor_data):
        return Armor(armor_data["type"], armor_data["stats"]["defense"])

    def generate_character(self, character_data, level, isEnemy = True):
        return Character(character_data["type"],
                         level,
                         character_data["stats"]["hp"], 
                         character_data["stats"]["atk"], 
                         character_data["stats"]["defp"], 
                         character_data["stats"]["acc"], 
                         character_data["stats"]["ev"])

    def generate_game_map(self, rooms_data):
        self.rooms = []
        self.room_clusters = {}
        room_types = [data["type"] for data in rooms_data]
        self.rooms_data = rooms_data
        random.shuffle(room_types)
        self.generate_positions()
        self.cluster_roots = []
        room_type_cycle = itertools.cycle((room_types))
        all_rooms = []
        cluster_id = 0
        while self.is_map_full is False:
            logging.debug(f"Current state of is_map_full: {self.is_map_full}")
            room_type = next(room_type_cycle)
            logging.info(f"Attempting to create cluster {cluster_id} with room type {room_type}")
            cluster_created = self.create_cluster(room_type, cluster_id)

            logging.info(f"Cluster creation result: {cluster_created}")
            cluster_id += 1
            if not cluster_created:
                print(f"Failed to create cluster {cluster_id-1}, skipping to next.")
                continue
            cluster_rooms = self.room_clusters[cluster_id-1]
            if cluster_id == 1 and cluster_rooms:
                logging.info(f"Setting player start room: {cluster_rooms[0].x}, {cluster_rooms[0].y}")
                self.set_player_start_room(cluster_rooms[0])
                logging.info(f"The player's start room is: {self.player_start_room.x}, {self.player_start_room.y}")
            all_rooms.extend(cluster_rooms)
            logging.debug(f"All rooms after extending cluster_rooms: {all_rooms}")
        self.connect_clusters()
        # self.add_placeables(all_rooms)
        # print(self.render_map())
        if self.is_map_full:
            logging.info("Game map successfully generated.")
            return True
        logging.error("Game map generation failed.")
        return False


    def generate_positions(self):
        positions = [(x, y) for x in range(self.grid_width) for y in range(self.grid_height)]
        random.shuffle(positions)
        self.positions = positions
    
    def generate_room(self, room_type, x, y):
        logging.debug(f"generate_room called with room_type={room_type}, x={x}, y={y}")
        adjective = next(self.adj_cycle)
        name = next(self.name_cycle)
        scene = next(self.scenery_cycle)
        atmos = next(self.atmosphere_cycle)
        unique_name = f'{adjective} {name}'
        unique_description = f'{scene} {atmos}'
        room = Room(room_type, unique_name, unique_description, x, y)
        return room

    def get_free_adjacent_positions(self, position, cluster_id):
        x, y = position
        possible_positions = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        return [pos for pos in possible_positions if self.is_position_in_map(pos) and self.is_position_free(*pos) and pos not in self.frontier_positions and self.is_adjacent_to_cluster(pos, cluster_id)]
    
    def is_adjacent_to_cluster(self, position, cluster_id):
        x, y = position
        possible_positions = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        return any(self.room_dict.get(pos, None) and self.room_dict[pos].cluster_id == cluster_id for pos in possible_positions)
    
    def is_position_in_map(self, position):
        x, y = position
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height

    def get_direction(self, room1, room2):
        dx = room2.x - room1.x
        dy = room2.y - room1.y

        if dx == 1 and dy == 0:
            return "east"
        elif dx == -1 and dy == 0:
            return "west"
        elif dx == 0 and dy == 1:
            return "south"
        elif dx == 0 and dy == -1:
            return "north"
        else:
            return "not connected"
    
    def is_adjacent(self, room1, room2):
        return (
            (abs(room1.x - room2.x) == 1 and room1.y == room2.y) or
            (abs(room1.y - room2.y) == 1 and room1.x == room2.x)
        )
    
    def is_connected(self, room1, room2):
        return room2 in room1.connected_rooms.values() and room1 in room2.connected_rooms.values()
    
    @property
    def is_map_full(self):
        return len(self.positions) == 0

    def is_position_free(self, x, y):
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return False
        for room in self.rooms:
            if room.x == x and room.y == y:
                return False
        return True
    
    def is_position_free_in_cluster(self, x, y, cluster_id):
        # Checking if the position is free
        if not self.is_position_free(x, y):
            return False
        # Checking the neighboring positions
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            neighbor = self.room_dict.get((nx, ny))
            if neighbor and neighbor.cluster_id == cluster_id:
                return True

        return False
    
    @staticmethod
    def opposite_direction(direction):
        opposites = {"north": "south", "south": "north", "east": "west", "west": "east"}
        return opposites.get(direction, None)
    
    def possible_room_pairs_between_clusters(self, cluster_id1, cluster_id2):
        cluster1 = self.room_clusters[cluster_id1]
        cluster2 = self.room_clusters[cluster_id2]
        room_pairs = [(room1, room2) for room1 in cluster1 for room2 in cluster2 if self.are_rooms_adjacent(room1, room2)]
        logging.info(f"Possible room pairs between cluster {cluster_id1} and cluster {cluster_id2} are: {room_pairs}")
        return room_pairs

    def set_player_start_room(self, room):
        self.player_start_room = room

    def render_fancy_map(self):
        rendered_map = [[' ' for _ in range(2*self.grid_width)] for _ in range(2*self.grid_height)]
        for room in self.rooms:
            if room is None:
                logging.warning(f"Room at position ({room.x}, {room.y} is None)")
            
            if room is not None:
                # Display rooms
                logging.info(f"Rendering room at position ({room.x}, {room.y}).")
                if room == self.player.current_room:
                    rendered_map[2*room.y][2*room.x] = 'P'
                elif room.enemy:
                    rendered_map[2*room.y][2*room.x] = 'E'
                elif room.weapon:
                    rendered_map[2*room.y][2*room.x] = 'W'
                elif room.armor:
                    rendered_map[2*room.y][2*room.x] = 'A'
                elif room.key_item:
                    rendered_map[2*room.y][2*room.x] = 'K'
                elif room.lock_item:
                    rendered_map[2*room.y][2*room.x] = 'L'
                elif room.ally:
                    rendered_map[2*room.y][2*room.x] = 'Y'
                else:
                    rendered_map[2*room.y][2*room.x] = 'X'  # Or another symbol you prefer for generic rooms
                # Display connections
                for direction, connected_room in room.connected_rooms.items():
                                        
                    if connected_room is not None:
                        logging.info(f"Rendering connection from room at ({room.x}, {room.y}) to room at ({connected_room.x}, {connected_room.y}).")
                        if direction == "north" and 2*room.y - 1 >= 0:
                            rendered_map[2*room.y - 1][2*room.x] = '|'
                        elif direction == "south" and 2*room.y + 1 < len(rendered_map):
                            rendered_map[2*room.y + 1][2*room.x] = '|'
                        elif direction == "west" and 2*room.x - 1 >= 0:
                            rendered_map[2*room.y][2*room.x - 1] = '-'
                        elif direction == "east" and 2*room.x + 1 < len(rendered_map[0]):
                            rendered_map[2*room.y][2*room.x + 1] = '-'
                    else:
                        pass

        # Return the rendered map as a multi-line string
        return '\n'.join([''.join(row) for row in rendered_map])

    def render_map(self):
        rendered_grid = [[' ']*self.grid_width for _ in range(self.grid_height)]
        for (x, y), room in self.room_dict.items():
            if room is not None:
                rendered_grid[y][x] = 'X'
        rendered_map = '\n'.join(''.join(row) for row in rendered_grid)
        return rendered_map

class Room:
    def __init__(self, room_type, name, description, x=0, y=0):
        self.type = room_type
        self.name = name
        self.description = description
        self.connected_rooms = defaultdict(lambda: None, {"north": None, "south": None, "east": None, "west": None})
        self.x = x
        self.y = y
        self.grid_position = (x, y)
        self.key_item = None
        self.lock_item = None
        self.enemy = None
        self.ally = None
        self.weapon = None
        self.armor = None
        if name != "":
            self.symbol = name[0]
        else:
            self.symbol = " "

    def __str__(self):
        item_descriptions = []
        if self.key_item:
            item_descriptions.append(f"You see a {self.key_item.name} here.")
        if self.lock_item:
            item_descriptions.append(f"You see a {self.lock_item.name} here.")
        if self.weapon:
            item_descriptions.append(f"You see a {self.weapon.name} here.")
        if self.armor:
            item_descriptions.append(f"You see a {self.armor.name} here.")
        if self.enemy:
            item_descriptions.append(f"You see a {self.enemy.name} here.")
        if self.ally:
            item_descriptions.append(f"You see a {self.ally.name} here.")
        item_descriptions_str = "\n".join(item_descriptions)
        connections = {direction: (room.name if isinstance(room, Room) else room) for direction, room in self.connected_rooms.items()}
        room_str = f"{self.name} ({self.type}): {self.description}\n\nItems: {item_descriptions_str}\n\nConnections: {connections}"
        return room_str

    def __lt__(self, other):
        if self.y != other.y:
            return self.y < other.y
        else:
            return self.x < other.x

    @property
    def id(self):
        return f"{self.x}-{self.y}"

    def available_connections(self):
            possible_directions = ["north", "south", "east", "west"]
            return [direction for direction in possible_directions if self.connected_rooms[direction] is None]

    def get_room_with_free_direction(self, possible_directions=None):
        if possible_directions is None:
            possible_directions = ["north", "south", "east", "west"]
        random.shuffle(possible_directions)
        for direction in possible_directions:
            if self.connected_rooms[direction] is None:
                return direction
        return None
   
class Item:
    def __init__(self, name, details):
        self.name = name
        self.details = details

class Healing:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp

class Key(Item):
    def __init__(self, name, unlock_room):
        super().__init__(name, "This key can unlock " + unlock_room)
        self.unlock_room = unlock_room

class Lock(Item):
    def __init__(self, name, locked_room):
        super().__init__(name, "This lock can be opened with a key for " + locked_room)
        self.locked_room = locked_room

class Weapon(Item):
    def __init__(self, name, damage):
        super().__init__(name, "This weapon can cause " + str(damage) + " points of damage.")
        self.damage = damage

class Armor(Item):
    def __init__(self, name, defense):
        super().__init__(name, "This armor can defend against " + str(defense) + " points of damage.")
        self.defense = defense

class Character:
    def __init__(self, name, level, hp, atk, defp, acc, ev):
        self.level = level
        self.name = name
        self.hp = hp
        self.atk = atk
        self.defp = defp
        self.acc = acc
        self.ev = ev
        self.inventory = []
        self.current_room = None
        self.x = 0
        self.y = 0
        self.is_enemy = None

    def add_item(self, item):
        self.inventory.append(item)
        if isinstance(item, Weapon):
            self.atk += item.damage
        elif isinstance(item, Armor):
            self.defp += item.defense

class Player(Character):
    def __init__(self):
        super().__init__(name="Player", level=1, hp=100, atk=10, defp=10, acc=50, ev=50)
        self.is_enemy = False
        self.xp = 0
