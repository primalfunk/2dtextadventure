from game_logic.data_loader import DataLoader
from game_logic.game_gui import GameGUI
import logging
import os
from PySide6.QtWidgets import QApplication
import sys

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication([])
    logging.basicConfig(filename='my_errors.log', 
                    level=logging.DEBUG, 
                    filemode='w')
    json_file_path = resource_path("./data/data.json")
    game_init = DataLoader(json_file_path)
    game_gui = GameGUI(data_loader=game_init)
    app.exec()