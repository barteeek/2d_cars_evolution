from evo.simulator import Simulator
from evo.EvolutionaryAlgorithms import SGA
import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evo run')
    parser.add_argument('output_dir', type=str,
                        help='output directory to save iterations')

    args = parser.parse_args()
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        print ("output dir exists")
        exit(-1)

    alg = SGA(output_dir, population_size=200, number_of_offspring=200, mutation_probability=0.4, number_of_iterations=200)
    simulator = Simulator(output_dir, 8, 3, 200, 30, 1)
    alg.make_evolution(simulator)
