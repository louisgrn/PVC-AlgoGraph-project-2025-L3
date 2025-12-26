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