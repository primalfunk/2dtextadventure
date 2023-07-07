import random

class Character:
    def __init__(self, level, hp=100, atk=35, defp=15, acc=45, ev=30, acc_gain=3, ev_gain=3, 
                 hp_gain=15, atk_gain=7, defp_gain=3, cap=80):
        self.level = level
        self.hp = hp
        self.atk = atk
        self.defp = defp
        self.acc = acc
        self.ev = ev
        self.acc_gain = acc_gain
        self.ev_gain = ev_gain
        self.hp_gain = hp_gain
        self.atk_gain = atk_gain
        self.defp_gain = defp_gain
        self.cap = cap
        self.total_damage_dealt = 0
        self.total_attacks = 0

    def level_up(self):
        self.level += 1
        self.hp += self.hp_gain + random.randint(-1, 1)
        self.atk += self.atk_gain + random.randint(-1, 1)
        self.defp += self.defp_gain + random.randint(-1, 1)
        self.acc += self.acc_gain + random.randint(-1, 1)
        self.ev += self.ev_gain + random.randint(-1, 1)
        self.acc_gain = max(1, self.acc_gain - 1)
        self.ev_gain = max(1, self.ev_gain - 1)
        self.acc = min(self.acc, self.cap)
        self.ev = min(self.ev, self.cap)
        self.hp_gain += random.randint(-2, 5)
        self.atk_gain += random.randint(4, 6)
        self.defp_gain += random.randint(4, 6)


class Weapon:
    def __init__(self, atk_boost=15, acc_boost=20):
        self.atk_boost = atk_boost
        self.acc_boost = acc_boost


class Armor:
    def __init__(self, defp_boost=15, ev_boost=30):
        self.defp_boost = defp_boost
        self.ev_boost = ev_boost


class Ally:
    def __init__(self, level=1, hp=100, atk=30, defp=20, acc=50, ev=50):
        self.level = level
        self.hp = hp
        self.atk = atk
        self.defp = defp
        self.acc = acc
        self.ev = ev
        self.total_damage_dealt = 0
        self.total_attacks = 0

