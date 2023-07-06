from game_logic.game_logic import Character
import gym
from gym import spaces
import logging
import numpy as np
import random

class CombatEnvironment(gym.Env):
    def __init__(self):
        super(CombatEnvironment, self).__init__()
        self.action_space = spaces.Box(low=-10, high=10, shape=(6,), dtype=np.float32)
        self.observation_space = spaces.Box(low=0, high=100, shape=(25,), dtype=np.float32)
        self.player = None  # Replace these placeholders with your game's player, ally, and enemy instances
        self.ally = None
        self.enemies = None
        self.round_number = 0

    def render(self):
        print(f"Player: Level {self.player.level}, HP {self.player.hp}, Atk {self.player.atk}, Defp {self.player.defp}, Acc {self.player.acc}, Ev {self.player.ev}")
        if self.ally:
            print(f"Ally: Level {self.ally.level}, HP {self.ally.hp}, Atk {self.ally.atk}, Defp {self.ally.defp}, Acc {self.ally.acc}, Ev {self.ally.ev}")
        for i, enemy in enumerate(self.enemies):
            print(f"Enemy {i}: Level {enemy.level}, HP {enemy.hp}, Atk {enemy.atk}, Defp {enemy.defp}, Acc {enemy.acc}, Ev {enemy.ev}")
        
    def attack(self, attacker, target_index):
        target = self.enemies[target_index]
        hit_rate = self.calculate_hit_rate(attacker.acc, target.ev)
        if random.randint(1, 100) <= hit_rate:
            hit = True
            damage = attacker.atk - int(random.uniform(0.75, 1.1) * 0.5 * target.defp)
            block_chance = ( target.defp * 2 ) / 100
            deflect_chance = ( target.defp ) / 100
            block = random.random() <= block_chance
            deflect = random.random() <= deflect_chance
            adjusted_defp = round(target.defp * random.uniform(0.7, 1.3))
            if deflect:
                damage = int(damage * 0.25)
            elif block:
                damage = int(damage * 0.5)
            damage -= int(adjusted_defp * 0.5)
            if random.randint(1, 100) <= 2.5:
                damage = int(damage * random.uniform(1.5, 3))
            damage = int(max(damage, random.randint(1, 2)))
            target.hp -= damage
            return hit, damage
        else:
            hit = False
            # Attack missed
            return hit, damage
    
    def step(self, action):
        # Player attacks an enemy
        hit, damage = self.attack(self.player, action)

        # Check if the enemy defeated by the player
        if self.enemies[action].hp <= 0:
            self.enemies.remove(self.enemies[action])
            reward = 100  # Large reward for defeating an enemy
        elif hit:
            reward = 10  # Reward for a regular hit
        else:
            reward = 0  # No reward for a miss

        # Ally attacks an enemy
        if self.ally and self.enemies:
            # The ally targets the enemy with the lowest HP
            target_index = min(range(len(self.enemies)), key=lambda index: self.enemies[index].hp)
            hit, damage = self.attack(self.ally, target_index)
            
            # Check if the enemy defeated by the ally
            if self.enemies[target_index].hp <= 0:
                self.enemies.remove(self.enemies[target_index])
                reward += 100  # Large reward for defeating an enemy

        # Enemies attack
        if self.enemies:
            for enemy in self.enemies:
                # The enemy targets the character with the lowest HP (either the player or the ally)
                if self.ally and self.ally.hp < self.player.hp:
                    target = self.ally
                else:
                    target = self.player

                # Store player's HP before the attack to calculate damage taken
                hp_before = target.hp
                hit, damage = self.attack(enemy, target)

                # Calculate damage taken and update the reward
                damage_taken = hp_before - target.hp
                reward -= damage_taken  # Penalty for taking damage

        # Check if all enemies have fallen
        if not self.enemies:
            done = True
        else:
            done = False

        # Get the new game state
        state = self._get_state()

        return state, reward, done

    def _get_state(self):
        characters = [self.player] + [self.ally] + self.enemies
        state = [[character.name, 
                character.level, 
                character.hp, 
                character.atk, 
                character.defp, 
                character.acc, 
                character.ev, 
                character.weapon_tier, 
                character.armor_tier] for character in characters]
        return state
    
    def reset(self):
        self.player.level = 1
        self.player.hp = 100
        self.player.atk = 10
        self.player.defp = 10
        self.player.acc = 10
        self.player.ev = 10
        self.player.weapon_tier = 0
        self.player.armor_tier = 0
        self.enemies = []
        self.generate_ally()
        self.generate_enemies()        
        self.round_number = 0
        return self._get_state()

    def generate_ally(self):
        ally = Character("Ally", level=1, hp=1, atk=1, defp=1, acc=1, ev=1, weapon_tier=0, armor_tier=0, is_enemy=False)
        ally.level = random.randint(min(1, self.player.level - 5), self.player.level + 5)
        ally.hp = random.randint(50, 150)
        ally.atk = random.randint(5, 15)
        ally.defp = random.randint(5, 15)
        ally.acc = random.randint(20, 50)
        ally.ev = random.randint(5, 40)
        ally.weapon_tier = random.randint(0,2)
        ally.armor_tier = random.randint(0,2)
        self.player.ally = ally

    def generate_enemies(self):
        for i in range(random.randint(1,3)):
            enemy = Character(f"Enemy{i}", level=1, hp=1, atk=1, defp=1, acc=1, ev=1, weapon_tier=0, armor_tier=0, is_enemy=True)
            enemy.level = random.randint(min(1, self.player.level - 5), self.player.level + 5)
            enemy.hp = random.randint(50, 150)
            enemy.atk = random.randint(5, 15)
            enemy.defp = random.randint(5, 15)
            enemy.acc = random.randint(20, 50)
            enemy.ev = random.randint(5, 40)
            enemy.weapon_tier = random.randint(0,2)
            enemy.armor_tier = random.randint(0,2)
            self.enemies.append(enemy)

