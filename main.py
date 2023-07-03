from game_gui import DataLoader
import logging
from PySide6.QtWidgets import QApplication
from game_gui import GameGUI



if __name__ == "__main__":
    app = QApplication([])
    logger = logging.getLogger()
    logger.handlers = []  # clear existing handlers
    handler = logging.FileHandler('my_errors.log', 'w')
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    game_init = DataLoader("data.json")
    game_gui = GameGUI(data_loader=game_init)

    game_gui.initialize_game(fresh=True)
    app.exec()