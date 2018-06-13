import argparse
import pickle
from visualization.playground import Playground
from visualization.framework import main
from evo.world_entities import Terrain
import numpy as np
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evo visualization run')
    parser.add_argument('route_file', type=str,
                        help='file with route definition')
    parser.add_argument('car_file', type=str,
                        help='file with car definition')
    args = parser.parse_args()

    with open(args.car_file, 'rb') as handle:
        dict = pickle.load(handle)
        
    # dict["best"].chromosome[16] /= 1.4
    # dict["best"].chromosome[14] *= 2.

    sys.path.append('evo')

    with open(args.route_file, 'rb') as handle:
        terrain = pickle.load(handle)

    dict["best"].chromosome = [-1.00086315,  0.212184,    1.10060529 , 1.43885187 , 0.71241061  ,0.73984752,
 -1.06452472 , 1.44566454 , 1.19407973 , 0.69498135 , 1.39545404  ,1.28407526,
  0.21789606 , 2.52724146,  0.35820385,  3.55290226 , 0.66961734]
    print ("BEST " , len(dict["best"].chromosome))
    main(Playground, dict["best"], terrain)
