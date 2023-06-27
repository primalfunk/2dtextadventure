from collections import defaultdict, deque
import itertools
import json
import math
import random

class GameMap:
    def __init__(self, room_data, grid_width, grid_height, data_loader):
        self.data_loader = data_loader
        self.rooms = []
        self.room_clusters = {}
        self.room_data = room_data
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

        self.room_dict = {(x, y): None  for x in range(grid_width) for y in range(grid_height)}
    
    def add_room(self, room, x=None, y=None, cluster_id=None):
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
        for cluster1 in self.room_clusters.keys():
            for cluster2 in self.room_clusters.keys():
                if cluster1 != cluster2:
                    dist = self.distance_between_clusters(cluster1, cluster2)
                    edges.append((dist, cluster1, cluster2))
        edges.sort()
        self.mst = set()
        sets = {c: {c} for c in self.room_clusters.keys()}
        for edge in edges:
            dist, cluster1, cluster2 = edge
            if sets[cluster1] != sets[cluster2]:
                self.mst.add(edge)
                union = sets[cluster1].union(sets[cluster2])
                for c in union:
                    sets[c] = union
        for edge in self.mst:
            dist, cluster1, cluster2 = edge
            if self.are_clusters_adjacent(cluster1, cluster2):
                print(f"Connecting cluster {cluster1} and {cluster2} with distance {dist}")
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
            direction = self.get_direction(room1, room2)
            print(f"Attempting to connect room at ({room1.x},{room1.y}) in cluster {cluster_id1} to room at ({room2.x},{room2.y}) in cluster {cluster_id2} with direction {direction}")  # New print statement
            if self.connect_rooms(room1, room2, direction):
                print(f"Successfully connected rooms.")
                return
        print(f"Failed to connect clusters {cluster_id1} and {cluster_id2}.")

    def connect_rooms(self, room1, room2, direction):
        opposite = self.opposite_direction(direction)
        if self.is_connected(room1, room2):
            return
        room1.connected_rooms[direction] = room2
        room2.connected_rooms[opposite] = room1
        pos1 = (room1.x, room1.y)
        pos2 = (room2.x, room2.y)
        self.room_dict[pos1].connected_rooms[direction] = self.room_dict[pos2]
        self.room_dict[pos2].connected_rooms[opposite] = self.room_dict[pos1]

    def create_cluster(self, cluster_id, room_type, min_rooms_per_cluster, max_rooms_per_cluster, rooms_data):
        rooms_in_cluster = random.randint(min_rooms_per_cluster, max_rooms_per_cluster)
        room_queue = deque()
        visited_positions = set()  # Keep track of visited positions
        position = self.find_free_random_position()
        if position is None:
            print("No free positions available. Exiting.")
            return
        room_queue.append((None, position))
        visited_positions.add(position)  # Add the position to visited_positions
        for _ in range(rooms_in_cluster):
            while room_queue:
                current_room, current_pos = room_queue.popleft()
                created_directions = set()  # Keep track of directions in which rooms are created
                for direction in self.directions.keys():
                    if direction in created_directions:  # Skip the direction if a room has been created in this direction
                        continue
                    dx, dy, _ = self.directions[direction]
                    new_pos = current_pos[0] + dx, current_pos[1] + dy
                    if self.is_position_free(*new_pos) and new_pos not in visited_positions:  # Check if the position has been visited
                        new_room = self.generate_room(room_type, rooms_data, *new_pos)  # generate the room just before adding it
                        self.add_room(new_room, *new_pos, cluster_id)
                        if current_room is not None:  # skip connection if it's the first room in cluster
                            self.connect_rooms(current_room, new_room, direction)
                        room_queue.append((new_room, new_pos))
                        visited_positions.add(new_pos)  # Add the new_pos to visited_positions
                        created_directions.add(direction)  # Add the direction to created_directions
                        break
                else:
                    continue
                break
            else:
                print(f"Could not create all rooms for cluster {cluster_id}. Exiting.")
                return False
        return True
            
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

    def find_free_random_position(self):
        if not self.positions:
            print("No free positions available. Exiting.")
            return None
        return self.positions.pop()
        
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

    def generate_game_map(self, rooms_data, min_rooms_per_cluster, max_rooms_per_cluster, min_clusters, retry=True):
        self.rooms = []
        self.room_clusters = {}
        room_types = [data["type"] for data in rooms_data]
        self.rooms_data = rooms_data
        random.shuffle(room_types)
        self.generate_positions()
        num_clusters = min_clusters
        self.cluster_roots = [i for i in range(num_clusters)]
        cluster_ids = list(range(num_clusters))
        random.shuffle(cluster_ids)
        room_type_cycle = itertools.cycle((room_types))
        item_clusters = random.sample(cluster_ids, 6)
        game_key_item = self.generate_key(random.choice(self.data_loader.data["elements"]["puzzle_items"]))
        game_lock_item = self.generate_lock(random.choice(self.data_loader.data["elements"]["puzzle_items"]))
        game_weapon = self.generate_weapon(random.choice(self.data_loader.data["elements"]["weapons"]))
        game_armor = self.generate_armor(random.choice(self.data_loader.data["elements"]["armor"]))
        level = 1 # will update when implementing experience
        game_enemy = self.generate_character(random.choice(self.data_loader.data["elements"]["characters"]), level, True)
        game_ally = self.generate_character(random.choice(self.data_loader.data["elements"]["characters"]), level, False)
        healing = self.generate_healing(random.choice(self.data_loader.data["elements"]["healing"]))
        all_rooms = []
        for cluster_id in cluster_ids:
            room_type = next(room_type_cycle)
            cluster_created = self.create_cluster(cluster_id, room_type, min_rooms_per_cluster, max_rooms_per_cluster, rooms_data)
            if not cluster_created:
                print(f"Failed to create cluster {cluster_id}, skipping to next.")
                continue
            cluster_rooms = self.room_clusters[cluster_id]
            if cluster_id in item_clusters:
                if cluster_id == item_clusters[0]:
                    random.shuffle(cluster_rooms)
                    cluster_rooms[0].key_item = game_key_item
                elif cluster_id == item_clusters[1]:
                    random.shuffle(cluster_rooms)
                    cluster_rooms[0].lock_item = game_lock_item
                elif cluster_id == item_clusters[2]:
                    random.shuffle(cluster_rooms)
                    cluster_rooms[0].weapon = game_weapon
                elif cluster_id == item_clusters[3]:
                    random.shuffle(cluster_rooms)
                    cluster_rooms[0].armor = game_armor
                elif cluster_id == item_clusters[4]:
                    random.shuffle(cluster_rooms)
                    cluster_rooms[0].enemy = game_enemy
                elif cluster_id == item_clusters[5]:
                    random.shuffle(cluster_rooms)
                    cluster_rooms[0].ally = game_ally
            all_rooms.extend(cluster_rooms)
            if cluster_id == 0:
                self.set_player_start_room(cluster_rooms[0])
        self.connect_clusters()
        print(self.render_map())

    def generate_positions(self):
        positions = [(x, y) for x in range(self.grid_width) for y in range(self.grid_height)]
        random.shuffle(positions)
        self.positions = positions
    
    def generate_room(self, room_type, rooms_data, x, y):
        room_data = next((data for data in rooms_data if data["type"] == room_type))
        adjectives = room_data["adjectives"]
        names = room_data["name"]
        scenery = room_data["scenery"]
        atmosphere = room_data["atmosphere"]
        random.shuffle(adjectives)
        random.shuffle(names)
        random.shuffle(scenery)
        random.shuffle(atmosphere)
        unique_names = [f'{adj} {n}' for adj, n in zip(adjectives, names)]
        combined_scenery_atmosphere = list(zip(scenery, atmosphere))
        random.shuffle(combined_scenery_atmosphere)
        unique_descriptions = []
        for pair in combined_scenery_atmosphere:
            if random.random() < 0.5:
                pair = pair[::-1]
            unique_descriptions.append(f'{pair[0]} {pair[1]}')
        if len(self.rooms) < len(unique_names):
            name = unique_names[len(self.rooms)]
        else:
            available_names = list(set(unique_names) - set([room.name for room in self.rooms]))
            if available_names:
                name = random.choice(available_names)
            else:
                name = random.choice(unique_names)
        if len(self.rooms) < len(unique_descriptions):
            description = unique_descriptions[len(self.rooms) % len(unique_descriptions)]
        else:
            description = random.choice(unique_descriptions)
        room = Room(room_type, name, description, x, y)
        return room

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
            print(f"get_direction error: Rooms at ({room1.x},{room1.y}) and ({room2.x},{room2.y}) are not adjacent.")
            return "not connected"
    
    def is_adjacent(self, room1, room2):
        return (
            (abs(room1.x - room2.x) == 1 and room1.y == room2.y) or
            (abs(room1.y - room2.y) == 1 and room1.x == room2.x)
        )
    
    def is_connected(self, room1, room2):
        return room2 in room1.connected_rooms.values() and room1 in room2.connected_rooms.values()
    
    def is_position_free(self, x, y):
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return False
        for room in self.rooms:
            if room.x == x and room.y == y:
                return False
        return True
    
    @staticmethod
    def opposite_direction(direction):
        opposites = {"north": "south", "south": "north", "east": "west", "west": "east"}
        return opposites.get(direction, None)
    
    def possible_room_pairs_between_clusters(self, cluster_id1, cluster_id2):
        cluster1 = self.room_clusters[cluster_id1]
        cluster2 = self.room_clusters[cluster_id2]
        return [(room1, room2) for room1 in cluster1 for room2 in cluster2 if self.are_rooms_adjacent(room1, room2)]

    def set_player_start_room(self, room):
        self.player_start_room = room

    def render_map(self):
        rendered_map = [[' ' for _ in range(2*self.grid_width)] for _ in range(2*self.grid_height)]
        for room in self.rooms:
            if room is not None:
                # Display rooms
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
                    rendered_map[2*room.y][2*room.x] = '□'  # Or another symbol you prefer for generic rooms
                # Display connections
                for direction, connected_room in room.connected_rooms.items():
                    if connected_room is not None:
                        if direction == "north" and 2*room.y - 1 >= 0:
                            rendered_map[2*room.y - 1][2*room.x] = '|'
                        elif direction == "south" and 2*room.y + 1 < len(rendered_map):
                            rendered_map[2*room.y + 1][2*room.x] = '|'
                        elif direction == "west" and 2*room.x - 1 >= 0:
                            rendered_map[2*room.y][2*room.x - 1] = '-'
                        elif direction == "east" and 2*room.x + 1 < len(rendered_map[0]):
                            rendered_map[2*room.y][2*room.x + 1] = '-'
        # Return the rendered map as a multi-line string
        return '\n'.join([''.join(row) for row in rendered_map])


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
