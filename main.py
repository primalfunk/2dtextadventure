<<<<<<< HEAD
from PySide6.QtWidgets import QApplication
from game_gui import GameGUI, load_game_data

def main():
    app = QApplication([])
    game_data = load_game_data('game_data.json')
    game_gui = GameGUI(game_data)
    app.exec()

if __name__ == '__main__':
=======
from PySide6.QtWidgets import QApplication
from game_gui import GameGUI, load_game_data

def main():
    app = QApplication([])
    game_data = load_game_data('game_data.json')
    game_gui = GameGUI(game_data)
    app.exec()

if __name__ == '__main__':
>>>>>>> main
    main()