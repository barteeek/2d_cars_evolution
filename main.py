from evo.simulator import Simulator
from evo.EvolutionaryAlgorithms import SGA
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
        exit(-1)

    with open(args.terrain_file, 'rb') as handle:
        terrain = pickle.load(handle)

    alg = SGA(output_dir, population_size=1000, number_of_offspring=1000, mutation_probability=0.4, number_of_iterations=200)
    simulator = Simulator(output_dir, terrain, 8, 3, 200, 30, 1)
    alg.make_evolution(simulator)
