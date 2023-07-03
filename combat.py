from PySide6.QtCore import QObject, Signal
import logging
import random
import time

class Combat(QObject):
    #threading signals
    combatUpdateSignal = Signal(str)
    combatEndSignal = Signal(str)

    def __init__(self, player, allies, enemies, game_gui):
        
        super().__init__()
        logging.basicConfig(filename='application.log', 
                level=logging.DEBUG, 
                filemode='w',  # 'w' means overwrite the file, 'a' means append
                format='%(asctime)s - %(levelname)s - %(message)s')
        self.running = False
        self.player = player
        self.allies = allies
        self.enemies = enemies
        self.game_gui = game_gui

    def combat_round(self):
        # Roll initiative and determine order
        characters = self.allies + self.enemies + [self.player]
        characters.sort(key=lambda x: x.roll_initiative(), reverse=True)
        # Start combat
        while self.running and self.player.hp > 0 and not all(enemy.hp <= 0 for enemy in self.enemies):
            for character in characters:
                if character.hp > 0:
                    if character.is_enemy:
                        # Select a random target (player or an ally)
                        targets = [self.player] + [ally for ally in self.allies if ally.hp > 0]
                        if targets:
                            target = random.choice(targets)
                            hit, damage, critical = character.attack(target)
                            if critical:
                                self.combatUpdateSignal.emit(f"{character.name} attacks {target.name} gets a critical hit, dealing {damage} damage!")
                            elif hit:
                                self.combatUpdateSignal.emit(f"{character.name} attacks {target.name} and hits for {damage} damage.")
                            else:
                                self.combatUpdateSignal.emit(f"{character.name} attacks {target.name} but misses.")
                    else:
                        # Select a random enemy
                        viable_enemies = [enemy for enemy in self.enemies if enemy.hp > 0]
                        if viable_enemies:
                            enemy = random.choice(viable_enemies)
                            hit, damage, critical = character.attack(enemy)
                            if critical:
                                self.combatUpdateSignal.emit(f"{character.name} attacks {enemy.name} gets a critical hit, dealing {damage} damage!")
                            elif hit:
                                self.combatUpdateSignal.emit(f"{character.name} attacks {enemy.name} and hits for {damage} damage.")
                            else:
                                self.combatUpdateSignal.emit(f"{character.name} attacks {enemy.name} but misses.")
                    # Update GUI here if necessary
                    time.sleep(3)
                # Check if all enemies or the player is defeated
                if self.player.hp <= 0 or all(enemy.hp <= 0 for enemy in self.enemies):
                    self.combatEndSignal.emit()
                    self.running = False
                    break

    def combat(self):
        self.running = True
        while self.running:
            self.combat_round()
        self.thread().quit()

    def stop_combat(self):
        self.running = False