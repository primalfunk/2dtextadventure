import heapq
import math
import random

class Prims:

    def __init__(self, rooms):
        self.rooms = rooms
        self.tree = []
        self.distances = {room: float('inf') for room in rooms}

    def prims_algorithm(self):
        queue = [(float('inf'), room) for room in self.rooms]
        heapq.heapify(queue)
        start_room = random.choice(self.rooms)
        self.update_distance_in_queue(queue, start_room, 0)

        while queue:
            _, current_room = heapq.heappop(queue)
            if current_room not in self.tree:
                self.tree.append(current_room)
                for neighbor in current_room.connected_rooms.values():
                    if neighbor is None or neighbor in self.tree:
                        continue
                    self.connect_room(current_room, neighbor)
                    new_distance = self.distance(current_room, neighbor)
                    self.update_distance_in_queue(queue, neighbor, new_distance)

    def get_possible_neighbors(self, room):
        neighbors = []
        for potential_neighbor in self.rooms:
            if potential_neighbor != room and not self.are_connected(room, potential_neighbor):
                neighbors.append(potential_neighbor)
        return neighbors

    def are_connected(self, room1, room2):
        for direction, connected_room in room1.connected_rooms.items():
            if connected_room == room2:
                return True
        return False

    def distance(self, room1, room2):
        dx, dy = room2.x - room1.x, room2.y - room1.y
        return math.sqrt(dx*dx + dy*dy)

    def update_distance_in_queue(self, queue, room, new_distance):
        if new_distance < self.distances[room]:
            self.distances[room] = new_distance
            heapq.heappush(queue, (new_distance, room))

    def connect_room(self, room1, room2):
        direction = self.calculate_direction(room1, room2)
        opposite = self.opposite_direction(direction)

        room1.connected_rooms[direction] = room2
        room2.connected_rooms[opposite] = room1

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

    def opposite_direction(self, direction):
        return {"north": "south", "south": "north", "east": "west", "west": "east"}[direction]