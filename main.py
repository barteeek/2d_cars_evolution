from evo.simulator import Simulator
from evo.EvolutionaryAlgorithms import SGA, ES
from evo.world_entities import CarBuilder
import os
import argparse
import pickle
import sys

if __name__ == "__main__":
    sys.path.append('evo')
    parser = argparse.ArgumentParser(description='Evo run')
    parser.add_argument('output_dir', type=str,
                        help='output directory to save iterations')
    parser.add_argument('terrain_file', type=str,
                        help='file with terrain definition')

    args = parser.parse_args()
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        print ("output dir exists")
        # exit(-1)

    with open(args.terrain_file, 'rb') as handle:
        terrain = pickle.load(handle)

    #alg = SGA(output_dir=output_dir, population_size=500, number_of_offspring=500, mutation_probability=0.2, number_of_iterations=200)
    alg = ES(sigma=1., tau=1., tau0=1., output_dir=output_dir, population_size=100, number_of_offspring=100, number_of_iterations=200)

    #alg = SGA(output_dir=output_dir, population_size=100, number_of_offspring=100, mutation_probability=0.4, number_of_iterations=200, with_permutations = True)
    simulator = Simulator(output_dir, terrain, 8, 3, 200, 30, 1)
    alg.make_evolution(simulator)
