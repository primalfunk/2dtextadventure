from combat import Combat
from game_logic import GameMap, Player, Key
import json
import logging
import os
from PySide6.QtWidgets import QWidget, QGridLayout, QTextEdit, QLabel, QPushButton, QSizePolicy, QHBoxLayout, QVBoxLayout, QFrame, QGridLayout
from PySide6.QtCore import Qt, QCoreApplication, QThread
from PySide6 import QtGui
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QPixmap
import random
import sys
import traceback

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

    def scrutinize_data(self, data): # debugging method
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
        
    def create_game_map(self, grid_width=9, grid_height=9):
        try: 
            if self.genre:
                logging.info("Genre data loaded successfully.")
                elements = self.genre.get("elements")
                if elements:
                    logging.info("Elements found in data.")
                    logging.debug(f"Elements before map generation: {str(elements)[:50]}")
                    logging.debug(f"Rooms before map generation: {str(elements['rooms'])[:50]}")
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
                logging.warning("No genre data loaded.")
                raise ValueError("No genre data loaded, can't create game map")
        except Exception as e:
            logging.error(f"An error occurred during game initialization: {e}")
            logging.error(traceback.format_exc())
        return False

    def get_game_map(self):
        logging.debug(f"Current game map: {self.game_map}")
        if self.game_map:
            return self.game_map
        else:
            raise Exception("Game map not created yet")

