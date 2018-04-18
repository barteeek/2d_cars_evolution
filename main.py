from evo.simulator import Simulator
from evo.EvolutionaryAlgorithms import SGA

if __name__ == "__main__":
    alg = SGA()
    simulator = Simulator(8, 3, 100, 1.5, 1)
    alg.make_evolution(simulator)
