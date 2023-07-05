import colorsys
from combat import Combat
from game_logic import Player, Key
import logging
from mapwindow import MapWindow
from matplotlib import colors
from PySide6.QtWidgets import QWidget, QGridLayout, QTextEdit, QLabel, QPushButton, QSizePolicy, QHBoxLayout, QVBoxLayout, QFrame, QGridLayout
from PySide6.QtCore import Qt, QCoreApplication, QThread, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6 import QtGui
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor
import random

class GameGUI(QWidget):
    def __init__(self, data_loader=None):
        super().__init__()
        self.player = None
        self.set_color_scheme()
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

        self.set_fonts()
        
        main_layout = QVBoxLayout() # top level layout is a QVBox
        self.setLayout(main_layout)
    
        self.player_info_label = QLabel("") # player info section, single-row-height at the very top of the window stretching almost the whole width
        self.player_info_label.setFont(self.font_title)
        player_info_layout = QHBoxLayout() 
        player_info_layout.addWidget(self.player_info_label)

        self.font_size_decrease_button = QPushButton("-") # text size buttons, not currently working but do need styling
        self.font_size_decrease_button.setEnabled(False)
        self.font_size_decrease_button.setFixedWidth(20)
        self.font_size_increase_button = QPushButton("+")
        self.font_size_increase_button.setEnabled(False)
        self.font_size_increase_button.setFixedWidth(20)
        player_info_layout.addWidget(self.font_size_decrease_button)
        player_info_layout.addWidget(self.font_size_increase_button)
        self.font_size_decrease_button.clicked.connect(self.decrease_font_size)
        self.font_size_increase_button.clicked.connect(self.increase_font_size)
        main_layout.addLayout(player_info_layout)
        
        self.game_text_area = QTextEdit() # Main text area, starting under the player info section and taking up most of the window
        self.game_text_area.setReadOnly(True)
        self.game_text_area.setAlignment(Qt.AlignCenter)
        self.game_text_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)        
        main_layout.addWidget(self.game_text_area)
        
        self.initialize_game(won=False) # Instantiate the GameMap and Player from scratch
        self.player = Player() # The main Player object is here; all other methods/classes should operate on this one

        game_title = self.data_loader.generate_game_title() # and set the treasure for the map
        self.treasure = self.data_loader.treasure

        format = QtGui.QTextCharFormat()
        font = QFont({self.font_m}, 52)
        format.setFont(font)
        cursor = self.game_text_area.textCursor()
        cursor.setCharFormat(format)
        cursor.insertText(game_title)
        format.setFont(self.font_title)
        cursor.insertBlock()
        cursor.setCharFormat(format)
        self.subLine = random.choice(self.subsToChoose)
        cursor.insertText(f"\na procedurally generated text adventure by j menard \n{self.subLine}\n")
        
        lowest_row_height = 280
        self.start_button = QPushButton("s(T)art")
        self.start_button.setFont(self.font_title)
        self.quit_button = QPushButton("(Q)uit")
        self.quit_button.setFont(self.font_title)
        self.start_button.clicked.connect(self.start_game)
        self.quit_button.clicked.connect(QCoreApplication.instance().quit)
        
        self.stats_label = QLabel("Player Stats")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setFont(self.font_title)
        self.stats_text = QTextEdit()
        new_font = self.font_main.family()
        stats_font = QFont(new_font, 12) # special font size adjustment to make sure they all fit vertically
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
        self.north_button.setFont(self.font_title)
        self.west_button = QPushButton("(W)est")
        self.west_button.setFont(self.font_title)
        self.east_button = QPushButton("(E)ast")
        self.east_button.setFont(self.font_title)
        self.south_button = QPushButton("(S)outh")
        self.south_button.setFont(self.font_title)
        self.interact_button = QPushButton("Interact(X)")
        self.interact_button.setFont(self.font_title)
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
        self.inventory_label.setFont(self.font_title)
        self.inventory_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.inventory_text = QTextEdit()
        self.inventory_text.setFont(self.font_main)
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
        self.update_player_stats()

    def set_color_scheme(self):
        # choose the color scheme
        self.all_the_colors = [
                "cyan", "magenta", "silver", "orange", "pink", "violet", 
                "coral", "lavender", "turquoise", "skyblue", "salmon", "peachpuff", 
                "chartreuse", "firebrick", "indigo", "khaki", "olive", "peru", 
                "plum", "sienna", "teal", "thistle", "tomato", "navajowhite", "wheat", 
                "springgreen", "royalblue", "saddlebrown", "seashell", "snow", "steelblue", 
                "tan", "slategray", "lightcyan", "mintcream", "palevioletred"
            ]
        base_color = self.all_the_colors[random.randint(0, len(self.all_the_colors) -1)]
        rgb_base_color = colors.cnames[base_color]
        hsv_base_color = colorsys.rgb_to_hsv(*colors.hex2color(rgb_base_color))
        shades_of_base_color = []
        num_shades = 2
        for i in range(num_shades):
            h = (hsv_base_color[0] + i/float(num_shades)) % 1
            rgb_shade = colorsys.hsv_to_rgb(h, hsv_base_color[1], hsv_base_color[2])
            shades_of_base_color.append(self.rgb_to_hex((int(rgb_shade[0]*255), int(rgb_shade[1]*255), int(rgb_shade[2]*255))))
        self.color_one = shades_of_base_color[0]
        self.color_two = shades_of_base_color[1]
        return shades_of_base_color

    def set_fonts(self):
        self.font_size = 14
        self.min_font_size = 10
        self.max_font_size = 30
        # randomize the fonts
        self.chooseFonts = ["Bebas Neue", "Cinzel", "Playfair Display", "Montserrat", "Raleway", "Roboto Slab", "Oswald", "Lato", "Open Sans", 
                            "Droid Serif", "Merriweather", "Arvo", "PT Sans", "Ubuntu", "Lora", "Bitter"]
        self.font_t= random.choice(self.chooseFonts)
        self.font_m = random.choice(self.chooseFonts)
        retries = 0
        while self.font_t == self.font_m and retries < 10: # ensure two different fonts are chosen
            retries += 1
            self.font_m = random.choice(self.chooseFonts)
        self.font_title = QFont(self.font_t, 14)
        self.font_main = QFont(self.font_m, 14)
        print(f"Titles font set to: {self.font_t}")
        print(f"Main font set to {self.font_m}")

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
        font = self.font_main
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
        self.data_loader.select_random_genre() # To refresh the genre selection and load a new map
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
        self.game_text_area.setStyleSheet(f"background-color: {self.color_one};")
        self.enable_all_buttons()
        self.update_player_stats()
        if self.game_map:
            self.map_window = MapWindow(game_map=self.game_map, player=self.player)
            self.map_window.setFixedSize(self.width(), self.height())
            map_window_x = self.geometry().x() + self.width()
            map_window_y = self.frameGeometry().y()
            self.map_window.move(map_window_x, map_window_y)
            QTimer.singleShot(100, self.regain_focus) # return focus to main window
        if self.start_button.text() == "s(T)art":
            self.game_text_area.clear()
            self.game_text_area.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.game_text_area.setFont(self.font_main)
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
            self.initialize_game(won=False) # character chooses restart
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
            format.setFont(self.font_title)
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
                print(f"Ally is: {self.player.ally.name}.")
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
            print(f"Ally name is: {self.player.ally.name}")

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
        self.game_text_area.append(f"You use the {self.player.key.name} to open the {self.player.current_room.lock_item.name}!")
        QTimer.singleShot(3000, self.beat_the_level1)
    
    def beat_the_level1(self):
        self.game_text_area.clear()
        self.game_text_area.append(f"From within the {self.player.current_room.lock_item.name}, a light begins to grow brighter and brighter, enveloping everything.")
        self.player.key = None
        QTimer.singleShot(3000, self.beat_the_level2)

    def beat_the_level2(self):
        self.game_text_area.clear()
        self.game_text_area.append(f"You find yourself in another place, deeper down the rabbit hole...")
        QTimer.singleShot(3000, self.beat_the_level3)

    def beat_the_level3(self):
        self.game_text_area.clear()
        self.game_text_area.setStyleSheet(f"background-color: black;")
        QTimer.singleShot(2000, self.beat_the_level4)
    
    def beat_the_level4(self):
        self.game_text_area.setStyleSheet(f"background-color: {self.color_one};")
        game_title = self.data_loader.generate_game_title()
        format = QtGui.QTextCharFormat()
        font_choice = random.choice(self.chooseFonts)
        font = QFont({font_choice}, 52)
        format.setFont(font)
        cursor = self.game_text_area.textCursor()
        cursor.setCharFormat(format)
        cursor.insertText(game_title)
        quote = random.choice(['"And what is the use of a book,” thought Alice, “without pictures or conversations?"',
                               '"How funny it will seem to come out among the people that walk with their heads downwards! The antipathies, I think—"',
                               '“Oh, how I wish I could shut up like a telescope! I think I could, if only I knew how to begin.” For, you see, so many out-of-the-way things had happened lately, that Alice had begun to think that very few things indeed were really impossible.',
                               'It was all very well to say "Drink me," but the wise little Alice was not going to do that in a hurry. "No, I will look first," she said, "and see whether it is marked poison or not."',
                               '“But it is no use now," thought poor Alice, "to pretend to be two people! Why, there is hardly enough of me left to make one respectable person!"',
                               '“Curiouser and curiouser!” cried Alice (she was so much surprised, that for the moment she quite forgot how to speak good English).',
                               '“I wish I had not cried so much!” said Alice, as she swam about, trying to find her way out. “I shall be punished for it now, I suppose, by being drowned in my own tears! That will be a queer thing, to be sure! However, everything is queer to-day.”',
                               '“When I used to read fairy tales, I fancied that kind of thing never happened, and now here I am in the middle of one!”',
                               '“Well! I have often seen a cat without a grin,” thought Alice; “but a grin without a cat! It is the most curious thing I ever saw in all my life!”',
                               '“How do you like the Queen?” said the Cat in a low voice.\n“Not at all,” said Alice: “she is so extremely—” Just then she noticed that the Queen was close behind her, listening: so she went on “—likely to win, that it is hardly worth while finishing the game.”',
                               '“Speak English!” said the Eaglet. “I do not know the meaning of half those long words, and, what\'s more, I don\'t believe you do either!”',
                               '“The Duchess! The Duchess! Oh my dear paws! Oh my fur and whiskers! She\'ll get me executed, as sure as ferrets are ferrets!” ',
                               'This was not an encouraging opening for a conversation. Alice replied, rather shyly, “I—I hardly know, Sir, just at present—at least I know who I was when I got up this morning, but I think I must have been changed several times since then.”',
                               '“What do you mean by that?” said the Caterpillar, sternly. “Explain yourself!”\n“I can\'t explain myself, I\'m afraid, Sir,” said Alice, “because I am not myself, you see.”',
                               '“Would you tell me, please, which way I ought to go from here?”\n “That depends a good deal on where you want to get to,” said the Cat.\n“I don\'t much care where—” said Alice. “Then it doesn\'t matter which way you go,” said the Cat. “—so long as I get somewhere,” Alice added as an explanation. \n“Oh, you\'re sure to do that,” said the Cat, “if you only walk long enough.”',
                               '“In that direction,” the Cat said, waving its right paw round, “lives a Hatter: and in that direction,” waving the other paw, “lives a March Hare. Visit either you like: they\'re both mad.”\n“But I don\'t want to go among mad people,” Alice remarked.\n“Oh, you can\'t help that,” said the Cat: “we\'re all mad here. I\'m mad. You\'re mad.”\n“How do you know I\'m mad?” said Alice.\n“You must be,” said the Cat, “or you wouldn\'t have come here.” ',
                               '“To begin with,” said the Cat, “a dog\'s not mad. You grant that?”\n“I suppose so,” said Alice.\n“Well, then,” the Cat went on, “you see a dog growls when it\'s angry, and wags its tail when it\'s pleased. Now I growl when I\'m pleased, and wag my tail when I\'m angry. Therefore I\'m mad.”\n“I call it purring, not growling,” said Alice.\n“Call it what you like,” said the Cat',
                               '“If everybody minded their own business,” the Duchess said, in a hoarse growl, “the world would go round a deal faster than it does.”',
                               '“And the moral of that is—\'Oh, \'tis love, \'tis love, that makes the world go round!’”\n“Somebody said,” Alice whispered, “that it\'s done by everybody minding their own business!”\n“Ah well! It means much the same thing,” said the Duchess, digging her sharp little chin into Alice\'s shoulder as she added, “and the moral of that is—\'Take care of the sense, and the sounds will take care of themselves.\'”',
                               '“And the moral of that is—\'Be what you would seem to be\'—or, if you\'d like it put more simply—\'Never imagine yourself not to be otherwise than what it might appear to others that what you were or might have been was not otherwise than what you had been would have appeared to them to be otherwise.’”',
                               '“Have some wine,” the March Hare said in an encouraging tone.\nAlice looked all round the table, but there was nothing on it but tea. “I don\'t see any wine,” she remarked.\n“There isn\'t any,” said the March Hare.\n“Then it wasn\'t very civil of you to offer it,” said Alice angrily.\n“It wasn\'t very civil of you to sit down without being invited,” said the March Hare.',
                               '“When we were little,” the Mock Turtle went on at last, more calmly, though still sobbing a little now and then,” we went to school in the sea. The master was an old Turtle—we used to call him Tortoise—”\n“Why did you call him Tortoise, if he wasn\'t one?” asked Alice.\n“We called him Tortoise because he taught us,” said the Mock Turtle angrily. “Really you are very dull!”',
                               'The Queen turned crimson with fury, and, after glaring at her for a moment like a wild beast, began screaming “Off with her head! Off with—”\n“Nonsense!” said Alice, very loudly and decidedly, and the Queen was silent.'])        
        format.setFont(self.fontT)
        cursor.insertBlock()
        cursor.setCharFormat(format)
        cursor.insertText(f"{quote}")
        QTimer.singleShot(3000, self.restart_game_after_level_won)

    def restart_game_after_level_won(self):
        self.initialize_game(won=True)
        self.start_button.setText("s(T)art")
        self.start_game()
        self.game_text_area.moveCursor(QtGui.QTextCursor.End)

    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

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