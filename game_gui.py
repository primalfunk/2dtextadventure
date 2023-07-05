from combat import Combat
from game_logic import GameMap, Player, Key
import json
import logging
import os
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QTextEdit, QLabel, QPushButton, QSizePolicy, QHBoxLayout, QVBoxLayout, QFrame, QGridLayout
from PySide6.QtCore import Qt, QCoreApplication, QThread, Signal, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6 import QtGui
from PySide6 import QtCore
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QPixmap
import random
import sys
import time
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

class GameGUI(QWidget):
    def __init__(self, data_loader=None):
        super().__init__()
        self.player = None
        self.subsToChoose = [
        "2023 all wrongs left unreserved",
        "2023 more rights than a roundabout",
        "2023 right-hand traffic not guaranteed",
        "2023 your rights are in another castle",
        "2023 rights reserved but we lost the reservation",
        "2023 we asked for rights they sent us lefts",
        "2023 all rights reversed",
        "2023 no rights were harmed in the making",
        "2023 rights have been left in the past",
        "2023 rights not included",
        "2023 rights are overrated",
        "2023 not even wrongs are reserved",
        "2023 rights sold separately",
        "2023 please mind your rights",
        "2023 some rights reserved others misplaced",
        "2023 rights went left never came back",
        "2023 rights are left to your imagination",
        "2023 all rights, no lefts",
        "2023 rights are not right right now",
        "2023 rights are having a timeout",
        "2023 rights once left are never right",
        "2023 rights took the wrong turn",
        "2023 rights have left the chat",
        "2023 rights not even once",
        "2023 no rights to begin with",
        "2023 little to no rights reserved",
        "2023 some rights reserved but you have to guess which",
        "2023 your rights are my rights your lefts my lefts",
        "2023 lefts are not wrong but rights are always correct",
        "2023 this is my rights there are many like it but this one is mine"
        "2023 this right is my right, it isn't your right"
        ]
        # gain focus immediately when created
        self.setFocusPolicy(Qt.StrongFocus)
        self.combat_object = None
        self.combat_thread = None
        self.data_loader = data_loader
        self.game_map = None
        self.chooseFonts = ["FoglihtenNo07calt", "FoglihtenNo04,", "Foglihten", "GlukMixer", "Mas Pendi Wow", "Great Vibes", "a Antara Distance", "a Anggota", "g Gerdu"]
        self.fontT = QFont("Roboto", 13)
        self.fontM = QFont("Fira Sans Medium", 16)
        self.font_size = 14
        self.min_font_size = 10
        self.max_font_size = 30
        self.backColorA = "#b1b1fa" # light blue
        self.backColorB = "powderblue"
        self.textColorA = "#000088" # darker blue
        self.textColorB = "black"
        
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
        # Player set up
        self.initialize_game(won=False)
        self.player = Player()
        game_title = self.data_loader.generate_game_title()
        format = QtGui.QTextCharFormat()
        font_choice = random.choice(self.chooseFonts)
        font = QFont({font_choice}, 52)
        format.setFont(font)
        cursor = self.game_text_area.textCursor()
        cursor.setCharFormat(format)
        cursor.insertText(game_title)
        format.setFont(self.fontT)
        cursor.insertBlock()
        cursor.setCharFormat(format)
        self.subLine = random.choice(self.subsToChoose)
        cursor.insertText(f"\na procedurally generated text adventure by j menard \n{self.subLine}\n")
        lowest_row_height = 280
        self.start_button = QPushButton("s(T)art")
        self.start_button.setFont(self.fontT)
        self.quit_button = QPushButton("(Q)uit")
        self.quit_button.setFont(self.fontT)
        self.start_button.clicked.connect(self.start_game)
        self.quit_button.clicked.connect(QCoreApplication.instance().quit)
        self.stats_label = QLabel("Player Stats")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setFont(self.fontT)
        self.stats_text = QTextEdit()
        new_font = self.fontM.family()
        stats_font = QFont(new_font, 12)
        self.stats_text.setFont(stats_font)
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
        self.north_button = QPushButton("(N)orth")
        self.north_button.setFont(self.fontT)
        self.west_button = QPushButton("(W)est")
        self.west_button.setFont(self.fontT)
        self.east_button = QPushButton("(E)ast")
        self.east_button.setFont(self.fontT)
        self.south_button = QPushButton("(S)outh")
        self.south_button.setFont(self.fontT)
        self.interact_button = QPushButton("Interact(X)")
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
        
        # Keyboard shortcuts
        shortcut_north = QShortcut(QKeySequence("n"), self)
        shortcut_south = QShortcut(QKeySequence("s"), self)
        shortcut_west = QShortcut(QKeySequence("w"), self)
        shortcut_east = QShortcut(QKeySequence("e"), self)
        shortcut_start = QShortcut(QKeySequence("t"), self)
        shortcut_quit = QShortcut(QKeySequence("q"), self)
        shortcut_interact = QShortcut(QKeySequence("x"), self)

        shortcut_north.activated.connect(self.travel_to_north)
        shortcut_south.activated.connect(self.travel_to_south)
        shortcut_west.activated.connect(self.travel_to_west)
        shortcut_east.activated.connect(self.travel_to_east)
        shortcut_start.activated.connect(self.start_game)
        shortcut_quit.activated.connect(QCoreApplication.instance().quit)
        shortcut_interact.activated.connect(self.interact)

        # Adding arrow key shortcuts
        shortcut_up = QShortcut(QKeySequence(Qt.Key_Up), self)
        shortcut_down = QShortcut(QKeySequence(Qt.Key_Down), self)
        shortcut_left = QShortcut(QKeySequence(Qt.Key_Left), self)
        shortcut_right = QShortcut(QKeySequence(Qt.Key_Right), self)

        shortcut_up.activated.connect(self.travel_to_north)
        shortcut_down.activated.connect(self.travel_to_south)
        shortcut_left.activated.connect(self.travel_to_west)
        shortcut_right.activated.connect(self.travel_to_east)
        
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

    def travel_to_north(self):
        self.travel("north")

    def travel_to_south(self):
        self.travel("south")

    def travel_to_west(self):
        self.travel("west")

    def travel_to_east(self):
        self.travel("east")
    
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
        print(f"Updating player info for player at {id(self.player)}")
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

    def initialize_game(self, won):
        # To refresh the genre selection and load a new map
        print(f"Load new genre")
        self.data_loader.select_random_genre()
        if not self.player or self.player.hp <= 0:
            print(f"Condition - create a new player object - self.player = Player()")
            self.player = Player()
            print(f"New player object created at {id(self.player)}")
        elif won:
            print(f"Keeping a player that's alive into the next level at {id(self.player)}")
        else:
            self.player = Player()
        self.data_loader.create_game_map(9, 9, self.player)
        self.game_map = self.data_loader.get_game_map()

    def start_game(self):
        self.game_text_area.setStyleSheet(f"background-color: {self.backColorA};")
        self.enable_all_buttons()
        self.update_player_stats()
        if self.game_map:
            self.map_window = MapWindow(game_map=self.game_map, player=self.player)
            self.map_window.setFixedSize(self.width(), self.height())
            map_window_x = self.geometry().x() + self.width()
            map_window_y = self.frameGeometry().y()
            self.map_window.move(map_window_x, map_window_y)
            # return focus to main window
            QTimer.singleShot(100, self.regain_focus)
        if self.start_button.text() == "s(T)art":
            self.game_text_area.clear()
            self.game_text_area.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.game_text_area.setFont(self.fontM)
            first_room = self.game_map.rooms[0]
            available_directions = [direction for direction, room in first_room.connected_rooms.items() if room is not None]
            room_description = f"<b>{first_room.name}</b><br><br>{first_room.description}<br><br>You can go: {', '.join(available_directions)}"
            self.game_text_area.append(room_description)
            self.player.x = first_room.x
            self.player.y = first_room.y
            self.player.current_room = first_room
            self.current_room = first_room
            self.update_player_info()
            self.start_button.setText("Res(T)art")
            self.font_size_increase_button.setEnabled(True)
            self.font_size_decrease_button.setEnabled(True)
            self.game_text_area.moveCursor(QtGui.QTextCursor.End)
            self.map_window.show_self()
            self.map_window.update_map()
        else:
            self.initialize_game(won=False)
            self.stats_text.clear()
            self.game_text_area.clear()
            self.game_text_area.setAlignment(Qt.AlignCenter)
            game_title = self.data_loader.generate_game_title()
            format = QtGui.QTextCharFormat()
            font_choice = random.choice(self.chooseFonts)
            print(f"font_choice: {font_choice}")
            font = QFont({font_choice}, 40)
            format.setFont(font)
            cursor = self.game_text_area.textCursor()
            cursor.setCharFormat(format)
            cursor.insertText(game_title)
            format.setFont(self.fontT)
            cursor.insertBlock()
            cursor.setCharFormat(format)
            self.subLine = random.choice(self.subsToChoose)
            cursor.insertText(f"a procedurally generated text adventure by j menard\n{self.subLine}\n")
            self.start_button.setText("s(T)art")
            self.font_size_increase_button.setEnabled(False)
            self.font_size_decrease_button.setEnabled(False)
            self.game_text_area.moveCursor(QtGui.QTextCursor.End)
            self.map_window = MapWindow(game_map=self.game_map, player=self.player)
            self.hide_map()

    def regain_focus(self):
            self.activateWindow()
            self.raise_()

    def update_inventory_text(self):
        inventory_text = ""
        for item in self.player.inventory:
            if item == self.player.weapon or item == self.player.armor:
                inventory_text += f"{item.name} (equipped)\n"
            else:
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
                self.player.y -= 1
            elif direction == "south":
                self.player.y += 1
            elif direction == "east":
                self.player.x += 1
            elif direction == "west":
                self.player.x -= 1
            self.current_room = next_room
            self.player.current_room = next_room
            self.game_text_area.clear()
            self.display_room(self.current_room)
            self.update_player_info()
            if self.player.ally is not None:
                self.player.ally.x = self.player.x
                self.player.ally.y = self.player.y
                self.player.ally.current_room.ally = None
                self.player.ally.current_room = self.current_room
                self.current_room.ally = self.player.ally
                self.game_text_area.append(f"{self.player.ally.name} arrives.")
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
        current_room = self.player.current_room
        if any([current_room.key_item, current_room.weapon, current_room.armor]): 
            self.interact_button.setText("Pick Up(X)")
        elif current_room.lock_item:
            has_key = any(isinstance(item, Key) for item in self.player.inventory)
            self.interact_button.setText("Unlock(X)") if has_key else self.interact_button.setText("Locked")
        elif current_room.enemy and not current_room.enemy.is_dead:
            self.interact_button.setText("Attack(X)")
        elif current_room.ally and self.player.ally is None:
            self.interact_button.setText("Greet(X)")
        else:
            self.interact_button.setText("Interact(X)")

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
        current_room = self.player.current_room
        if self.interact_button.text() == "Pick Up(X)":
            if current_room.key_item:
                item = current_room.key_item
                self.game_text_area.append(f"You pick up the {item.name}.")
                self.player.inventory.append(item)
                current_room.key_item = None
                self.player.key = item
            elif current_room.weapon:
                item = current_room.weapon
                if self.player.weapon:
                    # drop the existing weapon; remove from inventory and add to room
                    dropped_item = self.player.weapon
                    self.player.atk -= dropped_item.damage
                    self.player.acc -= dropped_item.accuracy
                    self.player.weapon = None
                    current_room.weapon = dropped_item
                    self.player.inventory.remove(dropped_item)
                    self.game_text_area.append(f"You drop the {dropped_item.name}.")
                self.game_text_area.append(f"You pick up the {item.name}.")
                self.player.inventory.append(item)
                self.player.weapon = item
                self.player.atk += item.damage
                self.player.acc += item.accuracy
                current_room.weapon = None
            
            elif current_room.armor:
                item = current_room.armor
                print(f"Armor is {item.name}")
                if self.player.armor:
                    dropped_item = self.player.armor
                    self.player.defp -= dropped_item.stats["defp"]
                    self.player.ev -= dropped_item.stats["ev"]
                    self.player.armor = None
                    current_room.armor = dropped_item
                    self.player.inventory.remove(dropped_item)
                    self.game_text_area.append(f"You drop the {dropped_item.name}.")
                self.game_text_area.append(f"You pick up the {item.name}.")
                self.player.inventory.append(item)
                self.player.defp += item.defense
                self.player.ev += item.evasion
                self.player.armor = item
                current_room.armor = None
            self.update_interact_button()
            self.update_inventory_text()
            self.update_player_stats()
        
        elif self.interact_button.text() == "Greet(X)":
            self.player.ally = self.current_room.ally
            self.game_text_area.append(f"{self.player.ally.name} starts following you.")

        elif self.interact_button.text() == "Attack(X)":
            try:
                self.game_text_area.append(f"\n{current_room.enemy.name} sees you and readies itself for battle. Combat has begun!\n")
                self.combat_object = Combat(self.player, [], [current_room.enemy], self)
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
        elif self.interact_button.text() == "Unlock(X)":
            # load a new game map and go on; reset everything except Player
            self.beat_the_level0()

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
            message = f"In {rounds} rounds, you defeated a level {enemy.level} {enemy.name} and gained {xp_award} XP.\n"
            message += f"Player Hit rate: {int(p_hit_rate)}%, Total Player Damage dealt: {p_total_dmg}\n" 
            message += f"Enemy Hit rate: {int(e_hit_rate)}%, Total Enemy Damage dealt: {e_total_dmg}\n"
            message += f"Current XP: {self.player.xp}, XP required for next level: {int(self.player.xp_required_to_level_up())}\n"
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
    
    def beat_the_level0(self):
        self.game_text_area.clear()
        self.game_text_area.append(f"\nYou use the {self.player.key.name} to open the {self.player.current_room.lock_item.name}!")
        QTimer.singleShot(5000, self.beat_the_level1)
    
    def beat_the_level1(self):
        self.game_text_area.clear()
        self.game_text_area.append(f"From within the {self.player.current_room.lock_item.name}, a light begins to grow brighter and brighter, enveloping everything.")
        self.player.key = None
        QTimer.singleShot(5000, self.beat_the_level2)

    def beat_the_level2(self):
        self.game_text_area.clear()
        self.game_text_area.append(f"You find yourself in another place...")
        QTimer.singleShot(5000, self.beat_the_level3)

    def beat_the_level3(self):
        self.game_text_area.setStyleSheet(f"background-color: black;")
        QTimer.singleShot(5000, self.restart_game_after_level_won)

    def restart_game_after_level_won(self):
        self.initialize_game(won=True)
        self.start_button.setText("s(T)art")
        self.start_game()
        self.game_text_area.moveCursor(QtGui.QTextCursor.End)

