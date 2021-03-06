import pickle
import time
from pathlib import Path
from typing import Dict, Tuple, List

import numpy as np
import datetime
from aco_tsp_reworked import Config, run_aco, Solution

N_AVERAGE = 3


def main():
    candidate_list_config = Config()
    candidate_list_config.FILE_NAME = "E-n76-k10.txt"

    candidate_list_config.ANT_CAPACITY = 140
    candidate_list_config.USE_2_OPT_STRATEGY = False
    candidate_list_config.USE_CANDIDATE_LIST_STRATEGY = True

    configs: Dict[str, Config] = {
        "candidate_list": candidate_list_config,
    }

    n_ants = [20]
    alphas = [2]
    rhos = [0.25]

    timestamp = int(time.time())
    log_dir = Path(__file__).resolve().parent / f"results_{timestamp}"
    log_dir.mkdir()

    results: Dict[Tuple, Tuple[np.ndarray, np.ndarray, datetime.timedelta]] = {}
    for name, config in configs.items():
        print(f"Testing config: {name}")
        for ants in n_ants:
            print(f"Ants: {ants}")
            config.NUM_ANTS = ants
            for alpha in alphas:
                print(f"Alpha: {alpha}")
                config.ALPHA = alpha
                for rho in rhos:
                    experiment_name = f"{name.upper()}: ants: {ants}, alpha: {alpha}, rho: {rho}"
                    print(experiment_name)
                    config.RHO = rho

                    start = datetime.datetime.now()
                    curr_results = []
                    for _ in range(N_AVERAGE):
                        try:
                            result = run_aco(config, False)
                            curr_results.append(result)
                        except Exception as e:
                            print(e)
                    best, history = average_n_results(curr_results)
                    time_difference = (datetime.datetime.now() - start) / N_AVERAGE
                    results[name, ants, alpha, rho] = (best, history, time_difference)
                    with open(log_dir / "log.txt", 'a') as f:
                        f.write(f"{experiment_name} = {best}\n")
                    with open(log_dir / "save.pkl", 'wb') as f:
                        pickle.dump(results, f)


def average_n_results(results: List[Tuple[Solution, List[Solution]]]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Average n results. Drop paths.
    :param results:
    :return: Tuple best score and history of scores
    """
    if not results:
        return np.inf, np.array([])
    best = []
    history = [[] for _ in range(len(results[0][1]))]
    for i in results:
        best.append(i[0].cost)
        for idx, elem in enumerate(i[1]):
            history[idx].append(elem.cost)
    return np.mean(best), np.mean(history, 1)


if __name__ == '__main__':
    main()
