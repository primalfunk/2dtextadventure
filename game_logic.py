from collections import defaultdict, deque
import itertools
import json
import math
from prims import Prims
import random
import sys

class GameMap:
    def __init__(self, grid_width, grid_height):
        self.rooms = []
        self.room_clusters = {}
        self.player = Player()
        self.player_start_room = None
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.grid = [[None] * grid_height for _ in range(grid_width)]
        self.directions = {
        "north": (0, -1, "south"),
        "south": (0, 1, "north"),
        "east": (1, 0, "west"),
        "west": (-1, 0, "east"),
    }

    def add_room(self, room, x=None, y=None):
        if x is None or y is None:
            x, y = self.find_free_random_position()
        elif not self.is_position_free(x, y):
            raise Exception(f"Position {x}, {y} is not free.")
        room.x = x
        room.y = y
        self.grid[x][y] = room
        self.rooms.append(room)

    def calculate_direction(self, room1, room2):
        dx, dy = room2.x - room1.x, room2.y - room1.y
        if dx > 0:
            return "east"
        elif dx < 0:
            return "west"
        elif dy > 0:
            return "north"
        else:  # dy < 0
            return "south"

    def calculate_distance(self, room1, room2):
        dx = room1.x - room2.x
        dy = room1.y - room2.y
        return math.sqrt(dx**2 + dy**2)

    def connect_clusters(self):
        self.cluster_roots = list(range(len(self.room_clusters)))
        clusters_not_connected = set(range(len(self.room_clusters)))
        print("Connect: Initial clusters_not_connected:", clusters_not_connected)
        while len(clusters_not_connected) != 1:
            for cluster_id in list(clusters_not_connected):
                print(f"Connect: Current cluster ID: {cluster_id}")
                cluster_rooms = self.room_clusters[cluster_id]
                closest_cluster_id, closest_room, closest_room_in_current_cluster = self.find_closest_cluster(cluster_id, cluster_rooms)
                print(f"Connect: Closest cluster ID: {closest_cluster_id}")
                if closest_cluster_id is not None and closest_cluster_id in clusters_not_connected:
                    direction = self.calculate_direction(closest_room_in_current_cluster, closest_room)
                    self.connect_rooms(closest_room_in_current_cluster, closest_room, direction)
                    self.union(cluster_id, closest_cluster_id)
                    clusters_not_connected.discard(closest_cluster_id)
                else:
                    clusters_not_connected.discard(cluster_id)
                print(f"Connect: Cluster_ID: {cluster_id}")
                print(f"Connect: Clusters_not_connected: {clusters_not_connected}")
                print(f"Connect: Closest_cluster_id: {closest_cluster_id}")
                
                if closest_cluster_id is None:
                    break
            if len(clusters_not_connected) == 1:
                cluster_ids = list(clusters_not_connected)
                cluster_id = cluster_ids[0]
                cluster_rooms = self.room_clusters[cluster_id]
                closest_room1, closest_room2 = self.find_closest_rooms(cluster_rooms, cluster_rooms)
                direction = self.calculate_direction(closest_room1, closest_room2)
                self.connect_rooms(closest_room1, closest_room2, direction)

        print("Connect: Final clusters_not_connected:", clusters_not_connected)

    def connect_rooms(self, room1, room2, direction):
        sys.setrecursionlimit(3000)
        # Create a queue to store the rooms that need to be connected.
        queue = []
        queue.append(room1)

        while queue:
            current_room = queue.pop(0)
            print(current_room.id)

            # For each room that is connected to the current room,
            # add the room to the queue if it has not already been connected.
            for connected_room in current_room.connected_rooms.values():
                if connected_room not in queue:
                    queue.append(connected_room)

            # Connect the current room to the room in the specified direction.
            self.connect_rooms(current_room, room2, direction)

    def create_cluster(self, cluster_id, room_type, min_rooms_per_cluster, max_rooms_per_cluster, rooms_data):
        rooms_in_cluster = random.randint(min_rooms_per_cluster, max_rooms_per_cluster)
        cluster_rooms = []
        root_room = self.generate_room(room_type, rooms_data)
        cluster_rooms.append(root_room)
        queue = deque(cluster_rooms)
        print(f"Create: Cluster ID: {cluster_id}, Rooms in Cluster: {rooms_in_cluster + 1}")
        while rooms_in_cluster > 0 and queue:
            current_room = queue.popleft()
            for direction, (dx, dy, opposite) in self.directions.items():
                new_x, new_y = current_room.x + dx, current_room.y + dy
                if (
                    0 <= new_x < self.grid_width
                    and 0 <= new_y < self.grid_height
                    and self.grid[new_x][new_y] is None
                ):
                    new_room = self.generate_room(room_type, rooms_data)
                    self.add_room(new_room)
                    self.connect_rooms(current_room, new_room, direction)
                    queue.append(new_room)
                    rooms_in_cluster -= 1
                    cluster_rooms.append(new_room)
                    if rooms_in_cluster <= 0:
                        break
        print(f"Create: Cluster ID: {cluster_id}, Number of Rooms: {len(cluster_rooms)}")
        print(f"Create: Cluster ID: {cluster_id}, Remaining Rooms in Cluster: {rooms_in_cluster}")
        self.room_clusters[cluster_id] = cluster_rooms
            
    def find(self, cluster):
        if self.cluster_roots[cluster] != cluster:
            self.cluster_roots[cluster] = self.find(self.cluster_roots[cluster])
        return self.cluster_roots[cluster]

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
        print(f"Find: Closest cluster ID: {closest_cluster_id}")
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
        free_positions = [(x, y) for x in range(self.grid_width) for y in range(self.grid_height) if self.grid[x][y] is None]
        return random.choice(free_positions)
    
    def find_room_not_in_list(self, room_list):
        available_rooms = [room for room in self.rooms if room not in room_list]
        if available_rooms:
            return random.choice(available_rooms)
        else:
            raise Exception("No available rooms to place item/character.")

    def find_room_with_free_connection(self, rooms):
        for room in rooms:
            if len(room.connected_rooms) < 4:
                return room
        return None
    
    def generate_key(self, key_data):
        return Key(key_data["key_item"], key_data["lock_item"])

    def generate_lock(self, lock_data):
        return Lock(lock_data["lock_item"], lock_data["key_item"])

    def generate_weapon(self, weapon_data):
        return Weapon(weapon_data["type"], weapon_data["stats"]["damage"])

    def generate_armor(self, armor_data):
        return Armor(armor_data["type"], armor_data["stats"]["defense"])

    def generate_character(self, character_data, is_enemy=True):
        return Character(character_data["type"], character_data["stats"]["hit_points"], character_data["stats"]["attack_points"], character_data["stats"]["defense_points"])

    def generate_game_map(self, rooms_data, min_rooms_per_cluster, max_rooms_per_cluster, min_clusters):
        self.rooms = []
        self.room_clusters = {}
        room_types = [data["type"] for data in rooms_data]
        random.shuffle(room_types)
        remaining_room_types = room_types.copy()
        if min_clusters > len(room_types):
            min_clusters = len(room_types)
        num_clusters = random.randint(min_clusters, min(len(room_types), min_clusters))
        self.cluster_roots = [i for i in range(num_clusters)]
        cluster_ids = list(range(num_clusters))
        random.shuffle(cluster_ids)
        room_type_cycle = itertools.cycle(room_types)
        item_clusters = random.sample(cluster_ids, 6)  # List of 6 random cluster ids
        json_data = json.load(open("fantasy.json"))
        game_key_item = self.generate_key(random.choice(json_data["elements"]["puzzle_items"]))
        game_lock_item = self.generate_lock(random.choice(json_data["elements"]["puzzle_items"]))
        game_weapon = self.generate_weapon(random.choice(json_data["elements"]["weapons"]))
        game_armor = self.generate_armor(random.choice(json_data["elements"]["armor"]))
        game_enemy = self.generate_character(random.choice(json_data["elements"]["enemies"]))
        game_ally = self.generate_character(random.choice(json_data["elements"]["allies"]), is_enemy=False)
        for cluster_id in cluster_ids:
            room_type = next(room_type_cycle)
            remaining_room_types.remove(room_type)
            self.create_cluster(cluster_id, room_type, min_rooms_per_cluster, max_rooms_per_cluster, rooms_data)
            cluster_rooms = self.room_clusters[cluster_id]
            print(f"Generate: Cluster ID: {cluster_id}, Number of Rooms: {len(cluster_rooms)}")
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
                if not remaining_room_types:
                    remaining_room_types = room_types.copy()
        self.set_player_start_room(self.rooms[0])
        self.connect_clusters()
        all_rooms = []
        for cluster_rooms in self.room_clusters.values():
            all_rooms.extend(cluster_rooms)
        prims = Prims(all_rooms)
        prims.prims_algorithm()
        self.print_map()

    def generate_room(self, room_type, rooms_data):
        room_data = next(data for data in rooms_data if data["type"] == room_type)
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
        room = Room(room_type, name, description)
        return room

    def get_direction(self, room1, room2):
        if room2.x > room1.x:
            return "east"
        elif room2.x < room1.x:
            return "west"
        elif room2.y > room1.y:
            return "south"
        else:
            return "north"
    
    def get_first_room_by_type(self, room_type):
        rooms_of_type = [room for room in self.rooms if room.type == room_type]
        if rooms_of_type:
            return rooms_of_type[0]
        else:
            return None

    def get_last_room_by_type(self, room_type):
        rooms_of_type = [room for room in self.rooms if room.type == room_type]
        if rooms_of_type:
            return rooms_of_type[-1]
        else:
            return None

    def get_random_room_by_type(self, room_type):
        rooms_of_type = [room for room in self.rooms if room.type == room_type]
        if rooms_of_type:
            return random.choice(rooms_of_type)
        else:
            return None

    def get_room_by_name(self, room_name):
        for room in self.rooms:
            if room.name == room_name:
                return room
        return None

    def get_connected_rooms(self, room):
        return room.connected_rooms.values()
    

    def is_connected(self, room1, room2):
        return room2 in room1.connected_rooms.values()
    
    def is_position_free(self, x, y):
        if x < 0 or y < 0 or x >= self.grid_width or y >= self.grid_height:
            return False
        return self.grid[x][y] is None
    
    def print_map(self):
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                room = self.grid[x][y]
                if room is None:
                    print("□ ", end="")  # Empty space
                else:
                    print(f"{room.name[0]} ", end="")  # First letter of the room's name
            print()
        print()

    @staticmethod
    def opposite_direction(direction):
            return {"north": "south", "south": "north", "east": "west", "west": "east"}[direction]
    
    def set_player_start_room(self, room):
        self.player_start_room = room

    def union(self, cluster1, cluster2):
        root1 = self.find(cluster1)
        root2 = self.find(cluster2)
        if root1 != root2:
            self.cluster_roots[root1] = root2


