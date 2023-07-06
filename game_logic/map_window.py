import colorsys
import logging
from matplotlib import colors
import os
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import random
import sys
import traceback


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
        self.font = QFont("Roboto", 7)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.legend_widget = QWidget()
        self.legend_widget.setMinimumWidth(100)
        self.legend_widget.setMaximumWidth(100)
        self.legend_layout = QVBoxLayout(self.legend_widget)
        self.room_type_legend_widget = QWidget()
        self.room_type_legend_widget.setMinimumWidth(100)
        self.room_type_legend_widget.setMaximumWidth(100)
        self.room_type_legend_layout = QVBoxLayout(self.room_type_legend_widget)
        self.text_color = "black"
        self.legend_labels = {
            QPixmap(self.resource_path("../img/player.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Player"),
            QPixmap(self.resource_path("../img/enemy.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Enemy"),
            QPixmap(self.resource_path("../img/weapon.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Weapon"),
            QPixmap(self.resource_path("../img/armor.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Armor"),
            QPixmap(self.resource_path("../img/key.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Key"),
            QPixmap(self.resource_path("../img/lock.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Lock"),
            QPixmap(self.resource_path("../img/ally.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel("Ally"),
            QPixmap(self.resource_path("../img/new_empty.png")).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation): QLabel('Room')
        }
        # Set up for the Item Legend
        for pixmap, label in self.legend_labels.items():
            legend_item_layout = QHBoxLayout()
            legend_item_widget = QWidget()
            pixmap_label = QLabel()
            pixmap_label.setPixmap(pixmap)
            legend_item_layout.addWidget(pixmap_label)
            label.setFont(self.font)
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
                    self.labels[i][j].setStyleSheet(f"background-color: blue; min-width: 10px; min-height: 10px;")
                self.grid_layout.addWidget(self.labels[i][j], i, j)
        self.room_pixmaps = {
            "player": QPixmap(self.resource_path("../img/player.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "enemy": QPixmap(self.resource_path("../img/enemy.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "weapon": QPixmap(self.resource_path("../img/weapon.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "armor": QPixmap(self.resource_path("../img/armor.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "key": QPixmap(self.resource_path("../img/key.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "lock": QPixmap(self.resource_path("../img/lock.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "ally": QPixmap(self.resource_path("../img/ally.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            "empty": QPixmap(self.resource_path("../img/new_empty.png")).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            }
        self.setLayout(self.layout)
        self.room_type_colors = {}
        self.room_type_border_colors = {}
        self.all_room_types = set(room.type for room in self.game_map.rooms if room is not None)
        print(f"All_room_types: {self.all_room_types}")
        self.num_room_types = len(self.all_room_types)
        all_the_colors = ["#FF0000","#00FF00","#0000FF","#FFFF00","#00FFFF","#FF00FF","#FF7F00","#00FF7F","#007FFF","#7F00FF","#FF007F","#7FFF00"]           
        base_color = all_the_colors[random.randint(0, len(all_the_colors) - 1)]
        rgb_base_color = colors.hex2color(base_color)
        hsv_base_color = colorsys.rgb_to_hsv(*rgb_base_color)
        self.num_shades = self.num_room_types * 2  # Total number of shades
        start_s, end_s = 0.1, 1
        start_v, end_v = 1, 0.1
        step_s = (end_s - start_s) / (self.num_shades - 1)
        step_v = (end_v - start_v) / (self.num_shades - 1)
        self.map_colors = []
        for i in range(self.num_shades):
                    s = start_s + i * step_s
                    v = start_v + i * step_v
                    rgb_shade = colorsys.hsv_to_rgb(hsv_base_color[0], s, v)
                    hex_color = self.rgb_to_hex((int(rgb_shade[0]*255), int(rgb_shade[1]*255), int(rgb_shade[2]*255)))
                    self.map_colors.append(hex_color)
        print(f"Map colors: {self.map_colors}")
        self.update_map()
        self.create_room_type_legend()
        print(f'Total widgets in room type legend: {self.room_type_legend_layout.count()}')
    
    def update_map(self):
        for i, room_type in enumerate(self.all_room_types):
            self.room_type_colors[room_type] = self.map_colors[i % self.num_shades]
            self.room_type_border_colors[room_type] = self.map_colors[(i + self.num_shades // 2) % self.num_shades] 
            color_choice = self.room_type_colors[room_type]
            room_type_text_label = QLabel(room_type)
            room_type_text_label.setFont(self.font)
            room_type_text_label.setStyleSheet(f"background-color: {color_choice}; border: 1px solid black; color: {self.text_color};")
            room_type_text_label.setAlignment(Qt.AlignCenter)
            self.room_type_legend_labels[room_type] = room_type_text_label
            print(f'Total room type labels: {len(self.room_type_legend_labels)}')

        print(f"Labels are: {self.room_type_legend_labels}")
        
        for room in self.game_map.rooms:
            if room is not None:
                if (0 <= 2*room.y < len(self.labels)) and (0 <= 2*room.x < len(self.labels[0])):
                    room_label = self.labels[2*room.y][2*room.x]
                    room_label.setAlignment(Qt.AlignCenter)
                    color_choice = self.room_type_colors[room.type]
                    if room == self.player.current_room:
                        room_label.setPixmap(self.room_pixmaps["player"])
                        room_label.setStyleSheet("background-color: lightgreen; border: 2px dashed black")
                    elif room.enemy and not room.enemy.is_dead:
                        room_label.setPixmap(self.room_pixmaps["enemy"])
                        room_label.setStyleSheet("background-color: red;")
                    elif room.weapon:
                        room_label.setPixmap(self.room_pixmaps["weapon"])
                        room_label.setStyleSheet("background-color: orange;")
                    elif room.armor:
                        room_label.setPixmap(self.room_pixmaps["armor"])
                        room_label.setStyleSheet("background-color: gold;")
                    elif room.key_item:
                        room_label.setPixmap(self.room_pixmaps["key"])
                        room_label.setStyleSheet("background-color: goldenrod;")
                    elif room.lock_item:
                        room_label.setPixmap(self.room_pixmaps["lock"])
                        room_label.setStyleSheet("background-color: darkorange;")
                    elif room.ally:
                        room_label.setPixmap(self.room_pixmaps["ally"])
                        room_label.setStyleSheet("background-color: skyblue;")
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
    
    def create_room_type_legend(self):
        print("Creating room type legend...")
        self.room_type_legend_widget.setLayout(self.room_type_legend_layout)
        for room_type_label in list(self.room_type_legend_labels.values()):
            if not isinstance(room_type_label, QWidget):
                print(f"{room_type_label.text()} is not a valid widget!")
                continue
            room_type_label.setWordWrap(True)
            self.room_type_legend_layout.addWidget(room_type_label)
            print(f'Added {room_type_label.text()} to room type legend')
            self.room_type_legend_widget.adjustSize()
            self.room_type_legend_widget.show()

    def focusInEvent(self, event):
            self.focusGained.emit()
            super().focusInEvent(event)

    def resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def show_self(self):
        self.show()

    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb
