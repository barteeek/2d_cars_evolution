import argparse
import math
import numpy as np
import os
import pickle

from world_entities import Terrain


class TerrainGenerator:
    @staticmethod
    def generateZigZag(length, maxHeight, friction = 30):
        heights = np.zeros(length)
        for i in range(length):
            if i % 2 == 0:
                heights[i] = maxHeight
            else:
                heights[i] = -maxHeight
        return Terrain(heights, friction)

    @staticmethod
    def generateRandom(length, maxHeight, friction = 30):
        heights = np.random.rand(length)
        return Terrain(heights, friction)

    @staticmethod
    def generateIncreasinglyDifficult(length, maxHeight, friction = 30):
        heights = np.zeros(length)
        for i in range(length):
            heights[i] = np.random.random() * (float(i)/float(length)) * maxHeight
        return Terrain(heights, friction)

    @staticmethod
    def generateGentleHills(length, maxHeight, friction = 30):
        heights = np.zeros(length)
        for i in range(length):
            heights[i] = math.cos(1.5*i)*maxHeight - maxHeight
        return Terrain(heights, friction)
    
    @staticmethod
    def generateStraightLine(length, maxHeight, friction = 30):
        heights = np.zeros(length)
        return Terrain(heights, friction)    
    

def put_to_file(terrain, directory, name):
    with open(directory + "/" + name, 'wb') as handle:
        pickle.dump(terrain, handle)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evo run')
    parser.add_argument('output_dir', type=str,
                        help='output directory to save generated terrains')
    parser.add_argument('number_of_terrains', type=int,
                        help='number of terrains to generate (for all types)')
    parser.add_argument('length', type=int,
                        help='terrain length')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    else:
        print ("output dir exists")
        exit(-1)

    
    generated_terrains = []

    for i in range(1):
        maxHeight = 0.175
        generated_terrains += \
            [(TerrainGenerator.generateGentleHills(args.length, maxHeight), "terrainGentleZigZag_" + "{:.2f}".format(maxHeight))]
    """
    for i in range(args.number_of_terrains):
        maxHeight = math.sqrt(i)
        generated_terrains += \
            [(TerrainGenerator.generateRandom(args.length, maxHeight), "terrainRandom_" + "{:.2f}".format(maxHeight))]
    
    for i in range(args.number_of_terrains):
        maxHeight = math.sqrt(i)
        generated_terrains += \
            [(TerrainGenerator.generateIncreasinglyDifficult(args.length, maxHeight), "terrainIncDifficult_" + "{:.2f}".format(maxHeight))]
    
    for i in range(args.number_of_terrains):
        maxHeight = math.sqrt(i)
        generated_terrains += \
            [(TerrainGenerator.generateGentleHills(args.length, maxHeight), "terrainGentleHills_" + "{:.2f}".format(maxHeight))]
    """
    for terrain, name in generated_terrains:
        put_to_file(terrain, args.output_dir, name)
        