class Room:
    def __init__(self, room_type, name, description, x=0, y=0):
        self.type = room_type
        self.name = name
        self.description = description
        self.connected_rooms = defaultdict(lambda: None, {"north": None, "south": None, "east": None, "west": None})
        self.x = x
        self.y = y
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

    def connect_room(self, direction, room):
        self.connected_rooms[direction] = room

    def get_room_with_free_direction(self, possible_directions=None):
        if possible_directions is None:
            possible_directions = ["north", "south", "east", "west"]
        random.shuffle(possible_directions)
        for direction in possible_directions:
            if self.connected_rooms[direction] is None:
                return direction
        return None
   
class Player:
    def __init__(self):
        self.hit_points = 50
        self.attack_points = 0
        self.defense_points = 0
        self.current_room = None
        self.inventory = []
        self.x = 0
        self.y = 0

class Item:
    def __init__(self, name, details):
        self.name = name
        self.details = details

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
    def __init__(self, name, hit_points, attack_points, defense_points):
        self.name = name
        self.hit_points = hit_points
        self.attack_points = attack_points
        self.defense_points = defense_points
        self.inventory = []
        self.current_room = None
        self.x = 0
        self.y = 0
        self.is_enemy = None

    def add_item(self, item):
        self.inventory.append(item)
        if isinstance(item, Weapon):
            self.attack_points += item.damage
        elif isinstance(item, Armor):
            self.defense_points += item.defense