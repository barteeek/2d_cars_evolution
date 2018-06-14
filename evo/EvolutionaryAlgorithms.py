from .world_entities import CarRepresentation

import numpy as np
import pickle

def PMX(ind1, ind2):
    a = np.random.choice(len(ind1), 2, False)
    i, j = a.min(), a.max()

    mapping1to2 = {}
    mapping2to1 = {}
    
    for index in range(i, j):
        x = ind1[index]
        y = ind2[index]
        mapping1to2[y] = x
        mapping2to1[x] = y
    
    kid1 = ind1.copy()
    kid2 = ind2.copy()
    
    kid1[i:j] = ind2[i:j]
    kid2[i:j] = ind1[i:j]
    
    for index in range(i):
        current = kid1[index]
        while current in mapping1to2:
            current = mapping1to2[current]
        kid1[index]  = current
        
        current = kid2[index]
        while current in mapping2to1:
            current = mapping2to1[current]
        kid2[index]  = current

    for index in range(j, len(ind1)):
        current = kid1[index]
        while current in mapping1to2:
            current = mapping1to2[current]
        kid1[index]  = current
        
        current = kid2[index]
        while current in mapping2to1:
            current = mapping2to1[current]
        kid2[index]  = current

    # print (kid1, kid2)
    # assert len(set(kid1)) == len(set(kid2)) == len(ind1)
    return kid1, kid2
    # return ind1, ind2

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


def simple_crossover_with_permutation(car1, car2):
    chromosome1 = car1.get_chromosome()
    chromosome2 = car2.get_chromosome()
    permutation1 = car1.get_permutation()
    permutation2 = car2.get_permutation()
    
    chromosome1 = car1.apply_permutation()
    chromosome2 = car2.apply_permutation(car1.get_permutation())
    
    to_cut = np.random.choice(len(chromosome1), 2, False)
    to_cut_left, to_cut_right = to_cut.min(), to_cut.max()
    chromosome1[to_cut_left:to_cut_right], chromosome2[to_cut_left:to_cut_right] = \
        chromosome2[to_cut_left:to_cut_right], chromosome1[to_cut_left:to_cut_right]

    kid1 = CarRepresentation()
    kid2 = CarRepresentation()

    kid1.construct_from_chromosome(chromosome1)
    kid2.construct_from_chromosome(chromosome2)
    kid1.set_permutation(permutation1)
    kid2.set_permutation(permutation1)

    kid_1 = [kid1, kid2][np.random.randint(0, 2)]
    kid_1.undo_permutation()

    chromosome1 = car1.apply_permutation(car2.get_permutation())
    chromosome2 = car2.apply_permutation()
    
    to_cut = np.random.choice(len(chromosome1), 2, False)
    to_cut_left, to_cut_right = to_cut.min(), to_cut.max()
    chromosome1[to_cut_left:to_cut_right], chromosome2[to_cut_left:to_cut_right] = \
        chromosome2[to_cut_left:to_cut_right], chromosome1[to_cut_left:to_cut_right]

    kid1 = CarRepresentation()
    kid2 = CarRepresentation()

    kid1.construct_from_chromosome(chromosome1)
    kid2.construct_from_chromosome(chromosome2)
    kid1.set_permutation(permutation2)
    kid2.set_permutation(permutation2)

    kid_2 = [kid1, kid2][np.random.randint(0, 2)]
    kid_2.undo_permutation()
    
    new_permutation1, new_permutation2 = PMX(permutation1, permutation2)
    
    kid_1.set_permutation(new_permutation1)
    kid_2.set_permutation(new_permutation2)

    return kid_1, kid_2


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

            pickleable_pop = []
            for ind in population:
                pickleable_pop += [ind.get_car()]

            with open(self.dump_dir + "/iteration_" + str(t), 'wb') as handle:
                pickle.dump({"best":best_individual, "population":pickleable_pop}, handle)

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
    def __init__(self, crossover_fun=simple_crossover_with_permutation, crossover_probability=0.95, mutation_probability=0.1, with_permutations = False, **kwargs):
        super(SGA, self).__init__(init_individual_fun=self.init_individual, **kwargs)
        self.crossover_probability=crossover_probability
        self.mutation_probability = mutation_probability
        self.crossover_fun = crossover_fun
        self.with_permutations = with_permutations

    def init_individual(self, simulator):
        return simulator.get_random_individual(with_permutations=self.with_permutations)

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
        children_population = [None] * self.number_of_offspring
        for i in range(int(self.number_of_offspring/2)):
            first_parent = population[parent_indices[2*i]].make_copy()
            second_parent = population[parent_indices[2*i+1]].make_copy()
            
            if np.random.random() < self.crossover_probability:
                if self.with_permutations == True:
                    children_population[2*i], children_population[2*i+1] = \
                        simple_crossover_with_permutation(first_parent, second_parent)
                else :
                    children_population[2*i], children_population[2*i+1] = \
                        simple_crossover(first_parent, second_parent)
            else:
                children_population[2*i], children_population[2*i+1] = first_parent, second_parent

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
        # normalize kids...
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

