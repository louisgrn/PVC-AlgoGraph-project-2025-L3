import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
import time
import sys
import threading
import itertools
import pvc_lib as pvc


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
    
    # Affiche un spinner pendant l'exécution pour indiquer que le travail est en cours
    stop = threading.Event()
    def _spin():
        for c in itertools.cycle("|/-\\"):
            if stop.is_set():
                break
            sys.stdout.write(f"\rExecution en cours (1..{n}) {c}")
            sys.stdout.flush()
            time.sleep(0.1)
        # Efface la ligne une fois terminé
        sys.stdout.write('\r' + ' ' * (30) + '\r')
        sys.stdout.flush()

    th = threading.Thread(target=_spin)
    th.start()
    try:
        with Pool() as p:
            results = p.map(exec_func, args_list)
    finally:
        stop.set()
        th.join()
        
    return results

def exec_all(m, sommet_n, list_func):
    # Générer les mêmes points pour tous les algos pour une comparaison équitable
    test_data = [pvc.generer_points(sommet_n) for _ in range(1, m+1)]
    
    args_list = [(test_data, f) for f in list_func]
    
    # Affiche un spinner pendant l'exécution pour indiquer que le travail est en cours
    stop = threading.Event()
    def _spin():
        for c in itertools.cycle("|/-\\"):
            if stop.is_set():
                break
            sys.stdout.write(f"\rExecution en cours ({m}x {sommet_n} sommets) {c}")
            sys.stdout.flush()
            time.sleep(0.1)
        # Efface la ligne une fois terminé
        sys.stdout.write('\r' + ' ' * (40) + '\r')
        sys.stdout.flush()

    th = threading.Thread(target=_spin)
    th.start()
    try:
        with Pool() as p:
            results = p.map(exec_func, args_list)
    finally:
        stop.set()
        th.join()
        
    return results


def plot_execution_times_and_lengths(results, labels):
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
    plt.show()

def show_average(result, labels):
  for i in range(len(result)):
    times, lengths = result[i]
    avg_time = sum(times) / len(times)
    avg_length = sum(lengths) / len(lengths)
    print(f"{labels[i]} : Temps moyen : {avg_time:.6f} s, Longueur moyenne : {avg_length:.2f}")
    
def plot_average_time(result, labels):
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
    plt.show()

def plot_average_length(result, labels):
    for i in range(len(result)):
        times, lengths = result[i]
        avg_length = sum(lengths) / len(lengths)
        plt.bar(i, avg_length, label=labels[i], alpha=0.7)
    plt.title("Longueur moyenne du cycle")
    plt.xlabel("Algorithmes")
    plt.ylabel("Longueur moyenne")
    plt.xticks(range(len(labels)), labels)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    number_of_tests = 100
    number_of_sommet = 200
    list_func = [pvc.ppp, pvc.optppp, pvc.optPrim, pvc.optOptPrim]
    labels = ["PPP", "OptPPP", "OptPrim", "OptOptPrim"]
    print("Execution des algorithmes de 1 à", number_of_tests, "sommets")
    results_1_n = exec_all_from_1_to_n_sommet(number_of_tests, list_func)
    print("Execution des algorithmes sur", number_of_sommet, "sommets, répété", number_of_tests, "fois")
    results = exec_all(number_of_tests, number_of_sommet, list_func)
    show_average(results, labels)
    plot_execution_times_and_lengths(results_1_n, labels)
    plot_average_time(results, labels)
    plot_average_length(results, labels)