class AspectRatioWidget(QWidget):
    def __init__(self, widget):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(widget)
    
    def resizeEvent(self, e):
        w = e.size().width()
        h = e.size().height()

        if w > h:  # if the width is greater than the height
            widget_h = h
            widget_w = h
        else:  # if the width is less than or equal to the height
            widget_w = w
            widget_h = w

        self._layout.itemAt(0).widget().resize(widget_w, widget_h)

class MapWindow(QWidget):
    def __init__(self, game_map, player):
        self.game_map = game_map
        self.player = player
        print(f"MapWindow initialized with player at {id(self.player)}")
        super(MapWindow, self).__init__()
        self.setWindowTitle("The Map of Maps")
        self.setWindowFlags(Qt.Window | Qt.WindowDoesNotAcceptFocus)
        self.layout = QHBoxLayout()
        self.room_type_legend_labels = {}
        self.fontA = QFont("Roboto", 7)
        self.backColor = "#b1b1fa"
        self.textColor = "#000088"
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet(f"background-color: {self.backColor};")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.legend_widget = QWidget()
        self.legend_widget.setMinimumWidth(100)
        self.legend_widget.setMaximumWidth(100)
        self.legend_widget.setStyleSheet(f"background-color: {self.backColor};")
        self.legend_layout = QVBoxLayout(self.legend_widget)
        self.room_type_legend_widget = QWidget()
        self.room_type_legend_widget.setMinimumWidth(100)
        self.room_type_legend_widget.setMaximumWidth(100)
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
        self.ar_widget_g = AspectRatioWidget(self.grid_widget)
        self.ar_widget_l = AspectRatioWidget(self.legend_widget)
        self.ar_widget_r = AspectRatioWidget(self.room_type_legend_widget)
        self.layout.addWidget(self.legend_widget)
        self.layout.addWidget(self.ar_widget_g)
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
                    self.labels[i][j].setStyleSheet("background-color: black; min-width: 50px; min-height: 50px; font-size: 10px;")  # Change font size to 10px
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

    def focusInEvent(self, event):
            self.focusGained.emit()
            super().focusInEvent(event)

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
                        if room == self.player.current_room:
                            room_label.setPixmap(self.room_pixmaps["player"])
                            room_label.setStyleSheet("background-color: lime; border: 2px dashed black")
                        elif room.enemy and not room.enemy.is_dead:
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