class GameGUI(QWidget):
    def __init__(self, data_loader=None):
        self.combat_object = None
        self.combat_thread = None
        self.data_loader = data_loader
        self.game_map = None
        self.fontB = QFont("Sunny", 44)
        self.fontT = QFont("Roboto", 14)
        self.fontM = QFont("Fira Sans Medium", 14)
        self.font_size = 14
        self.min_font_size = 10
        self.max_font_size = 30
        self.backColorA = "#b1b1fa"
        self.backColorB = "powderblue"
        self.textColorA = "#000088"
        self.textColorB = "black"
        super().__init__()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
    
        self.player_info_label = QLabel("")
        self.player_info_label.setFont(self.fontT)
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
        self.font_size_decrease_button.clicked.connect(self.decrease_font_size)
        self.font_size_increase_button.clicked.connect(self.increase_font_size)
        main_layout.addWidget(self.game_text_area)
        logging.info(f"Initialize game is called.")
        self.initialize_game()
        logging.info(f"Generate_game_title is called.")
        game_title = self.data_loader.generate_game_title()
        format = QtGui.QTextCharFormat()
        format.setFont(self.fontB)
        cursor = self.game_text_area.textCursor()
        cursor.setCharFormat(format)
        cursor.insertText(game_title)
        format.setFont(self.fontT)
        cursor.insertBlock()
        cursor.setCharFormat(format)
        cursor.insertText("a procedurally generated text adventure by j menard\n")
        cursor.insertText("YOSL 2023")
        lowest_row_height = 280
        self.start_button = QPushButton("Start")
        self.start_button.setFont(self.fontT)
        self.quit_button = QPushButton("Quit")
        self.quit_button.setFont(self.fontT)
        self.start_button.clicked.connect(self.start_game)
        self.quit_button.clicked.connect(QCoreApplication.instance().quit)
        self.stats_label = QLabel("Player Stats")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setFont(self.fontT)
        self.stats_text = QTextEdit()
        self.stats_text.setFont(self.fontM)
        self.stats_text.setReadOnly(True)
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.stats_label)
        button_layout.addWidget(self.stats_text)
        button_layout.addStretch(1)
        button_layout.addStretch(1)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.quit_button)
        self.buttons_frame = QFrame()
        self.buttons_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        buttons_frame_layout = QVBoxLayout()
        buttons_frame_layout.addStretch(1)
        buttons_frame_layout.addLayout(button_layout)
        buttons_frame_layout.addStretch(1)
        self.buttons_frame.setLayout(buttons_frame_layout)
        self.buttons_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.buttons_frame.setFixedHeight(lowest_row_height)
        self.direction_frame = QFrame()
        self.direction_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        direction_layout = QGridLayout()
        self.north_button = QPushButton("North")
        self.north_button.setFont(self.fontT)
        self.west_button = QPushButton("West")
        self.west_button.setFont(self.fontT)
        self.east_button = QPushButton("East")
        self.east_button.setFont(self.fontT)
        self.south_button = QPushButton("South")
        self.south_button.setFont(self.fontT)
        self.interact_button = QPushButton("Interact")
        self.interact_button.setFont(self.fontT)
        direction_layout.addWidget(self.north_button, 0, 1, 1, 1)
        direction_layout.addWidget(self.west_button, 1, 0, 1, 1)
        direction_layout.addWidget(self.interact_button, 1, 1, 1, 1)
        direction_layout.addWidget(self.east_button, 1, 2, 1, 1)
        direction_layout.addWidget(self.south_button, 2, 1, 1, 1)
        self.direction_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.direction_frame.setFixedHeight(lowest_row_height)
        self.direction_frame.setLayout(direction_layout)
        self.north_button.clicked.connect(lambda: self.travel("north"))
        self.west_button.clicked.connect(lambda: self.travel("west"))
        self.east_button.clicked.connect(lambda: self.travel("east"))
        self.south_button.clicked.connect(lambda: self.travel("south"))
        self.interact_button.clicked.connect(lambda: self.interact())
        self.inventory_frame = QFrame()
        self.inventory_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        inventory_layout = QVBoxLayout()
        self.inventory_label = QLabel("Inventory")
        self.inventory_label.setFont(self.fontT)
        self.inventory_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.inventory_text = QTextEdit()
        self.inventory_text.setFont(self.fontM)
        self.inventory_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        inventory_layout.addWidget(self.inventory_label)
        inventory_layout.addWidget(self.inventory_text)
        inventory_layout.setStretch(0, 0)
        self.inventory_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.inventory_frame.setFixedHeight(lowest_row_height)
        self.inventory_frame.setLayout(inventory_layout)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.buttons_frame)
        bottom_layout.addWidget(self.direction_frame)
        bottom_layout.addWidget(self.inventory_frame)
        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 2) 
        main_layout.setStretch(2, 1)
        main_layout.addLayout(bottom_layout)
        self.interactive_buttons = [self.font_size_decrease_button, 
                                    self.font_size_increase_button,
                                    self.north_button,
                                    self.west_button,
                                    self.east_button,
                                    self.south_button,
                                    self.interact_button]
        self.setWindowTitle("Undeclared Game Title")
        self.setGeometry(200, 100, 950, 700)
        self.show()
        self.set_GUI_color()
        self.player = Player()
        self.update_player_stats()

    def set_GUI_color(self):
        self.player_info_label.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.stats_label.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.stats_text.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.stats_text.setAlignment(Qt.AlignCenter)
        self.inventory_label.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.inventory_text.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.inventory_text.setAlignment(Qt.AlignCenter)
        self.font_size_decrease_button.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.font_size_increase_button.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.game_text_area.setStyleSheet(f"background-color: {self.backColorA}; color: {self.textColorA};")
        self.start_button.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.quit_button.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.north_button.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.west_button.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.east_button.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.south_button.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.interact_button.setStyleSheet(f"background-color: {self.backColorB}; color: {self.textColorB};")
        self.buttons_frame.setStyleSheet(f"background-color: {self.backColorA};")
        self.direction_frame.setStyleSheet(f"background-color: {self.backColorA};")
        self.inventory_frame.setStyleSheet(f"background-color: {self.backColorA};")

    def disable_all_buttons(self):
        for button in self.interactive_buttons:
            button.setDisabled(True)

    def enable_all_buttons(self):
        for button in self.interactive_buttons:
            button.setDisabled(False)

    def increase_font_size(self):
        if self.font_size < self.max_font_size:
            self.font_size += 1
            self.update_font()

    def decrease_font_size(self):
        if self.font_size > self.min_font_size:
            self.font_size -= 1
            self.update_font()

    def update_font(self):
        font = self.fontM
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

    def update_player_info(self):
        self.player_info_label.setText(f"Player Info - Position: ({self.current_room.x}, {self.current_room.y})")

    def update_player_stats(self):
        self.stats_text.clear()
        self.stats_text.setPlainText(
            f"Level: {self.player.level}\n"
            f"Hit Points: {self.player.hp}\n"
            f"Attack: {self.player.atk}\n"
            f"Defense: {self.player.defp}\n"
            f"Accuracy: {self.player.acc}\n"
            f"Defense: {self.player.ev}"
        )

    def initialize_game(self):
        # To refresh the genre selection and load a new map
        self.data_loader.select_random_genre()
        self.data_loader.create_game_map()
        self.game_map = self.data_loader.get_game_map()

    def start_game(self):
        self.data_loader.game_map.set_player(self.player)
        self.enable_all_buttons()
        if self.game_map:
            logging.info(f"Game_map object right here is {type(self.game_map)}")
            self.map_window = MapWindow(game_map=self.game_map)
        if self.start_button.text() == "Start":
            self.game_text_area.clear()
            self.game_text_area.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.game_text_area.setFont(self.fontM)
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
            self.initialize_game()
            self.game_text_area.clear()
            self.game_text_area.setAlignment(Qt.AlignCenter)
            game_title = self.data_loader.generate_game_title()
            format = QtGui.QTextCharFormat()
            format.setFont(self.fontB)
            cursor = self.game_text_area.textCursor()
            cursor.setCharFormat(format)
            cursor.insertText(game_title)
            format.setFont(self.fontT)
            cursor.insertBlock()
            cursor.setCharFormat(format)
            cursor.insertText("a procedurally generated text adventure by j menard\n")
            cursor.insertText("YOSL 2023")
            self.start_button.setText("Start")
            self.font_size_increase_button.setEnabled(False)
            self.font_size_decrease_button.setEnabled(False)
            self.game_text_area.moveCursor(QtGui.QTextCursor.End)
            self.hide_map()

    def update_inventory_text(self):
        inventory_text = ""
        for item in self.game_map.player.inventory:
            inventory_text += f"{item.name}\n"
        self.inventory_text.setText(inventory_text)

    def refresh_room(self):
        self.update_interact_button()
        available_directions = [direction for direction, room in self.current_room.connected_rooms.items() if room is not None]
        available_directions = ", ".join(available_directions)
        travel_options = f"You can go: {available_directions}"
        self.game_text_area.append(travel_options)
        self.game_text_area.moveCursor(QtGui.QTextCursor.End)
        self.map_window.update_map()

    def travel(self, direction):
        if direction in self.current_room.connected_rooms:
            next_room = self.current_room.connected_rooms[direction]
            if next_room is None:
                self.game_text_area.append("You can't go that way.")
                self.game_text_area.moveCursor(QtGui.QTextCursor.End)
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
        elif current_room.enemy and not current_room.enemy.is_dead:
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
        elif self.interact_button.text() == "Attack":
            try:
                self.game_text_area.append(f"{current_room.enemy.name} readies itself for battle. Combat has begun!\n")
                self.combat_object = Combat(self.game_map.player, [], [current_room.enemy], self)
                self.combat_object.combatUpdateSignal.connect(self.update_combat_text)
                self.combat_object.statsUpdateSignal.connect(self.update_player_stats)
                self.combat_object.combatEndSignal.connect(self.combat_object.stop_combat)
                self.combat_object.battleEndSignal.connect(self.end_of_battle)
                self.combat_thread = QThread()
                self.combat_object.moveToThread(self.combat_thread)
                self.combat_thread.started.connect(self.combat_object.combat)
                self.combat_thread.finished.connect(self.combat_object.stop_combat)
                self.combat_thread.finished.connect(self.combat_thread.deleteLater)
                self.combat_thread.finished.connect(self.combat_object.deleteLater)
                self.combat_thread.start()
            except Exception:
                logging.exception("Caught an error")
        elif self.interact_button.text() == "Use Key":
            self.data_loader.game_map = "" # we'll have to figure this out later
            self.data_loader.game_map.set_player(self.player) 
        self.game_text_area.moveCursor(QtGui.QTextCursor.End)

    def update_combat_text(self, text):
        self.game_text_area.append(text)
        self.game_text_area.moveCursor(QtGui.QTextCursor.End)

    def show_self(self):
        self.show()
        print(self.isVisible())
        self.update_map()

    def hide_map(self):
        self.map_window.hide()

    def end_of_battle(self):
        enemy = self.combat_object.enemies[0]
        rounds = self.combat_object.rounds
        p_hit_rate = self.combat_object.p_successful_attacks / rounds * 100
        e_hit_rate = self.combat_object.e_successful_attacks / rounds * 100
        p_total_dmg = self.combat_object.p_total_damage
        e_total_dmg = self.combat_object.e_total_damage
        if self.player.hp > 0:
            enemy.is_dead = True
            xp_award = enemy.calculate_xp_award(self.player.level)
            level_before = self.player.level
            self.player.gain_xp(xp_award)
            level_after = self.player.level
            message = f"In {rounds} rounds, you defeated a level {enemy.level} {enemy.name} and gained {int(enemy.calculate_xp_award(self.player.level))} XP.\n"
            message += f"Player Hit rate: {int(p_hit_rate)}%, Total Player Damage dealt: {p_total_dmg}\n" 
            message += f"Enemy Hit rate: {int(e_hit_rate)}%, Total Enemy Damage dealt: {e_total_dmg}\n"
            self.game_text_area.append(message)
            enemy.name = "dead " + enemy.name
            if level_after > level_before:
                self.game_text_area.append(f"You leveled up! You're now level {self.player.level}!\n")
            
            self.update_player_stats() 
            # Expand on the gains here ater, listing the old stats and the new ones like Attack: 30 > 32, or something like this.
            self.refresh_room()
        else:
            # Game Over
            self.game_text_area.append(f"You have been defeated. Please restart to continue.\n")
            self.disable_all_buttons()


