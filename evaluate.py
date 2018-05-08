import os
import argparse
import pickle
from evo.simulator import Simulator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluates on benchmarks')
    parser.add_argument('benchmarks_dir', type=str,
                        help='directory with benchmarks')
    parser.add_argument('car_file', type=str,
                        help='file with car definition')

    args = parser.parse_args()
    simulator = Simulator('/tmp', 8, 3, 200, 30, 1)
    with open(args.car_file, 'rb') as handle:
        dict = pickle.load(handle)

    for filename in os.listdir(args.benchmarks_dir):
        with open(args.benchmarks_dir + '/' + filename, 'rb') as handle:
            terrain = pickle.load(handle)
            score = simulator.get_scores([dict["best"]])

            print(filename + "-- score: " + str(score[0]) + \
                  " route_end: " + terrain.route_end)