from PySide6.QtWidgets import QWidget, QGridLayout, QTextEdit, QLabel, QPushButton, QSizePolicy, QHBoxLayout, QVBoxLayout, QFrame
from PySide6.QtCore import Qt, QCoreApplication, QEvent
from PySide6 import QtGui
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor
from game_logic import GameMap, Player, Key
import json
import logging
import random
import traceback

class DataLoader:
    def __init__(self, json_path):
        self.json_path = json_path
        self.data = None
        self.game_map = None
        self.load_data()

    def generate_game_title(self):
        game_title = random.choice(self.data["elements"]["game_title"]) 
        treasure = random.choice(self.data["elements"]["treasure"])
        title = f"{game_title} {treasure}"
        return title

    def scrutinize_data(self, data):
        logging.info("Scrutinize_data is called.")
        for genre_data in data["genres"]:
            genre = genre_data["genre"]
            logging.info(f"Genre: {genre}")
            elements = genre_data["elements"]
            for key, value in elements.items():
                if key == "rooms":
                    count = len(value)
                    logging.info(f"Rooms count: {count}")
                    for room in value:
                        room_type = room["type"]
                        name_count = len(room["name"])
                        adjectives_count = len(room["adjectives"])
                        scenery_count = len(room["scenery"])
                        atmosphere_count = len(room["atmosphere"])
                        logging.info(f"Room type: {room_type}")
                        logging.info(f"Name count: {name_count}")
                        logging.info(f"Adjectives count: {adjectives_count}")
                        logging.info(f"Scenery count: {scenery_count}")
                        logging.info(f"Atmosphere count: {atmosphere_count}")

    def load_data(self):
        try:
            with open(self.json_path, 'r') as file:
                data = json.load(file)
                # self.scrutinize_data(data)
                genres = data.get("genres")
                if not genres:
                    raise ValueError("Genres not found in data")
                if self.data is None:
                    self.data = random.choice(genres)
                else:
                    self.data = None
                    self.data = random.choice(genres)
                logging.debug(f"Data keys after loading: {self.data.keys()}")
                logging.debug(f"Data length after loading: {len(self.data)}")
        except (FileNotFoundError, ValueError) as e:
            logging.error(f"Error in loading data: {str(e)}")
        
    def create_game_map(self, grid_width=9, grid_height=9):
        try: 
            if self.data:
                logging.info("Data loaded successfully.")
                elements = self.data.get("elements")
                if elements:
                    logging.info("Elements found in data.")
                    logging.debug(f"Elements before map generation: {str(elements)[:15]}")
                    logging.debug(f"Rooms before map generation: {str(elements['rooms'])[:20]}")
                    try:
                        self.game_map = GameMap(elements["rooms"], grid_width, grid_height, data_loader=self)
                    except Exception as e:
                        logging.exception("Failed to initialize game: %s, e)")
                    retries = 5  # maximum number of retries
                    for i in range(retries):
                        successful_generation = self.game_map.generate_game_map(elements["rooms"])
                        if successful_generation:
                            logging.info("Game map successfully generated.")
                            return self.game_map
                        else:
                            logging.error(f"***Game map generation failed at attempt {i+1}. Retrying...")
                    logging.error("Game map generation failed after maximum retries.")
                    raise Exception("Game map generation failed after maximum retries.")
                else:
                    
                    logging.warning("No data loaded.")
                    raise ValueError("Data not loaded, can't create game map")
            return False
        except Exception as e:
            logging.error(f"An error occurred during game initialization: {e}")
            logging.error(traceback.format_exc())

    def get_game_map(self):
        logging.debug(f"Current game map: {self.game_map}")
        if self.game_map:
            return self.game_map
        else:
            raise Exception("Game map not created yet")

