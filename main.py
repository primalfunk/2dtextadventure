from game_gui import DataLoader
import logging
from PySide6.QtWidgets import QApplication
from game_gui import GameGUI

if __name__ == "__main__":
    app = QApplication([])
    logging.basicConfig(filename='my_errors.log', 
                    level=logging.DEBUG, 
                    filemode='w',  # 'w' means overwrite the file, 'a' means append
                    format='%(asctime)s - %(levelname)s - %(message)s')
    game_init = DataLoader("data.json")
    game_gui = GameGUI(data_loader=game_init)

    app.exec()