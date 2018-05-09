import os
import argparse
import pickle
import sys
from evo.simulator import Simulator
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluates on benchmarks')
    parser.add_argument('benchmarks_dir', type=str,
                        help='directory with benchmarks')
    parser.add_argument('car_file', type=str,
                        help='file with car definition')

    args = parser.parse_args()
    sys.path.append('evo')

    with open(args.car_file, 'rb') as handle:
        dict = pickle.load(handle)

    row_format = "{:<25}"*4

    filenames = os.listdir(args.benchmarks_dir)
    scores = np.zeros(len(filenames))

    for i, filename in enumerate(filenames):
        with open(args.benchmarks_dir + '/' + filename, 'rb') as handle:
            terrain = pickle.load(handle)
            simulator = Simulator('/tmp', terrain, 8, 3, 200, 30, 1)
            score, position = simulator.get_scores([dict["best"]])
            scores[i] = score
            to_print = [filename,
                        "score: " + str(score[0]),
                        "route_end: " + str(terrain.route_end),
                        "position: " + str(position[0])]
            print(row_format.format(*to_print))
    print ("SCORES_MEAN = ", np.mean(scores))
    print ("SCORES_STD = ", np.std(scores))
