"""
Cart-pole balancing with independent discretization
"""
import sys
## HACK
sys.path.append("/home/jarvis/work/clipper/models/rl/")

from ClothCutter import ClothCutter
from rlpy.Agents import SARSA, Q_Learning
from Representations import *
from rlpy.Policies import eGreedy, GibbsPolicy
from rlpy.Experiments import Experiment
import numpy as np

# param_space = {
#     "num_rbfs": hp.qloguniform("num_rbfs", np.log(1e1), np.log(1e4), 1),
#     'resolution': hp.quniform("resolution", 3, 30, 1),
#     'lambda_': hp.uniform("lambda_", 0., 1.),
#     'boyan_N0': hp.loguniform("boyan_N0", np.log(1e1), np.log(1e5)),
#     'initial_learn_rate': hp.loguniform("initial_learn_rate", np.log(5e-2), np.log(1))}


def make_experiment(
        exp_id=1, path="./Results/Temp/{domain}/{agent}/{representation}/",
        boyan_N0=1,
        lambda_=0.3,
        initial_learn_rate=1.,
        resolution=15., num_rbfs=5000):
    opt = {}
    opt["path"] = path
    opt["exp_id"] = exp_id
    opt["max_steps"] = 5000
    opt["num_policy_checks"] = 1
    opt["checks_per_policy"] = 1

    domain = ClothCutter()
    opt["domain"] = domain
    representation = ModifiedRBF(domain, num_rbfs=int(num_rbfs), 
                         resolution_max=resolution, resolution_min=resolution,
                         const_feature=False, normalize=True, seed=exp_id)
    policy = GibbsPolicy(representation)
    opt["agent"] = SARSA(
        policy, representation, discount_factor=domain.discount_factor,
        lambda_=lambda_, initial_learn_rate=initial_learn_rate,
        learn_rate_decay_mode="const", boyan_N0=boyan_N0)
    experiment = Experiment(**opt)
    return experiment

if __name__ == '__main__':
    # from rlpy.Tools.run import run_profiled
    # run_profiled(make_experiment)
    experiment = make_experiment(2)
    experiment.run()
    rep = experiment.agent.representation
    rep.dump_to_directory("./Results/Temp")
    # experiment.plot()
    experiment.save()
