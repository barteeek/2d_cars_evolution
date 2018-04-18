from evo.simulator import Simulator
from evo.EvolutionaryAlgorithms import SGA

if __name__ == "__main__":
    alg = SGA()
    simulator = Simulator()
    alg.make_evolution(simulator)