class GameGUI(QWidget):
    def __init__(self, data_loader=None):
        self.data_loader = data_loader
        self.game_map = None
        self.font = QFont("EuropeanTypewriter", 14)
        self.font_size = 14
        self.min_font_size = 10
        self.max_font_size = 30
        super().__init__()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.player_info_label = QLabel("")
        player_info_layout = QHBoxLayout()
        player_info_layout.addWidget(self.player_info_label)
        self.font_size_decrease_button = QPushButton("-")
        self.font_size_decrease_button.setEnabled(False)
        self.font_size_decrease_button.setFixedWidth(20)
        self.font_size_increase_button = QPushButton("+")
        self.font_size_increase_button.setEnabled(False)
        self.font_size_increase_button.setFixedWidth(20)
        player_info_layout.addWidget(self.font_size_decrease_button)
        player_info_layout.addWidget(self.font_size_increase_button)
        main_layout.addLayout(player_info_layout)
        self.game_text_area = QTextEdit()
        self.game_text_area.setReadOnly(True)
        self.game_text_area.setAlignment(Qt.AlignCenter)
        self.game_text_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.game_text_area.setCurrentFont(QFont("EuropeanTypewriter"))
        self.font_size_decrease_button.clicked.connect(self.decrease_font_size)
        self.font_size_increase_button.clicked.connect(self.increase_font_size)
        main_layout.addWidget(self.game_text_area)
        game_title = self.generate_game_title()
        format = QtGui.QTextCharFormat()
        format.setFont(QFont("EuropeanTypewriter", 30))
        cursor = self.game_text_area.textCursor()
        cursor.setCharFormat(format)
        cursor.insertText(game_title)
        format.setFont(QFont("EuropeanTypewriter", 16))
        cursor.insertBlock()
        cursor.setCharFormat(format)
        cursor.insertText("a procedurally generated text adventure")
        lowest_row_height = 225
        self.start_button = QPushButton("Start")
        quit_button = QPushButton("Quit")
        self.start_button.clicked.connect(self.start_game)
        quit_button.clicked.connect(QCoreApplication.instance().quit)
        self.stats_label = QLabel("Player Stats")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setFont(QFont("EuropeanTypewriter", 14))
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.stats_label)
        button_layout.addWidget(self.stats_text)
        button_layout.addStretch(1)
        button_layout.addStretch(1)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(quit_button)
        buttons_frame = QFrame()
        buttons_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        buttons_frame_layout = QVBoxLayout()
        buttons_frame_layout.addStretch(1)
        buttons_frame_layout.addLayout(button_layout)
        buttons_frame_layout.addStretch(1)
        buttons_frame.setLayout(buttons_frame_layout)
        buttons_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        buttons_frame.setFixedHeight(lowest_row_height)
        direction_frame = QFrame()
        direction_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        direction_layout = QGridLayout()
        north_button = QPushButton("North")
        west_button = QPushButton("West")
        east_button = QPushButton("East")
        south_button = QPushButton("South")
        self.interact_button = QPushButton("Interact")
        direction_layout.addWidget(north_button, 0, 1, 1, 1)
        direction_layout.addWidget(west_button, 1, 0, 1, 1)
        direction_layout.addWidget(self.interact_button, 1, 1, 1, 1)
        direction_layout.addWidget(east_button, 1, 2, 1, 1)
        direction_layout.addWidget(south_button, 2, 1, 1, 1)
        direction_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        direction_frame.setFixedHeight(lowest_row_height)
        direction_frame.setLayout(direction_layout)
        north_button.clicked.connect(lambda: self.travel("north"))
        west_button.clicked.connect(lambda: self.travel("west"))
        east_button.clicked.connect(lambda: self.travel("east"))
        south_button.clicked.connect(lambda: self.travel("south"))
        self.interact_button.clicked.connect(lambda: self.interact())
        inventory_frame = QFrame()
        inventory_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        inventory_layout = QVBoxLayout()
        inventory_label = QLabel("Inventory")
        inventory_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.inventory_text = QTextEdit()
        self.inventory_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        inventory_layout.addWidget(inventory_label)
        inventory_layout.addWidget(self.inventory_text)
        inventory_layout.setStretch(0, 0)
        inventory_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        inventory_frame.setFixedHeight(lowest_row_height)
        inventory_frame.setLayout(inventory_layout)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(buttons_frame)
        bottom_layout.addWidget(direction_frame)
        bottom_layout.addWidget(inventory_frame)
        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 2) 
        main_layout.setStretch(2, 1)
        main_layout.addLayout(bottom_layout)
        self.setWindowTitle("Game of Games")
        self.setGeometry(100, 100, 800, 600)
        self.show()
        self.player = Player()
        self.update_player_stats()

    def increase_font_size(self):
        if self.font_size < self.max_font_size:
            self.font_size += 1
            self.update_font()

    def decrease_font_size(self):
        if self.font_size > self.min_font_size:
            self.font_size -= 1
            self.update_font()

    def update_font(self):
        font = QFont("EuropeanTypewriter", self.font_size)
        current_text = self.game_text_area.toPlainText()
        self.game_text_area.clear()
        self.game_text_area.setCurrentFont(font)
        self.game_text_area.setPlainText(current_text)
        format_bold = QTextCharFormat()
        format_bold.setFontWeight(QFont.Bold)
        lines = current_text.split('\n')
        if len(lines) >= 1:
            title_length = len(lines[0])
            cursor = self.game_text_area.textCursor()
            cursor.setPosition(0, QTextCursor.MoveAnchor)
            cursor.setPosition(title_length, QTextCursor.KeepAnchor)
            cursor.setCharFormat(format_bold)

    def generate_game_title(self):
        return self.data_loader.generate_game_title() if self.data_loader else "Exciting Title Of Game"

    def update_player_info(self):
        self.player_info_label.setText(f"Player Info - Position: ({self.current_room.x}, {self.current_room.y})")

    def update_player_stats(self):
        self.stats_text.setPlainText(
            f"Level: {self.player.level}\n"
            f"Hit Points: {self.player.hp}\n"
            f"Attack: {self.player.atk}\n"
            f"Defense: {self.player.defp}\n"
            f"Accuracy: {self.player.defp}\n"
            f"Defense: {self.player.defp}"
        )

    def initialize_game(self, fresh):
        try:
            if fresh:
                self.game_map = self.data_loader.create_game_map(9,9)
            else:
                self.game_map = self.data_loader.create_game_map(9,9)
            logging.info(f"Game map type is {type(self.game_map)}, Fresh start is {fresh}")


        except Exception as e:
            logging.error(f"Failed to initialize game: {e}")
            self.game_map = None

    def start_game(self):
        logging.info(f"Start button pressed.")
        if self.game_map:
            logging.info(f"Game_map object right here is {type(self.game_map)}")
            self.map_window = MapWindow(game_map=self.game_map)
        if self.start_button.text() == "Start":
            self.game_text_area.clear()
            self.game_text_area.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.game_text_area.setFont(self.font)
            first_room = self.game_map.rooms[0]
            available_directions = [direction for direction, room in first_room.connected_rooms.items() if room is not None]
            room_description = f"<b>{first_room.name}</b><br><br>{first_room.description}<br><br>You can go: {', '.join(available_directions)}"
            self.game_text_area.append(room_description)
            self.game_map.player.x = first_room.x
            self.game_map.player.y = first_room.y
            self.game_map.player.current_room = first_room
            self.current_room = first_room
            self.update_player_info()
            self.start_button.setText("Restart")
            self.font_size_increase_button.setEnabled(True)
            self.font_size_decrease_button.setEnabled(True)
            self.game_text_area.moveCursor(QtGui.QTextCursor.End)
            self.map_window.show_self()
            self.map_window.update_map()
        else:
            self.game_text_area.clear()
            self.game_text_area.setAlignment(Qt.AlignCenter)
            game_title = self.generate_game_title()
            format = QtGui.QTextCharFormat()
            format.setFont(QFont("EuropeanTypewriter", 30))
            cursor = self.game_text_area.textCursor()
            cursor.setCharFormat(format)
            cursor.insertText(game_title)
            format.setFont(QFont("EuropeanTypewriter", 16))
            cursor.insertBlock()
            cursor.setCharFormat(format)
            cursor.insertText("a procedurally generated text adventure")
            self.start_button.setText("Start")
            self.font_size_increase_button.setEnabled(False)
            self.font_size_decrease_button.setEnabled(False)
            self.game_text_area.moveCursor(QtGui.QTextCursor.End)
            self.initialize_game(fresh=False)
            self.hide_map()

    def update_inventory_text(self):
        inventory_text = ""
        for item in self.game_map.player.inventory:
            inventory_text += f"{item.name}\n"
        self.inventory_text.setText(inventory_text)

    def travel(self, direction):
        if direction in self.current_room.connected_rooms:
            next_room = self.current_room.connected_rooms[direction]
            if next_room is None:
                self.game_text_area.append("You can't go that way.")
                return
            self.game_text_area.append(f"You travel {direction}.\n")
            if direction == "north":
                self.game_map.player.y -= 1
            elif direction == "south":
                self.game_map.player.y += 1
            elif direction == "east":
                self.game_map.player.x += 1
            elif direction == "west":
                self.game_map.player.x -= 1
            self.current_room = next_room
            self.game_map.player.current_room = next_room
            self.display_room(self.current_room)
            self.update_player_info()
            self.update_interact_button()
            available_directions = [direction for direction, room in self.current_room.connected_rooms.items() if room is not None]
            available_directions = ", ".join(available_directions)
            travel_options = f"You can go: {available_directions}"
            self.game_text_area.append(travel_options)
            self.game_text_area.moveCursor(QtGui.QTextCursor.End)
            self.map_window.update_map()
        else:
            self.game_text_area.append("You can't go that way.")

    def update_interact_button(self):
        current_room = self.game_map.player.current_room
        if any([current_room.key_item, current_room.weapon, current_room.armor]): 
            self.interact_button.setText("Pick Up")
        elif current_room.lock_item:
            has_key = any(isinstance(item, Key) for item in self.game_map.player.inventory)
            self.interact_button.setText("Unlock") if has_key else self.interact_button.setText("Locked")
        elif current_room.enemy:
            self.interact_button.setText("Attack")
        elif current_room.ally:
            self.interact_button.setText("Greet")
        else:
            self.interact_button.setText("Interact")

    def get_current_room(self):
        room_name = self.game_text_area.toPlainText().split(":")[0]
        for room in self.game_map.rooms:
            if room.name == room_name:
                return room
        return None

    def display_room(self, room):
        self.game_text_area.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        item_description = ""
        if room.key_item:
            item_description += f"<br><br>There is a {room.key_item.name} here."
        if room.lock_item:
            item_description += f"<br><br>There is a {room.lock_item.name} here."
        if room.weapon:
            item_description += f"<br><br>There is a {room.weapon.name} here."
        if room.armor:
            item_description += f"<br><br>There is a {room.armor.name} here."
        if room.enemy:
            item_description += f"<br><br>You see a {room.enemy.name} here."
        if room.ally:
            item_description += f"<br><br>A {room.ally.name} is here."
        room_description = f"<b>{room.name}</b><br><br>{room.description}{item_description}"
        self.game_text_area.moveCursor(QtGui.QTextCursor.End)
        self.game_text_area.insertHtml(room_description)
        self.game_text_area.moveCursor(QtGui.QTextCursor.End)

    def interact(self):
        current_room = self.game_map.player.current_room

        if self.interact_button.text() == "Pick Up":
            if current_room.key_item:
                item = current_room.key_item
                self.game_text_area.append(f"You pick up the {item.name}.")
                self.game_map.player.inventory.append(item)
                current_room.key_item = None
            elif current_room.weapon:
                item = current_room.weapon
                self.game_text_area.append(f"You pick up the {item.name}.")
                self.game_map.player.inventory.append(item)
                current_room.weapon = None
            elif current_room.armor:
                item = current_room.armor
                self.game_text_area.append(f"You pick up the {item.name}.")
                self.game_map.player.inventory.append(item)
                current_room.armor = None
            self.update_interact_button()
            self.update_inventory_text()
        else:
            # Handle other interact actions (e.g., attacking, greeting, unlocking)
            # ...
            pass
        self.game_text_area.moveCursor(QtGui.QTextCursor.End)

    def show_self(self):
        self.show()
        print(self.isVisible())
        self.update_map()

    def hide_map(self):
        self.map_window.hide()


