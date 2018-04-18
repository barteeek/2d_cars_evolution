from .world_entities import CarRepresentation

import numpy as np
import pickle

def simple_crossover(car1, car2):
    chromosome1 = car1.get_chromosome()
    chromosome2 = car2.get_chromosome()
    to_cut = np.random.choice(len(chromosome1), 2, False)
    to_cut_left, to_cut_right = to_cut.min(), to_cut.max()
    chromosome1[to_cut_left:to_cut_right], chromosome2[to_cut_left:to_cut_right] = \
        chromosome2[to_cut_left:to_cut_right], chromosome1[to_cut_left:to_cut_right]

    kid1 = CarRepresentation()
    kid2 = CarRepresentation()

    kid1.construct_from_chromosome(chromosome1)
    kid2.construct_from_chromosome(chromosome2)

    return kid1, kid2


class SGA:
    def __init__(self, dump_dir, population_size=500, chromosome_length=21, number_of_offspring=500, \
        crossover_probability=0.95, mutation_probability=0.1, number_of_iterations=50, \
        mutation_fun=lambda *args: args, crossover_fun=simple_crossover):
        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.number_of_offspring = number_of_offspring
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.number_of_iterations = number_of_iterations
        self.mutation_fun = mutation_fun
        self.crossover_fun = crossover_fun
        self.dump_dir = dump_dir
    
    def make_evolution(self, simulator):
        self.simulator = simulator
        self.best_objective_value = -np.Inf
        self.counter = 0
        best_individual = None

        # generating an initial population
        population = []
        for i in range(self.population_size):
            population += [simulator.get_random_individual()]

        # evaluating the objective function on the current population
        objective_values = self.simulator.get_scores(population)

        self.costs = np.zeros(self.number_of_iterations)

        for t in range(self.number_of_iterations):
            population, objective_values, best_individual = \
                self.make_step(population, objective_values, best_individual)
            with open(self.dump_dir + "/iteration_" + str(t), 'wb') as handle:
                pickle.dump({"best":best_individual, "population":population}, handle)
            with open(self.dump_dir + "/logs", "a") as file:
                file.write("Iteration: " + str(t) +
                           " min: " + str(np.min(objective_values)) +
                           " max: " + str(np.max(objective_values)) +
                           " mean: " + str(np.mean(objective_values)) + '\n')
            print ("Iteration: " + str(t) +
                       " min: " + str(np.min(objective_values)) +
                       " max: " + str(np.max(objective_values)) +
                       " mean: " + str(np.mean(objective_values)))

        best_score = self.simulator.get_scores([best_individual])
        return best_individual, best_score
    
    def make_step(self, population, objective_values, best_car):
        print ("in make_step ", self.counter)
        self.counter += 1
        # selecting the parent indices by the roulette wheel method
        fitness_values = objective_values - objective_values.min()
        if fitness_values.sum() > 0:
            fitness_values = fitness_values / fitness_values.sum()
        else:
            fitness_values = np.ones(self.population_size) / self.population_size
        parent_indices = np.random.choice(self.population_size, self.number_of_offspring, True,
                                          fitness_values).astype(np.int64)


        # creating the children population
        children_population = [None]*self.number_of_offspring
        for i in range(int(self.number_of_offspring/2)):
            if np.random.random() < self.crossover_probability:
                children_population[2*i], children_population[2*i+1] = \
                   self.crossover_fun(population[parent_indices[2*i]].make_copy(), \
                       population[parent_indices[2*i+1]].make_copy())
            else:
                children_population[2*i], children_population[2*i+1] = population[parent_indices[2*i]].make_copy(), population[parent_indices[2*i+1]].make_copy()
        if np.mod(self.number_of_offspring, 2) == 1:
            children_population[-1] = population[parent_indices[-1]]

        # mutating the children population
        for i in range(self.number_of_offspring):
            chromosome = children_population[i].get_chromosome()
            for j in range(chromosome.shape[0]):
                if np.random.random() < self.mutation_probability:
                    chromosome[j] = np.random.random()
            children_population[i].construct_from_chromosome(chromosome)

        # evaluating the objective function on the children population
        children_objective_values = self.simulator.get_scores(children_population)

        # replacing the current population by (Mu + Lambda) Replacement
        objective_values = np.hstack([objective_values, children_objective_values])
        population = np.hstack([population, children_population])

        I = np.argsort(objective_values)
        population = population[I[-self.population_size:]]
        objective_values = objective_values[I[-self.population_size:]]
        
        # self.costs[t] = objective_values[0]
        
        # recording some statistics
        if self.best_objective_value < objective_values[0]:
            self.best_objective_value = objective_values[0]
            best_car = population[-1]
        
        return population, objective_values, best_car
