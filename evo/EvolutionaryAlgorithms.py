from .car import CarRepresentation

import numpy as np

class SGA:
    def __init__(self, population_size=500, chromosome_length=21, number_of_offspring=500, \
        crossover_probability=0.95, mutation_probability=0.25, number_of_iterations=50, \
        mutation_fun=lambda *args: args, crossover_fun=lambda *args: args):
        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.number_of_offspring = number_of_offspring
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.number_of_iterations = number_of_iterations
        self.mutation_fun = mutation_fun
        self.crossover_fun = crossover_fun
    
    def make_evolution(self, simulator):
        self.simulator = simulator
        self.best_objective_value = np.Inf
        best_car = CarRepresentation()

        # generating an initial population
        population = []
        for i in range(self.population_size):
            current_car = CarRepresentation()
            population += [current_car]

        # evaluating the objective function on the current population
        objective_values = self.simulator.get_scores(population)
            
        self.costs = np.zeros(self.number_of_iterations)
        
        for t in range(self.number_of_iterations):
            population, objective_values, best_car = self.make_step(population, objective_values, best_car)
            
        best_score = self.simulator.get_scores([best_car])
        
        return self.best_car, best_score
    
    def make_step(self, population, objective_values, best_car):
        print ("in make_step")
        # selecting the parent indices by the roulette wheel method
        fitness_values = objective_values.max() - objective_values
        if fitness_values.sum() > 0:
            fitness_values = fitness_values / fitness_values.sum()
        else:
            fitness_values = np.ones(self.population_size) / self.population_size
        parent_indices = np.random.choice(self.population_size, self.number_of_offspring, True,
                                          fitness_values).astype(np.int64)

        # creating the children population
        children_population = [None]*self.population_size
        for i in range(int(self.number_of_offspring/2)):
            if np.random.random() < self.crossover_probability:
                children_population[2*i], children_population[2*i+1] = population[parent_indices[2*i]].make_copy(), population[parent_indices[2*i+1]].make_copy()
                # children_population[2*i, :], children_population[2*i+1, :] = \
                #    self.crossover_fun(population[parent_indices[2*i], :].copy(), \
                #        population[parent_indices[2*i+1], :].copy())
            else:
                children_population[2*i], children_population[2*i+1] = population[parent_indices[2*i]].make_copy(), population[parent_indices[2*i+1]].make_copy()
        if np.mod(self.number_of_offspring, 2) == 1:
            children_population[-1] = population[parent_indices[-1]]

        # mutating the children population
        for i in range(self.number_of_offspring):
            if np.random.random() < self.mutation_probability:
                children_population[i] = children_population[i]

        # evaluating the objective function on the children population
        children_objective_values = self.simulator.get_scores(children_population)

        # replacing the current population by (Mu + Lambda) Replacement
        objective_values = np.hstack([objective_values, children_objective_values])
        population = np.hstack([population, children_population])

        I = np.argsort(objective_values)
        population = population[I[:self.population_size]]
        objective_values = objective_values[I[:self.population_size]]
        
        # self.costs[t] = objective_values[0]
        
        # recording some statistics
        if self.best_objective_value > objective_values[0]:
            self.best_objective_value = objective_values[0]
            best_car= population[0]
        
        return population, objective_values, best_car