class ES(EvoAlgBase):
    def __init__(self, sigma, tau, tau0, **kwargs):
        super(ES, self).__init__(init_individual_fun=self.init_individual, **kwargs)

        self.sigma = sigma
        self.tau = tau
        self.tau_0 = tau0

    class Individual:
        def __init__(self, simulator, sigma):
            self.car = simulator.get_random_individual()
            self.sigmas = sigma * np.ones(len(self.car.chromosome))
            self.update_chrom()

        def put_to_world(self, *args, **kwargs):
            return self.car.put_to_world(*args, **kwargs)

        def chrom_len(self):
            return self.sigmas.shape[0]

        def update_chrom(self):
            self.chromosome = np.concatenate([self.car.chromosome, self.sigmas])

        def update_from_chromosome(self):
            self.car.chromosome = self.chromosome[:self.sigmas.shape[0]]
            self.sigmas = self.chromosome[self.sigmas.shape[0]:]
            self.car.normalize()

        def get_car(self):
            return self.car

    def init_individual(self, simulator):
        return self.Individual(simulator, self.sigma)


    def make_step(self, population, objective_values, positions, iterations, \
                  best_car):
        population_size = len(population)
        chromosome_length = population[0].chrom_len()

        for t in range(self.number_of_iterations):
            # selecting the parent indices by the roulette wheel method
            fitness_values = objective_values - objective_values.min()
            if fitness_values.sum() > 0:
                fitness_values = fitness_values / fitness_values.sum()
            else:
                fitness_values = 1.0 / population_size * np.ones(
                    population_size)
            parent_indices = np.random.choice(population_size, (
            self.number_of_offspring, 2), True, fitness_values).astype(np.int64)

            # creating the children population by Global Intermediere Recombination
            children_population = [0] * self.number_of_offspring
            children_population_solutions = np.zeros(
                (self.number_of_offspring, chromosome_length))
            children_population_sigmas = np.zeros(
                (self.number_of_offspring, chromosome_length))
            for i in range(self.number_of_offspring):
                p1 = population[parent_indices[i, 0]]
                p2 = population[parent_indices[i, 1]]
                child = self.init_individual(self.simulator)
                child.chromosome = (p1.chromosome + p2.chromosome) / 2.

                child.chromosome[chromosome_length:] *= np.exp(
                    self.tau * np.random.randn(chromosome_length) +
                    self.tau_0 * np.random.randn(1))
                child.chromosome[:chromosome_length] += \
                    child.chromosome[chromosome_length:] * np.random.randn(chromosome_length)

                child.update_from_chromosome()
                children_population[i] = child


            # evaluating the objective function on the children population
            children_objective_values, children_positions, children_iterations = \
                self.simulator.get_scores(children_population)

            # replacing the current population by (Mu + Lambda) Replacement
            objective_values = np.hstack(
                [objective_values, children_objective_values])
            positions = np.hstack([positions, children_positions])
            iterations = np.hstack([iterations, children_iterations])
            population = np.hstack([population, children_population])

            I = np.argsort(objective_values)
            population = population[I[-self.population_size:]]
            objective_values = objective_values[I[-self.population_size:]]
            positions = positions[I[-self.population_size:]]
            iterations = iterations[I[-self.population_size:]]

            # recording some statistics
            if self.best_objective_value < objective_values[-1]:
                self.best_objective_value = objective_values[-1]
                best_car = population[-1].car

            return population, objective_values, positions, iterations, best_car
