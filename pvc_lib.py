import math
import numpy as np
import numpy.random as rd

#%% Génération des graphes :

def generer_points(n):
    """
    Génère n points avec des coordonnées tirées aléatoirement dans l'intervalle
    [0, 1].

    Args:
        n (int): Le nombre de points à générer.

    Returns:
        list: Une liste de tuples (x, y).
    """
    # Matrice n x 2 avec des valeurs entre 0 et 1
    points_array = rd.rand(n, 2)

    # Liste de tuples (x, y)
    points = [(float(p[0]), float(p[1])) for p in points_array]
    return points

def lire_points_fichier(chemin_fichier):
    """
    Lit les points depuis un fichier texte.
    Le fichier doit contenir un point par ligne sous la forme (x, y).

    Args:
        chemin_fichier (str): Le chemin vers le fichier.

    Returns:
        list: Une liste de tuples (x, y).
    """
    points = []
    try:
        with open(chemin_fichier, 'r') as f:
            for ligne in f:
                ligne = ligne.strip()
                if ligne:
                    # Enlever les parenthèses et virgules
                    coords = ligne.replace('(', '').replace(')', '').split(',')

                    if len(coords) == 2:
                        try:
                            x = float(coords[0].strip())
                            y = float(coords[1].strip())
                            points.append((x, y))
                        except ValueError:
                            print(f"Ignoré (format invalide) : {ligne}")
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{chemin_fichier}' est introuvable.")
        return []

    return points

def calculer_matrice_distances(points):
    """
    Calcule la matrice D de dimension n x n.
    D[i,j] contient la distance euclidienne entre Pi et Pj.

    Args:
        points (list): Liste de tuples (x, y).

    Returns:
        numpy.ndarray: Matrice n x n des distances.
    """
    n = len(points)
    # Initialisation de la matrice avec des zéros
    D = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i != j:
                xi, yi = points[i]
                xj, yj = points[j]
                # Calcul de la distance
                dist = math.sqrt((xi - xj)**2 + (yi - yj)**2)
                D[i, j] = dist
            else:
                D[i, j] = 0.0

    return D


#%% Point le Plus Proche (PPP) :

def trouver_couple_min(L, c, D):
    """
    Trouve le couple (Q_i, Q_j) tel que Q_i dans L, Q_j dans c et D[Q_i, Q_j] est minimale.
    Args:
        L (list): Liste des indices des points non encore visités
        c (list): Liste des indices du cycle partiel actuel
        D (np.ndarray): Matrice des distances n x n
    Returns:
        tuple: (Q_i, Q_j) indices
    """
    d_min = float('inf')
    Q_i = None
    Q_j = None
    for u in L:
        for v in c:
            if D[u, v] < d_min:
                d_min = D[u, v]
                Q_i = u
                Q_j = v
    return Q_i, Q_j

def inserer_dans_cycle(c, Q_i, Q_j, D, l):
    """
    Insère Q_i dans c entre Q_j et son point adjacent, met à jour la longueur du cycle.
    Args:
        c (list): Liste des indices du cycle partiel
        Q_i (int): Indice du point à insérer
        Q_j (int): Indice du point d'ancrage dans c
        D (np.ndarray): Matrice des distances
        l (float): Longueur actuelle du cycle
    Returns:
        tuple: (c, l) cycle mis à jour et nouvelle longueur
    """
    n = len(c)
    idx_j = c.index(Q_j)
    
    # Insertion entre Q_j et le suivant (j+1)
    idx_next = (idx_j + 1) % n
    Q_next = c[idx_next]
    cout_droite = D[Q_j, Q_i] + D[Q_i, Q_next] - D[Q_j, Q_next]
    
    # Insertion entre le précédent (j-1) et Q_j
    idx_prev = (idx_j - 1) % n
    Q_prev = c[idx_prev]
    cout_gauche = D[Q_prev, Q_i] + D[Q_i, Q_j] - D[Q_prev, Q_j]
    
    # Choix du meilleur
    if cout_droite <= cout_gauche:
        c.insert(idx_j + 1, Q_i)
        l += cout_droite
    else:
        c.insert(idx_j, Q_i)
        l += cout_gauche

    return c, l

def ppp(points, Q=None, D=None):
    """
    Procédure PPP : construit un cycle hamiltonien en insérant itérativement le point le plus proche du cycle actuel.
    Args:
        points (list): Liste de tuples (x, y)
        Q (int, optional): Indice du point de départ. Si None, prend 0.
        D (np.ndarray, optional): Matrice des distances. Si None, la calcule.
    Returns:
        tuple: (c, l) cycle hamiltonien (liste d'indices), longueur du cycle
    """
    n = len(points)
    if n == 0:
        return [], 0.0
    if D is None:
        D = calculer_matrice_distances(points)
    if Q is None:
        Q = 0
    L = list(range(n))
    c = [Q]
    l = 0.0
    L.remove(Q)
    while L != []:
        Q_i, Q_j = trouver_couple_min(L, c, D)
        c, l = inserer_dans_cycle(c, Q_i, Q_j, D, l)
        L.remove(Q_i)
    return c, l

