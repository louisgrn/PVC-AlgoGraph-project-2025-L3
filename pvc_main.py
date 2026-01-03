import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
from multiprocessing import Pool
import time
import sys
import threading
import itertools
import pvc_lib as pvc

# Copier coller d'un site pour l'effet visuel dans la console

class Spinner:
    """Simple console spinner that runs on a separate thread."""
    def __init__(self, message="Execution en cours", delay=0.1):
        self._message = message
        self._delay = delay
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._spin)

    def _spin(self):
        for c in itertools.cycle("|/-\\"):
            if self._stop.is_set():
                break
            sys.stdout.write(f"\r{self._message} {c}")
            sys.stdout.flush()
            time.sleep(self._delay)
        sys.stdout.write('\r' + ' ' * (len(self._message) + 4) + '\r')
        sys.stdout.flush()

    def start(self):
        if not self._thread.is_alive():
            self._stop.clear()
            self._thread = threading.Thread(target=self._spin)
            self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join()


# def generer_points(n):
#   """
#   Génère n points avec des coordonnées tirées aléatoirement dans l'intervalle
#   [0, 1].

#   Args:
#       n (int): Le nombre de points à générer.

#   Returns:
#       list: Une liste de tuples (x, y).
#   """
#   # Matrice n x 2 avec des valeurs entre 0 et 1
#   points_array = rd.rand(n, 2)

#   # Liste de tuples (x, y)
#   points = [(float(p[0]), float(p[1])) for p in points_array]
#   return points

def exec_func(args):
    test_data, function = args
    times = []
    lengths = []
    
    for points in test_data:
        d = pvc.calculer_matrice_distances(points)
        
        t_start = time.time()
        _, l = function(d)
        t_end = time.time()
        
        times.append(t_end - t_start)
        lengths.append(l)
        
    return times, lengths


def exec_all_from_1_to_n_sommet(n, list_func):
    # Générer les mêmes points pour tous les algos pour une comparaison équitable
    test_data = [pvc.generer_points(i) for i in range(1, n+1)]
    
    args_list = [(test_data, f) for f in list_func]
    
    with Pool() as p:
        results = p.map(exec_func, args_list)
        
    return results

def exec_all(m, sommet_n, list_func):
    # Générer les mêmes points pour tous les algos pour une comparaison équitable
    test_data = [pvc.generer_points(sommet_n) for _ in range(1, m+1)]
    
    args_list = [(test_data, f) for f in list_func]
    
    with Pool() as p:
        results = p.map(exec_func, args_list)
        
    return results


def plot_execution_times_and_lengths(results, labels, path=None):
    times_list = [r[0] for r in results]
    lengths_list = [r[1] for r in results]
    
    # Nombre de points (axe X)
    x_axis = range(1, len(times_list[0]) + 1)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    # Graphique des temps
    for i, times in enumerate(times_list):
        ax1.plot(x_axis, times, label=labels[i])
    ax1.set_title("Temps d'exécution")
    ax1.set_xlabel("Nombre de points")
    ax1.set_ylabel("Temps (s)")
    ax1.legend()
    ax1.grid(True)

    # Graphique des longueurs (qualité)
    for i, lengths in enumerate(lengths_list):
        ax2.plot(x_axis, lengths, label=labels[i])
    ax2.set_title("Longueur du cycle (Qualité)")
    ax2.set_xlabel("Nombre de points")
    ax2.set_ylabel("Distance totale")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    if path:
        plt.savefig(path)
        plt.close(fig)
    else:
        plt.show()

def show_average(result, labels):
  for i in range(len(result)):
    times, lengths = result[i]
    avg_time = sum(times) / len(times)
    avg_length = sum(lengths) / len(lengths)
    print(f"{labels[i]} : Temps moyen : {avg_time:.6f} s, Longueur moyenne : {avg_length:.2f}")
    
def plot_average_time(result, labels, path=None):
    fig = plt.figure(figsize=(10, 6))
    for i in range(len(result)):
        times, lengths = result[i]
        avg_time = sum(times) / len(times)
        avg_length = sum(lengths) / len(lengths)
        plt.bar(i, avg_time, label=labels[i], alpha=0.7)
    plt.title("Temps d'exécution moyen")
    plt.xlabel("Algorithmes")
    plt.ylabel("Temps moyen (s)")
    plt.xticks(range(len(labels)), labels)
    plt.legend()
    if path:
        plt.savefig(path)
        plt.close(fig)
    else:
        plt.show()

def plot_average_length(result, labels, path=None):
    fig = plt.figure(figsize=(10, 6))
    for i in range(len(result)):
        times, lengths = result[i]
        avg_length = sum(lengths) / len(lengths)
        plt.bar(i, avg_length, label=labels[i], alpha=0.7)
    plt.title("Longueur moyenne du cycle")
    plt.xlabel("Algorithmes")
    plt.ylabel("Longueur moyenne")
    plt.xticks(range(len(labels)), labels)
    plt.legend()
    if path:
        plt.savefig(path)
        plt.close(fig)
    else:
        plt.show()


if __name__ == "__main__":
    number_of_tests = 10
    number_of_sommet = 10
    list_func = [pvc.ppp, pvc.optppp, pvc.optPrim, pvc.optOptPrim, pvc.hds]
    labels = ["PPP", "OptPPP", "OptPrim", "OptOptPrim", "HDS"]
    spinner = Spinner("Execution en cours...", delay=0.1)
    try:
        spinner.start()
        print("Execution des algorithmes de 1 à", number_of_tests, "sommets")
        results_1_n = exec_all_from_1_to_n_sommet(number_of_tests, list_func)
        print("Execution des algorithmes sur", number_of_sommet, "sommets, répété", number_of_tests, "fois")
        results = exec_all(number_of_tests, number_of_sommet, list_func)
    finally:
        spinner.stop()
    show_average(results, labels)
    # Calcul des pourcentages gagnés/perdus
    ppp_length = sum(results[0][1]) / len(results[0][1])
    optppp_length = sum(results[1][1]) / len(results[1][1])
    optprim_length = sum(results[2][1]) / len(results[2][1])

    pct_optppp_vs_ppp = ((optppp_length - ppp_length) / ppp_length) * 100
    pct_optprim_vs_optppp = ((optprim_length - optppp_length) / optppp_length) * 100

    print(f"\nOptPPP vs PPP: {pct_optppp_vs_ppp:+.2f}%")
    print(f"OptPrim vs OptPPP: {pct_optprim_vs_optppp:+.2f}%")
    plot_execution_times_and_lengths(results_1_n, labels)
    plot_average_time(results, labels)
    plot_average_length(results, labels)

