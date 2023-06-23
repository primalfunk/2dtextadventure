from game_logic import GameMap, Room
import json
import unittest

class TestMyCode(unittest.TestCase):

    def setUp(self):
        self.room1 = Room('type1', 'room1', 'description1', 0, 0)
        self.room2 = Room('type2', 'room2', 'description2', 1, 0)
        self.game_map = GameMap(9,9)
        with open('fantasy.json', 'r') as file:
            data = json.load(file)
        self.rooms_data = data['elements']['rooms']
    
    def test_generate_room(self):
        room_type = 'castle'
        new_room = self.game_map.generate_room(room_type, self.rooms_data)
        self.assertIsInstance(new_room, Room)
        self.assertEqual(new_room.type, room_type)
        self.assertIn(new_room.name, [f'{adj} {n}' for adj, n in zip(self.rooms_data[0]['adjectives'], self.rooms_data[0]['name'])])

    def test_add_room(self):
        new_room = Room('type1', 'room3', 'description3')
        self.game_map.add_room(new_room, x=1, y=1)
        self.assertEqual(self.game_map.grid[1][1], new_room)
        self.assertEqual(new_room.x, 1)
        self.assertEqual(new_room.y, 1)

    def test_add_room_exception(self):
        self.game_map.add_room(self.room1, x=0, y=0)
        with self.assertRaises(Exception):
            self.game_map.add_room(self.room2, x=0, y=0)

    def test_connect_clusters(self):
        self.game_map.room_clusters = {
            0: [self.room1],
            1: [self.room2]
        }
        self.game_map.add_room(self.room1, x=0, y=0)
        self.game_map.add_room(self.room2, x=1, y=1)
        self.game_map.connect_clusters()
        self.assertIn(self.room2, self.room1.connected_rooms.values())
        self.assertIn(self.room1, self.room2.connected_rooms.values())

    def test_connect_rooms(self):
        self.game_map.add_room(self.room1, x=0, y=0)
        self.game_map.add_room(self.room2, x=1, y=0)
        room1_connections = set(self.room1.available_connections())
        room2_connections = set(self.room2.available_connections())
        common_direction = room1_connections.intersection(room2_connections).pop()
        self.game_map.connect_rooms(self.room1, self.room2, common_direction)
        self.assertEqual(self.room1.connected_rooms[common_direction], self.room2)
        self.assertEqual(self.room2.connected_rooms[self.game_map.opposite_direction(common_direction)], self.room1)

    def test_create_cluster(self):
        room_type = self.rooms_data[0]["type"]
        min_rooms_per_cluster = 5
        max_rooms_per_cluster = 10
        cluster_id = 0
        self.game_map.create_cluster(cluster_id, room_type, min_rooms_per_cluster, max_rooms_per_cluster, self.rooms_data)
        cluster_rooms = self.game_map.room_clusters[cluster_id]
        self.assertTrue(min_rooms_per_cluster <= len(cluster_rooms) <= max_rooms_per_cluster, f"Number of rooms in the cluster {len(cluster_rooms)} is not within the range {min_rooms_per_cluster}-{max_rooms_per_cluster}")
        for room in cluster_rooms:
            self.assertEqual(room.type, room_type)
        for room in cluster_rooms:
            connected_rooms = room.connected_rooms.values()
            self.assertTrue(any(other_room in connected_rooms for other_room in cluster_rooms))

    def test_union(self):
            self.game_map.room_clusters = {
                0: [self.room1],
                1: [self.room2]
            }
            self.game_map.cluster_roots = [0, 1]
            self.game_map.union(0, 1)
            self.assertEqual(len(self.game_map.cluster_roots), 1)
            remaining_cluster = self.game_map.room_clusters[self.game_map.cluster_roots[0]]
            self.assertIn(self.room1, remaining_cluster)
            self.assertIn(self.room2, remaining_cluster)

if __name__ == "__main__":
    unittest.main()