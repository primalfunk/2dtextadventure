from equipment_balancing import Character, Battle, Weapon, Armor, Ally
import random
import numpy as np
from deap import base, creator, tools, algorithms

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", dict, fitness=creator.FitnessMax)
toolbox = base.Toolbox()
toolbox.register("attr_hp", random.randint, 50, 150)
toolbox.register("attr_other", random.randint, 5, 65)
toolbox.register("individual", init_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def init_individual():
    individual = creator.Individual()
    # Initialize the attributes
    individual["attrs"] = [toolbox.attr_hp(), toolbox.attr_other(), toolbox.attr_other(), toolbox.attr_other(),
                           toolbox.attr_other(), toolbox.attr_other(), toolbox.attr_other(), toolbox.attr_other(),
                           toolbox.attr_other(), toolbox.attr_other(), toolbox.attr_other(), toolbox.attr_other(),
                           toolbox.attr_other(), toolbox.attr_other(), toolbox.attr_other(), toolbox.attr_other(),
                           toolbox.attr_hp(), toolbox.attr_other(), toolbox.attr_other(), toolbox.attr_other(),
                           toolbox.attr_other()]
    individual["avg_round_count"] = 0
    individual["round_count_penalty"] = 0
    return individual

# Modify your evaluation function to update the avg_round_count and round_count_penalty values
def eval_func(individual):
    score, avg_round_count, round_count_penalty = run_battle_simulation(individual["attrs"])
    individual["avg_round_count"] = avg_round_count
    individual["round_count_penalty"] = round_count_penalty
    return score,

# Genetic operations
toolbox.register("evaluate", eval_func)
toolbox.register("mate", tools.cxTwoPoint)  # two-point crossover
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)  # gaussian mutation
toolbox.register("select", tools.selTournament, tournsize=3)  # tournament selection

def run_battle_simulation(individual):
    player = Character(level=1, hp=individual[0], atk=individual[1], defp=individual[2], acc=individual[3], ev=individual[4], acc_gain=individual[5], 
                       ev_gain=individual[6], hp_gain=individual[7], atk_gain=individual[8], defp_gain=individual[9], cap=individual[10])
    player_weapon = Weapon(atk_boost=individual[11], acc_boost=individual[12])
    player_armor = Armor(defp_boost=individual[13], ev_boost=individual[14])
    ally = Ally(level=1, hp=individual[15], atk=individual[16], defp=individual[17], acc=individual[18], ev=individual[19])
    # Initialize a Battle with the generated player and the parameters
    battle = Battle(player, player_weapon, player_armor, ally )
    # Run the simulation and get the results
    results = battle.results
    round_4_win_rate = battle.round_wins[3] / battle.round_battles[3]
    avg_round_count = sum(battle.round_counts) / len(battle.round_counts)
    # check if average round count is within the desired range
    if avg_round_count < 10 or avg_round_count > 30:
        round_count_penalty = abs(avg_round_count - 20) / 20  # penalty based on distance from the center of the range
    else:
        round_count_penalty = 0
    # take into account both win rate and round count
    fitness = (abs(0.5 - round_4_win_rate) + round_count_penalty) / 2
    return fitness, avg_round_count, round_count_penalty

def main():
    pop = toolbox.population(n=100)  # initialize a population of 100 individuals
    hof = tools.HallOfFame(1)  # object that will keep track of the individual with the highest fitness
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)
    stats.register("std", np.std)
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=100, stats=stats, halloffame=hof, verbose=True)
    return pop, log, hof

if __name__ == "__main__":
    pop, log, hof = main()
    print("Best individual: ")
    print(f"hp: {hof[0]['attrs'][0]}")
    print(f"atk: {hof[0]['attrs'][1]}")
    print(f"defp: {hof[0]['attrs'][2]}")
    print(f"acc: {hof[0]['attrs'][3]}")
    print(f"ev: {hof[0]['attrs'][4]}")
    print(f"acc_gain: {hof[0]['attrs'][5]}")
    print(f"ev_gain: {hof[0]['attrs'][6]}")
    print(f"hp_gain (initial): {hof[0]['attrs'][7]}")
    print(f"atk_gain (initial): {hof[0]['attrs'][8]}")
    print(f"defp_gain (initial): {hof[0]['attrs'][9]}")
    print(f"cap: {hof[0]['attrs'][10]}")
    print(f"weapon_atk_boost: {hof[0]['attrs'][11]}")
    print(f"weapon_acc_boost: {hof[0]['attrs'][12]}")
    print(f"armor_defp_boost: {hof[0]['attrs'][13]}")
    print(f"armor_ev_boost: {hof[0]['attrs'][14]}")
    print(f"ally hp: {hof[0]['attrs'][15]}")
    print(f"ally atk: {hof[0]['attrs'][16]}")
    print(f"ally defp: {hof[0]['attrs'][17]}")
    print(f"ally acc: {hof[0]['attrs'][18]}")
    print(f"ally ev: {hof[0]['attrs'][19]}")
    print(f"With fitness: {hof[0].fitness}")
    print(f"Best individual avg_round_count: {hof[0]['avg_round_count']}")
    print(f"Best individual round_count_penalty: {hof[0]['round_count_penalty']}")
    