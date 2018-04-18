import argparse
import pickle
from visualization.playground import Playground
from visualization.framework import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evo visualization run')
    parser.add_argument('input_dir', type=str,
                        help='input directory to get data from')
    parser.add_argument('iteration_it', type=str,
                        help='iteration from which we want to get data')
    args = parser.parse_args()

    with open(args.input_dir + '/' + 'iteration_' + args.iteration_it, 'rb') as handle:
        dict = pickle.load(handle)

    with open(args.input_dir + '/terrain', 'rb') as handle:
        terrain = pickle.load(handle)

    main(Playground, dict["best"], terrain)
