import argparse
import pickle
from visualization.playground import Playground
from visualization.framework import main
from evo.world_entities import Terrain
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evo visualization run')
    parser.add_argument('route_file', type=str,
                        help='file with route definition')
    parser.add_argument('car_file', type=str,
                        help='file with car definition')
    args = parser.parse_args()

    with open(args.car_file, 'rb') as handle:
        dict = pickle.load(handle)

    with open(args.route_file, 'rb') as handle:
        terrain = pickle.load(handle)

    main(Playground, dict["best"], terrain)
