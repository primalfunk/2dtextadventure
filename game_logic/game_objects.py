from collections import defaultdict
import logging
import random
from random import choice

class Room:
    def __init__(self, room_type, name, description, x=0, y=0, max_connections=4, cluster_id=None):
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
        self.items = []
        if name != "":
            self.symbol = name[0]
        else:
            self.symbol = " "
        self.cluster_id = cluster_id
        self.max_connections = max_connections

    def __lt__(self, other):
        if isinstance(other, Room):
            return self.count_connections() < other.count_connections()
        return NotImplemented

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

    def count_connections(room):
        return len([direction for direction, connected_room in room.connected_rooms.items() if connected_room is not None])

    @property
    def id(self):
        return f"{self.x}-{self.y}"

    def available_connections(self):
            possible_directions = ["north", "south", "east", "west"]
            return [direction for direction in possible_directions if self.connected_rooms[direction] is None]
    
    def get_adjacent_rooms(self):
        adjacent_rooms = []
        for _, room in self.connected_rooms.items():
            if room is not None:
                adjacent_rooms.append(room)
        return adjacent_rooms

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

class Item:
    def __init__(self, name, details):
        self.name = name
        self.current_room = None
        self.details = details

class Healing:
    def __init__(self, name, hp):
        self.name = name
        self.current_room = None
        self.hp = hp

class Key(Item):
    def __init__(self, name, unlock_room):
        super().__init__(name, "This key can unlock " + unlock_room)
        self.current_room = None
        self.unlock_room = unlock_room

class Lock(Item):
    def __init__(self, name, locked_room):
        super().__init__(name, "This lock can be opened with a key for " + locked_room)
        self.current_room = None
        self.locked_room = locked_room

class Weapon(Item):
    def __init__(self, name, damage, accuracy):
        super().__init__(name, "This weapon can cause " + str(damage) + " points of damage.")
        self.current_room = None
        self.damage = damage
        self.accuracy = accuracy

class Armor(Item):
    def __init__(self, name, defp, ev):
        super().__init__(name, "This armor can defend against " + str(defp) + " points of damage.")
        self.current_room = None
        self.defense = defp
        self.evasion = ev

class Character:
    def __init__(self, name, level, hp, atk, defp, acc, ev, wt, at, is_enemy):
        if not isinstance(self, Player):
            self.name = self.generate_decorated_name(name, is_enemy, level)
        else:
            self.name = name
        self.level = level
        self.hp = hp + sum(random.randint(2, 12) for _ in range(self.level))
        self.atk = atk + sum(random.randint(1, 3) for _ in range(self.level)) 
        self.defp = defp + sum(random.randint(1, 2) for _ in range(self.level))
        self.acc = acc + sum(random.randint(1, 2) for _ in range(self.level))
        self.ev = ev + sum(random.randint(1, 2) for _ in range(self.level))
        
        
        self.weapon = None
        self.armor = None
        self.inventory = []
        self.current_room = None
        self.x = 0
        self.y = 0
        self.is_enemy = is_enemy
        self.ally = None
        self.is_dead = False
        self.base_xp_reward = 100
        self.base_xp_peak = 250
        self.weapon_tier = wt
        self.armor_tier = at
        
    def xp_required_to_level_up(self):
        return self.base_xp_peak * (1.5 ** (self.level - 1)) 

    def calculate_xp_award(self, player_level):
        level_difference = self.level - player_level
        if level_difference >= 0:
            return self.base_xp_reward * ((1 + level_difference) * 0.5)
        else:
            return 100 / (1 - 0.1 * level_difference)

    def add_item(self, item):
        self.inventory.append(item)
        if isinstance(item, Weapon):
            self.atk += item.damage
        elif isinstance(item, Armor):
            self.defp += item.defp

    def roll_initiative(self):
        return random.randint(1, 20) + self.ev
 
    @staticmethod
    def generate_decorated_name(base_name, is_hostile, level_difference):
        descriptors = {
            5: ["Elite", "Battle-Hardened", "Steely", "Hardened", "Ruthless", "Dauntless"],
            4: ["Seasoned", "Practiced", "Adept", "Wise", "Veteran", "Proficient"],
            3: ["Challenging", "Full-grown", "Trained", "Tricky"],
            2: ["Tough", "Experienced", "Solid", "Rugged", "Stout", "Strong"],
            1: ["Wily", "Cunning", "Spirited", "Fiery", "Energetic", "Ambitious"],
            0: ["Normal", "Average", "Standard", "Regular", "Usual"],
            -1: ["Hesitant", "Unprepared", "Immature", "Bruised", "Sick-looking"],
            -2: ["Innocuous", "Harmless", "Old", "Scowling", "Unfortunate"],
            -3: ["Inexperienced", "Novice", "Beginner", "Rookie"],
            -4: ["Weak", "Fragile", "Frail", "Feeble", "Tottering", "Sickly"],
            -5: ["Helpless", "Uninteresting", "Inept", "Ineffectual", "Sad", "Lame"]
}
        friendly_synonyms = ["friendly", "ally", "peaceful", "relaxed", "polite", "smiling"]
        hostile_synonyms = ["hostile", "enemy", "angry", "violent", "rude", "crazed"]
        if level_difference > 5:
            level_difference = 5
        elif level_difference < -5:
            level_difference = -5
        
        if level_difference not in descriptors:
            level_difference = "Unknown"
        else:
            level_difference = choice(descriptors[level_difference])
        type_desc = choice(hostile_synonyms if is_hostile else friendly_synonyms)
        return f"{level_difference} {base_name} ({type_desc})"

    def pick_up(self, item):
            ...
            # Remove the item from the room
            self.current_room.remove_item(item)

    def drop(self, item):
        if isinstance(item, Weapon):
            self.weapon = None
        elif isinstance(item, Armor):
            self.armor = None
        # Add the item to the room
        self.current_room.add_item(item)

class Player(Character):
    def __init__(self):
        super().__init__(name="Player", level=1, hp=100, atk=10, defp=10, acc=45, ev=35, wt=0, at=0, is_enemy=False)
        self.xp = 0
        self.key = None

    def gain_xp(self, xp_amount):
        self.xp += xp_amount
        while self.xp >= self.xp_required_to_level_up():
            self.xp -= self.xp_required_to_level_up()
            self.level_up()

    def level_up(self):
        self.level += 1
        self.hp += 48 + random.randint(2, 12)
        self.atk += 4 + random.randint(1, 3)
        self.defp += 3 + random.randint(1, 2)
        self.acc += random.randint(1, 2)
        self.ev += random.randint(1, 2)