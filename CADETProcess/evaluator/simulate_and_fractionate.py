from CADETProcess import CADETProcessError
from CADETProcess.dataStructure import StructMeta

from CADETProcess.processModel import Process
from CADETProcess.simulator import SimulatorBase
from CADETProcess.fractionation import FractionationOptimizer

from CADETProcess.performance import get_bad_performance


class SimulateAndFractionate(metaclass=StructMeta):
    """Wrapper for sequential simulation and fractionation of processes.

    Attributes
    ----------
    process_solver: SolverBase
        Solver for simulating the process.
        Can include stationarity evaluator.
    fractionation_optimizer: FractionationOptimizer
        Optimizer for fractionating and evaluating process solution.

    See Also
    --------
    Process
    simulation.SolverBase
    fractionation.FractionationOptimizer
    """

    def __init__(self, process_simulator, fractionation_optimizer):
        self.process_simulator = process_simulator
        self.fractionation_optimizer = fractionation_optimizer

    @property
    def process_simulator(self):
        return self._process_simulator

    @process_simulator.setter
    def process_simulator(self, process_simulator):
        if not isinstance(process_simulator, SimulatorBase):
            raise TypeError('Expected SimulatorBase')
        self._process_solver = process_simulator

    @property
    def fractionation_optimizer(self):
        return self._fractionation_optimizer

    @fractionation_optimizer.setter
    def fractionation_optimizer(self, fractionation_optimizer):
        if not isinstance(fractionation_optimizer, FractionationOptimizer):
            raise TypeError('Expected FractionationOptimizer')
        self._fractionation_optimizer = fractionation_optimizer

    def simulate_and_fractionate(self, process):
        """Runs the process simulation and calls the fractionation optimizer.

        Parameters
        -----------
        process : Process
            Process to be simulated

        Returns
        -------
        frac : Fractionator
            Fractionator object with optimized fractionation times.
        """
        simulation_results = self.process_simulator.simulate(process)
        frac = self.fractionation_optimizer.optimize_fractionation(
            simulation_results
        )
        return frac

    def evaluate(self, process):
        """Runs the process simulation and calls the fractionation optimizer.

        Parameters
        ----------
        process : Process
            Process to be simulated

        Raises
        ------
        TypeError
            If process is not an instance of Process

        Returns
        -------
        performance : Performance
            Process performance after fractionation with obj_fun and nonlin_fun
        """
        if not isinstance(process, Process):
            raise TypeError('Expected Process')

        try:
            frac = self.simulate_and_fractionate(process)
            performance = frac.performance
        except CADETProcessError:
            n_comp = process.flow_sheet.n_comp
            performance = get_bad_performance(n_comp)

        return performance
