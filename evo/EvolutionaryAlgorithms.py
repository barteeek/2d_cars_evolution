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

class EvoAlgBase:
    def __init__(self, output_dir, init_individual_fun, population_size=500, chromosome_length=21, number_of_offspring=500, \
        number_of_iterations=50):
        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.number_of_offspring = number_of_offspring
        self.number_of_iterations = number_of_iterations
        self.init_individual_fun = init_individual_fun
        self.dump_dir = output_dir

    def make_evolution(self, simulator):
        self.simulator = simulator
        self.best_objective_value = -np.Inf
        self.counter = 0
        best_individual = None

        # generating an initial population
        population = []
        for i in range(self.population_size):
            population += [self.init_individual_fun(self.simulator)]

        # evaluating the objective function on the current population
        objective_values, positions, iterations = self.simulator.get_scores(population)

        self.costs = np.zeros(self.number_of_iterations)

        for t in range(self.number_of_iterations):
            population, objective_values, positions, iterations, best_individual = \
                self.make_step(population=population, objective_values=objective_values, positions=positions,\
                               iterations=iterations, best_car=best_individual)
            chromosomes = np.zeros((self.population_size, len(population[0].chromosome)))
            for i in range(self.population_size):
                chromosomes[i] = population[i].chromosome
            with open(self.dump_dir + "/iteration_" + str(t), 'wb') as handle:
                pickle.dump({"best":best_individual, "population":population}, handle)

            I = np.argsort(objective_values)
            min_index = I[0]
            max_index = I[-1]

            with open(self.dump_dir + "/logs", "a") as file:
                file.write("Iteration: " + str(t) + '\n' +
                           " min_score: " + str(np.min(objective_values)) +
                           " max_score: " + str(np.max(objective_values)) +
                           " std_score: " + str(np.std(objective_values)) +
                           " std_chromosome: " + str(np.std(chromosomes, axis=0)) +
                           " mean_score: " + str(np.mean(objective_values)) + '\n' +
                           " min_pos: " + str(positions[min_index]) +
                           " max_pos: " + str(positions[max_index]) +
                           " mean_pos: " + str(np.mean(positions)) + "\n" +
                           " min_iters: " + str(iterations[min_index]) +
                           " max_iters: " + str(iterations[max_index]) +
                           " mean_iters: " + str(np.mean(iterations)) + "\n" +
                           " route_end: " + str(simulator.get_end_of_route()) + '\n')
            print ("Iteration: " + str(t) + '\n' +
                           " min_score: " + str(np.min(objective_values)) +
                           " max_score: " + str(np.max(objective_values)) +
                           " std_score: " + str(np.std(objective_values)) +
                           " std_chromosome: " + str(np.std(chromosomes, axis=0)) +
                           " mean_score: " + str(np.mean(objective_values)) + '\n' +
                           " min_pos: " + str(positions[min_index]) +
                           " max_pos: " + str(positions[max_index]) +
                           " mean_pos: " + str(np.mean(positions)) + "\n" +
                           " min_iters: " + str(iterations[min_index]) +
                           " max_iters: " + str(iterations[max_index]) +
                           " mean_iters: " + str(np.mean(iterations)) + "\n" +
                           " route_end: " + str(simulator.get_end_of_route()) + '\n')

        best_score, _, _ = self.simulator.get_scores([best_individual])
        return best_individual, best_score

    def make_step(self, **kwargs):
        pass


class SGA(EvoAlgBase):
    def __init__(self, crossover_fun=simple_crossover, crossover_probability=0.95, mutation_probability=0.1, **kwargs):
        super(SGA, self).__init__(init_individual_fun=self.init_individual, **kwargs)
        self.crossover_probability=crossover_probability
        self.mutation_probability = mutation_probability
        self.crossover_fun = crossover_fun

    def init_individual(self, simulator):
        return simulator.get_random_individual()


    def make_step(self, population, objective_values, positions, iterations, \
                  best_car):
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
                    if j in [13, 15]:
                        chromosome[j] = np.random.randint(0, 6)
                    else:
                        chromosome[j] += np.random.random() * 2. - 1.
                        chromosome[j] = np.clip(chromosome[j], 0.05, np.inf)
            children_population[i].construct_from_chromosome(chromosome)

        # evaluating the objective function on the children population
        children_objective_values, children_positions, children_iterations = self.simulator.get_scores(children_population)

        # replacing the current population by (Mu + Lambda) Replacement
        objective_values = np.hstack([objective_values, children_objective_values])
        positions = np.hstack([positions, children_positions])
        iterations = np.hstack([iterations, children_iterations])
        population = np.hstack([population, children_population])

        I = np.argsort(objective_values)
        population = population[I[-self.population_size:]]
        z = objective_values[I[-self.population_size:]]
        objective_values = objective_values[I[-self.population_size:]]
        positions = positions[I[-self.population_size:]]
        iterations = iterations[I[-self.population_size:]]
        
        # self.costs[t] = objective_values[0]
        
        # recording some statistics
        if self.best_objective_value < objective_values[-1]:
            self.best_objective_value = objective_values[-1]
            best_car = population[-1]

        return population, objective_values, positions, iterations, best_car