class MapWindow(QWidget):
    def __init__(self, game_map):
        self.game_map = game_map
        super(MapWindow, self).__init__()
        self.setWindowTitle("Game Map")
        self.setGeometry(950, 100, 500, 400)
        self.layout = QVBoxLayout()
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background-color: white;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.layout.addWidget(self.grid_widget)
        try:
                # Log the type and value of game_map
            logging.info(f"game_map type: {type(self.game_map)}")
            logging.info(f"game_map value: {self.game_map}")
            # If game_map is the expected type, log its grid_width and grid_height
            if isinstance(self.game_map, GameMap):  # replace GameMap with the actual type of your game_map
                logging.info(f"game_map.grid_width: {self.game_map.grid_width}")
                logging.info(f"game_map.grid_height: {self.game_map.grid_height}")

            self.labels = [[None for _ in range(2*game_map.grid_width - 1)] for _ in range(2*game_map.grid_height - 1)]
        except Exception as e:
            logging.error(f"Label problem: {e}")
            logging.error(traceback.format_exc())
        for i in range(2*game_map.grid_height - 1):
            for j in range(2*game_map.grid_width - 1):
                self.labels[i][j] = QLabel(' ')
                self.grid_layout.addWidget(self.labels[i][j], i, j)
        self.setLayout(self.layout)
        self.room_type_colors = {}

    def update_map(self):
        try:
            all_the_colors = ["yellow", "cyan", "magenta", "silver", "lime", 
            "orange", "pink", "violet", "coral", "lavender", "turquoise", "skyblue", "salmon", "peachpuff"]
            for room in self.game_map.rooms:
                if room is not None:
                    if (0 <= 2*room.y < len(self.labels)) and (0 <= 2*room.x < len(self.labels[0])):
                        room_label = self.labels[2*room.y][2*room.x]
                        room_label.setAlignment(Qt.AlignCenter)
                        room_label.setStyleSheet("font-size: 20px; font-weight: bold;")  # Default room style
                        # set type background
                        if room.type not in self.room_type_colors:
                            random.shuffle(all_the_colors)
                            shuffled_colors = all_the_colors
                            color_choice = shuffled_colors.pop(0)
                            self.room_type_colors[room.type] = color_choice
                        # Set room symbol
                        if room == self.game_map.player.current_room:
                            room_label.setText('P')
                            room_label.setStyleSheet(f"background-color: red; border: 2px solid black; font-size: 20px; font-weight: bold;")
                        elif room.enemy:
                            room_label.setText('E')
                            room_label.setStyleSheet(f"background-color: {self.room_type_colors[room.type]}; font-size: 20px; font-weight: bold;")
                        elif room.weapon:
                            room_label.setText('W')
                            room_label.setStyleSheet(f"background-color: {self.room_type_colors[room.type]}; font-size: 20px; font-weight: bold;")
                        elif room.armor:
                            room_label.setText('A')
                            room_label.setStyleSheet(f"background-color: {self.room_type_colors[room.type]}; font-size: 20px; font-weight: bold;")
                        elif room.key_item:
                            room_label.setText('K')
                            room_label.setStyleSheet(f"background-color: {self.room_type_colors[room.type]}; font-size: 20px; font-weight: bold;")
                        elif room.lock_item:
                            room_label.setText('L')
                            room_label.setStyleSheet(f"background-color: {self.room_type_colors[room.type]}; font-size: 20px; font-weight: bold;")
                        elif room.ally:
                            room_label.setText('A')
                            room_label.setStyleSheet(f"background-color: {self.room_type_colors[room.type]}; font-size: 20px; font-weight: bold;")
                        else:
                            room_label.setText('R')
                            room_label.setStyleSheet(f"background-color: {self.room_type_colors[room.type]}; font-size: 20px; font-weight: bold;")
                        # Draw connections
                        for direction, connected_room in room.connected_rooms.items():
                            if connected_room is not None:
                                connection_label = None
                                if direction == "north" and 2*room.y - 1 >= 0:
                                    connection_label = self.labels[2*room.y - 1][2*room.x]
                                    connection_label.setText('|')
                                elif direction == "south" and 2*room.y + 1 < len(self.labels):
                                    connection_label = self.labels[2*room.y + 1][2*room.x]
                                    connection_label.setText('|')
                                elif direction == "west" and 2*room.x - 1 >= 0:
                                    connection_label = self.labels[2*room.y][2*room.x - 1]
                                    connection_label.setText('-')
                                elif direction == "east" and 2*room.x + 1 < len(self.labels[0]):
                                    connection_label = self.labels[2*room.y][2*room.x + 1]
                                    connection_label.setText('-')
                                if connection_label is not None:
                                    connection_label.setAlignment(Qt.AlignCenter)
                                    connection_label.setStyleSheet("border: 1px solid black; font-size: 10px;")
        except Exception as e:
            logging.error(f"Error occurred during update_map function: {e}")

    def show_self(self):
        self.show()