class MapWindow(QWidget):
    def __init__(self, game_map):
        self.game_map = game_map
        super(MapWindow, self).__init__()
        self.setWindowTitle("Game Map")
        self.setGeometry(950, 100, 500, 400)
        self.layout = QHBoxLayout()
        self.room_type_legend_labels = {}
        self.fontA = QFont("Roboto", 7)
        self.fontB = QFont("Fira Sans Medium", 14)
        self.backColor = "#b1b1fa"
        self.textColor = "#000088"
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet(f"background-color: {self.backColor};")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.legend_widget = QWidget()
        self.legend_widget.setMinimumWidth(100)
        self.legend_widget.setStyleSheet(f"background-color: {self.backColor};")
        self.legend_layout = QVBoxLayout(self.legend_widget)
        self.room_type_legend_widget = QWidget()
        self.room_type_legend_widget.setMinimumWidth(100)
        self.room_type_legend_widget.setStyleSheet(f"background-color: {self.backColor};")
        self.room_type_legend_layout = QVBoxLayout(self.room_type_legend_widget)
        self.legend_labels = {
            QPixmap(self.resource_path("img/player.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Player"),
            QPixmap(self.resource_path("img/enemy.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Enemy"),
            QPixmap(self.resource_path("img/weapon.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Weapon"),
            QPixmap(self.resource_path("img/armor.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Armor"),
            QPixmap(self.resource_path("img/key.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Key"),
            QPixmap(self.resource_path("img/lock.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Lock"),
            QPixmap(self.resource_path("img/ally.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Ally"),
            QPixmap(self.resource_path("img/new_empty.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel('Room')
        }
        for pixmap, label in self.legend_labels.items():
            legend_item_layout = QHBoxLayout()
            legend_item_widget = QWidget()
            pixmap_label = QLabel()
            pixmap_label.setPixmap(pixmap)
            legend_item_layout.addWidget(pixmap_label)
            label.setFont(self.fontA)
            label.setStyleSheet(f"background-color: {self.backColor}; color: {self.textColor};")
            label.setAlignment(Qt.AlignCenter)
            legend_item_layout.addWidget(label)
            legend_item_widget.setLayout(legend_item_layout)
            self.legend_layout.addWidget(legend_item_widget)

        self.layout.addWidget(self.legend_widget)
        self.layout.addWidget(self.grid_widget)
        self.layout.addWidget(self.room_type_legend_widget)
        try:
           self.labels = [[None for _ in range(2*game_map.grid_width - 1)] for _ in range(2*game_map.grid_height - 1)]
        except Exception as e:
            logging.error(traceback.format_exc())
        for i in range(2*game_map.grid_height - 1):
            for j in range(2*game_map.grid_width - 1):
                self.labels[i][j] = QLabel(' ')
                self.labels[i][j].setAlignment(Qt.AlignCenter)
                if i % 2 == 0 and j % 2 == 0:
                    self.labels[i][j].setStyleSheet("background-color: white; min-width: 50px; min-height: 50px; font-size: 10px;")  # Change font size to 10px
                else:
                    self.labels[i][j].setStyleSheet(f"background-color: {self.backColor}; min-width: 10px; min-height: 10px;")
                self.grid_layout.addWidget(self.labels[i][j], i, j)
        self.room_pixmaps = {
            "player": QPixmap(self.resource_path("img/player.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "enemy": QPixmap(self.resource_path("img/enemy.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "weapon": QPixmap(self.resource_path("img/weapon.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "armor": QPixmap(self.resource_path("img/armor.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "key": QPixmap(self.resource_path("img/key.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "lock": QPixmap(self.resource_path("img/lock.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "ally": QPixmap(self.resource_path("img/ally.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "empty": QPixmap(self.resource_path("img/new_empty.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            }
        self.setLayout(self.layout)
        self.room_type_colors = {}
        self.update_map()
        self.create_room_type_legend()

    def resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def update_map(self):
        try:
            all_the_colors = [
                "cyan", "magenta", "silver", "orange", "pink", "violet", 
                "coral", "lavender", "turquoise", "skyblue", "salmon", "peachpuff", 
                "chartreuse", "firebrick", "indigo", "khaki", "olive", "peru", 
                "plum", "sienna", "teal", "thistle", "tomato", "navajowhite", "wheat", 
                "springgreen", "royalblue", "saddlebrown", "seashell", "snow", "steelblue", 
                "tan", "slategray", "lightcyan", "mintcream", "palevioletred"
            ]           
            for room in self.game_map.rooms:
                if room is not None:
                    if (0 <= 2*room.y < len(self.labels)) and (0 <= 2*room.x < len(self.labels[0])):
                        room_label = self.labels[2*room.y][2*room.x]
                        room_label.setAlignment(Qt.AlignCenter)
                        # set type background

                        if room.type not in self.room_type_colors:
                            random.shuffle(all_the_colors)
                            shuffled_colors = all_the_colors
                            color_choice = shuffled_colors.pop(0)
                            self.room_type_colors[room.type] = color_choice
                            
                            room_type_text_label = QLabel(room.type)
                            room_type_text_label.setFont(self.fontA)
                            room_type_text_label.setStyleSheet(f"background-color: {color_choice}; border: 1px solid black; color: {self.textColor};")
                            room_type_text_label.setAlignment(Qt.AlignCenter)
                            self.room_type_legend_labels[room.type] = room_type_text_label
                        else:
                            color_choice = self.room_type_colors[room.type]
                        
                        if room == self.game_map.player.current_room:
                            room_label.setPixmap(self.room_pixmaps["player"])
                            room_label.setStyleSheet("background-color: lime; border: 2px dashed black")
                        elif room.enemy:
                            room_label.setPixmap(self.room_pixmaps["enemy"])
                            room_label.setStyleSheet("background-color: red;")
                        elif room.weapon:
                            room_label.setPixmap(self.room_pixmaps["weapon"])
                            room_label.setStyleSheet("background-color: whitesmoke;")
                        elif room.armor:
                            room_label.setPixmap(self.room_pixmaps["armor"])
                            room_label.setStyleSheet("background-color: paleturquoise;")
                        elif room.key_item:
                            room_label.setPixmap(self.room_pixmaps["key"])
                            room_label.setStyleSheet("background-color: gold;")
                        elif room.lock_item:
                            room_label.setPixmap(self.room_pixmaps["lock"])
                            room_label.setStyleSheet("background-color: goldenrod;")
                        elif room.ally:
                            room_label.setPixmap(self.room_pixmaps["ally"])
                            room_label.setStyleSheet("background-color: yellow;")
                        else:
                            room_label.setPixmap(self.room_pixmaps["empty"])
                            room_label.setStyleSheet(f"background-color: {color_choice};")
                        
                        for direction, connected_room in room.connected_rooms.items():
                            if connected_room is not None:
                                connection_label = None
                                if direction == "north" and 2*room.y - 1 >= 0:
                                    connection_label = self.labels[2*room.y - 1][2*room.x]
                                    connection_label.setStyleSheet("background-color: seashell; min-height: 10px;")
                                elif direction == "south" and 2*room.y + 1 < len(self.labels):
                                    connection_label = self.labels[2*room.y + 1][2*room.x]
                                    connection_label.setStyleSheet("background-color: seashell; min-height: 10px;")
                                elif direction == "west" and 2*room.x - 1 >= 0:
                                    connection_label = self.labels[2*room.y][2*room.x - 1]
                                    connection_label.setStyleSheet("background-color: seashell; min-width: 10px;")
                                elif direction == "east" and 2*room.x + 1 < len(self.labels[0]):
                                    connection_label = self.labels[2*room.y][2*room.x + 1]
                                    connection_label.setStyleSheet("background-color: seashell; min-width: 10px;")
                                if connection_label is not None:
                                    connection_label.setAlignment(Qt.AlignCenter)
        except Exception as e:
            logging.error(f"Error occurred during update_map function: {e}")
    
    def create_room_type_legend(self):
        for room_type_label in self.room_type_legend_labels.values():
            room_type_label.setWordWrap(True)
            self.room_type_legend_layout.addWidget(room_type_label)

    def show_self(self):
        self.show()