class Battle:
    def __init__(self, player, weapon, armor, ally):
        self.player = player
        self.enemy = Character(level=1)
        self.weapon = weapon
        self.armor = armor
        self.ally = ally
        self.use_ally = False
        self.avg_hp = {'round1_hp': 0,
                       'round2_hp': 0,
                       'round3_hp': 0,
                       'round4:hp': 0
                       }
        self.wins = 0
        self.rounds = 0
        self.round_counts = []
        self.run_simulation()

    def pick_course(self, perk):
        if perk == "weapon":
            self.player.atk += self.weapon.atk_boost
            self.player.acc += self.weapon.acc_boost
        elif perk == "armor":
            self.player.defp += self.armor.defp_boost
            self.player.ev += self.armor.ev_boost
        elif perk == "ally":
            self.use_ally = True
        else:
            print(f"That's not a perk.")

    def run_simulation(self):
        self.wins = 0
        self.use_ally = False
        self.results = {
            'total_wins': 0,
            'weapon_wins': 0,
            'armor_wins': 0,
            'ally_wins': 0,
            'geared_up_wins': 0
        }
        self.perks = ["weapon", "armor", "ally"]
        random.shuffle(self.perks)
        # Initialize round win counters
        self.round_wins = {1: 0, 2: 0, 3: 0, 4: 0}
        self.round_battles = {1: 0, 2: 0, 3: 0, 4: 0}
        self.simulate_battles(1, self.player, self.enemy)
        first_perk = self.perks[0]
        self.pick_course(first_perk)
        self.enemy.level_up()
        if self.use_ally:
            self.avg_hp['round2_hp'] = self.simulate_battles(2, self.player, self.enemy, self.ally)
        else:
            self.avg_hp['round2_hp'] = self.simulate_battles(2, self.player, self.enemy)
        second_perk = self.perks[1]
        self.pick_course(second_perk)
        self.enemy.level_up()
        if self.use_ally:
            self.avg_hp['round3_hp'] = self.simulate_battles(3, self.player, self.enemy, self.ally)
        else:
            self.avg_hp['round3_hp'] = self.simulate_battles(3, self.player, self.enemy)
        third_perk = self.perks[2]
        self.pick_course(third_perk)
        self.enemy.level_up()
        self.avg_hp['round4_hp'] = self.simulate_battles(4, self.player, self.enemy, self.ally)


    def simulate_battles(self, round, player, enemy, ally=None, num_battles=100):
        total_remaining_hp = 0
        for _ in range(num_battles):
            player.hp, enemy.hp = 100, 100
            if self.simulate_battle(player, enemy, ally):
                total_remaining_hp += player.hp
                self.results['total_wins'] += 1
                if round == 4:
                    self.results['geared_up_wins'] += 1
                elif round < 4:    
                    if self.perks[round - 1] == "weapon":
                        self.results['weapon_wins'] += 1
                    elif self.perks[round - 1] == "armor":
                        self.results['armor_wins'] += 1
                    else:
                        self.results['ally_wins'] += 1
                self.round_wins[round] += 1
            else:
                total_remaining_hp += enemy.hp
        average_remaining_hp = total_remaining_hp / num_battles
        self.round_battles[round] += num_battles
        return num_battles

    def simulate_battle(self, player, enemy, ally=None):
        fight_rounds = 0
        while player.hp > 0 and enemy.hp > 0:
            fight_rounds += 1
            self.rounds += 1
            self.attack(player, enemy)
            if enemy.hp > 0:
                self.attack(enemy, player)
            if ally and enemy.hp > 0:
                self.attack(ally, enemy)
        if player.hp > 0:
            self.wins += 1
        self.round_counts.append(fight_rounds)
        return player.hp > 0

    def attack(self, attacker, target):
        hit_rate = self.calculate_hit_rate(attacker.acc, target.ev)
        if random.randint(1, 100) <= hit_rate:
            # if the attack is a hit, first apply half the target defp as a direct damage reduction
            damage = attacker.atk - (0.5 * target.defp)
            # block and deflect can further reduce damage
            block_chance = (target.ev / (attacker.acc + target.ev) * 0.3)
            deflect_chance = min(1, (target.ev / (attacker.acc + target.ev)) * 0.15)
            block = random.random() <= block_chance
            deflect = random.random() <= deflect_chance
            if deflect:
                damage = int(damage * 0.25)
            elif block:
                damage = int(damage * 0.5)

            if random.randint(1, 100) <= 2:
                damage = int(damage * random.uniform(1.5, 3))
            damage = int(max(damage, random.randint(1, 2)))
            attacker.total_damage_dealt += damage
            attacker.total_attacks += 1
            target.hp -= damage

    def calculate_hit_rate(self, acc, ev):
        return max(25, min(80, 50 * (acc / (acc + ev + 0.1))))

    def summarize(self):
        total_battles = 10000
        average_rounds = sum(self.round_counts) / total_battles
        min_rounds = min(self.round_counts)
        max_rounds = max(self.round_counts)
        player_average_damage = self.player.total_damage_dealt / self.player.total_attacks
        enemy_average_damage = self.enemy.total_damage_dealt / self.enemy.total_attacks
        print(f"Total battles: {total_battles}")
        print(f"Total wins: {self.results['total_wins'] / total_battles * 100:.2f}% (Count: {self.results['total_wins']})")
        print(f"Weapon wins: {self.results['weapon_wins'] / total_battles * 100:.2f}% (Count: {self.results['weapon_wins']})")
        print(f"Armor wins: {self.results['armor_wins'] / total_battles * 100:.2f}% (Count: {self.results['armor_wins']})")
        print(f"Ally wins: {self.results['ally_wins'] / total_battles * 100:.2f}% (Count: {self.results['ally_wins']})")
        print(f"Fully geared wins: {self.results['geared_up_wins'] / total_battles * 100:.2f}% (Count: {self.results['geared_up_wins']})")
        print(f"Average rounds per battle: {average_rounds}")
        print(f"Minimum rounds in a battle: {min_rounds}")
        print(f"Maximum rounds in a battle: {max_rounds}")
        print(f"Player average damage per attack: {round(player_average_damage, 2)}")
        print(f"Enemy average damage per attack: {round(enemy_average_damage, 2)}")
        print(f"Average remaining HP after round 1: {self.avg_hp['round1_hp']:.2f}")
        print(f"Average remaining HP after round 2: {self.avg_hp['round2_hp']:.2f}")
        print(f"Average remaining HP after round 3: {self.avg_hp['round3_hp']:.2f}")
        print(f"Average remaining HP after round 4: {self.avg_hp['round4_hp']:.2f}")

def main():
    battle = Battle()

if __name__ == "__main__":
    main()