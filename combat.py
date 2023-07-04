from PySide6.QtCore import QObject, Signal
import logging
import random
import time

class Combat(QObject):
    #threading signals
    combatUpdateSignal = Signal(str)
    statsUpdateSignal = Signal(str)
    combatEndSignal = Signal(str)
    battleEndSignal = Signal(str)

    def __init__(self, player, allies, enemies, game_gui):
        super().__init__()
        logging.basicConfig(filename='application.log', 
                level=logging.DEBUG, 
                filemode='w')
        self.running = False
        self.player = player
        self.allies = allies
        self.enemies = enemies
        self.game_gui = game_gui
        self.p_successful_crits = 0
        self.p_successful_attacks = 0
        self.p_total_damage = 0
        self.e_successful_crits = 0
        self.e_successful_attacks = 0
        self.e_total_damage = 0
        self.rounds = 0

    def combat_round(self):
        logging.info(f"Combat round started with: {self.player.name} Level {self.player.level} HP {self.player.hp} Atk {self.player.atk} Defp {self.player.defp} Acc {self.player.acc} Ev {self.player.ev}")
        if self.player.ally is None:
            logging.info(f"There are no allies present.")
        for enemy in self.enemies:
            logging.info(f"Enemy combatant is: {enemy.name} Level {enemy.level} HP {enemy.hp} Atk {enemy.atk} Defp {enemy.defp} Acc {enemy.acc} Ev {enemy.ev}")
        for ally in self.allies:
            logging.info(f"Ally is: {ally.name} Level {ally.level} HP {ally.hp} Atk {ally.atk} Defp {ally.defp} Acc {ally.acc} Ev {ally.ev}")
        characters = self.allies + self.enemies + [self.player]
        initiative_rolls = {character: character.roll_initiative() for character in characters}
        characters.sort(key=lambda x: initiative_rolls[x], reverse=True)
        logging.info("Initiative rolls:")
        for character, roll in initiative_rolls.items():
            logging.info(f"{character.name} rolls {roll} for initiative.")
        logging.info(f"Round move order:")
        move_orders = ""
        for char in characters:
            move_orders += f"{char.name} "
        logging.info(f"Move orders are: {move_orders}.")
        while self.running and self.player.hp > 0 and not all(enemy.hp <= 0 for enemy in self.enemies):
            round_text = ""
            for character in characters:
                if character.hp > 0:
                    if character.is_enemy:
                        targets = [self.player] + [ally for ally in self.allies if ally.hp > 0]
                        if targets:
                            target = random.choice(targets)
                            hit, damage, critical = self.attack(character, target)
                            if critical:
                                round_text += (f"{character.name} attacks {target.name} gets a critical hit, dealing {damage} damage!\n")
                                self.e_successful_crits += 1
                                self.e_successful_attacks += 1
                                self.e_total_damage += damage
                            elif hit:
                                round_text += (f"{character.name} attacks {target.name} and hits for {damage} damage.\n")
                                self.e_successful_attacks += 1
                                self.e_total_damage += damage
                            else:
                                round_text += (f"{character.name} attacks {target.name} but misses.\n")
                    else:
                        viable_enemies = [enemy for enemy in self.enemies if enemy.hp > 0]
                        if viable_enemies:
                            enemy = random.choice(viable_enemies)
                            hit, damage, critical = self.attack(character, enemy)
                            if critical:
                                round_text += (f"{character.name} attacks {enemy.name} gets a critical hit, dealing {damage} damage!\n")
                                self.p_successful_crits
                                self.p_successful_attacks += 1
                                self.p_total_damage += damage
                            elif hit:
                                round_text += (f"{character.name} attacks {enemy.name} and hits for {damage} damage.\n")
                                self.p_successful_attacks += 1
                                self.p_total_damage += damage
                            else:
                                round_text += (f"{character.name} attacks {enemy.name} but misses.\n")
            self.rounds += 1
            self.combatUpdateSignal.emit(round_text)
            self.statsUpdateSignal.emit("UpdatePlayerStats")
            time.sleep(2)
            if self.player.hp <= 0 or all(enemy.hp <= 0 for enemy in self.enemies):
                self.combatEndSignal.emit("Combat has ended.")
                self.battleEndSignal.emit("It's all over, folks.")
                self.running = False
                break

    def calculate_hit_rate(self, attacker_accuracy, defender_evasion):
        logging.info(f"Attacker accuracy: {attacker_accuracy}, defender evasion: {defender_evasion}")
        hit_chance = min(1, max(0.1, attacker_accuracy / (attacker_accuracy + defender_evasion)))
        # apply randomness
        hit_chance *= random.uniform(0.85, 1.15)
        logging.info(f"Calculated chance after 15% randomness: {int(hit_chance * 100)}")
        return int(hit_chance * 100)

    def combat(self):
        self.running = True
        while self.running:
            self.combat_round()
        self.thread().quit()

    def attack(self, attacker, target):
        hit_rate = self.calculate_hit_rate(attacker.acc, target.ev)
        if random.randint(1, 100) <= hit_rate:
            logging.info("The attack hits!")
            damage = attacker.atk - int(random.uniform(0.75, 1.1) * 0.5 * target.defp)
            block_chance = ( target.defp * 2 ) / 100
            deflect_chance = ( target.defp ) / 100
            block = random.random() <= block_chance
            deflect = random.random() <= deflect_chance
            adjusted_defp = round(target.defp * random.uniform(0.7, 1.3))
            if deflect:
                damage = int(damage * 0.25)
                logging.info(f"Successful deflect, quarter damage {damage}.")
            elif block:
                damage = int(damage * 0.5)
                logging.info(f"Successful block, half damage {damage}.")
            damage -= int(adjusted_defp * 0.5)
            if random.randint(1, 100) <= 2.5:
                logging.info("Critical hit!")
                damage = int(damage * random.uniform(1.5, 3))
                critical = True
            else:
                critical = False
            damage = int(max(damage, random.randint(1, 3)))
            target.hp -= damage
            logging.info(f"***{target.name} has {target.hp} HP left.***")
            return True, damage, critical
        else:
            logging.info("The attack misses.")
            # Attack missed
            return False, 0, False

    def stop_combat(self):
        self.running = False