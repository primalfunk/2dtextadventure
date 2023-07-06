from game_logic.game_logic import GameMap
import json
import logging
import os
import random
import sys

class DataLoader:
    def __init__(self, json_path):
        self.json_path = json_path
        self.data = None
        self.genre = None
        self.game_map = None
        self.treasure = None
        self.title = None
        self.load_data()

    def resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def generate_game_title(self):
        logging.info(f"DL/Generate_game_title: Data now looks this way: {str(self.genre)[:50]}")
        game_title = random.choice(self.genre["elements"]["game_title"]) 
        treasure = random.choice(self.genre["elements"]["treasure"])
        self.title = game_title
        self.treasure = treasure
        title = f"{game_title} {treasure}"
        return title

    def select_random_genre(self):
        try:
            genres = self.data.get("genres")
            logging.info(f"Select_random_genre: Genres comes up as {str(genres)[:50]}")
            if not genres:
                raise ValueError("Genres not found in data")
            self.genre = random.choice(genres)
            logging.debug(f"Select_random_genre: Data keys after loading: {self.data.keys()}")
            logging.debug(f"Data length after loading: {len(self.data)}")
        except ValueError as e:
            logging.error(f"Error in selecting random genre: {str(e)}")

    def load_data(self):
        try:
            with open(self.json_path, 'r') as file:
                self.data = json.load(file)
        except (FileNotFoundError, ValueError) as e:
            logging.error(f"Error in loading data: {str(e)}")
        
    def create_game_map(self, grid_width=9, grid_height=9, player=None):
        # instantiates GameMap; returns a successful game map to data_loader.game_map (self.game_map, in here)
        if self.genre:
            elements = self.genre.get("elements")
            if elements:
                self.game_map = GameMap(elements["rooms"], grid_width, grid_height, data_loader=self, player=player)
                retries = 5  # maximum number of retries
                for _ in range(retries):
                    successful_generation = self.game_map.generate_game_map(elements["rooms"])
                    if successful_generation:
                        return self.game_map
        return False

    def get_game_map(self):
        logging.debug(f"Current game map: {self.game_map}")
        if self.game_map:
            return self.game_map
        else:
            raise Exception("Game map not created yet")