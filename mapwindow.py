import logging
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
        except Exception as e:
            logging.error(f"Error occurred during update_map function: {e}")
    
    def create_room_type_legend(self):
        for room_type_label in self.room_type_legend_labels.values():
            room_type_label.setWordWrap(True)
            self.room_type_legend_layout.addWidget(room_type_label)

    def show_self(self):
        self.show()
