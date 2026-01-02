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

def ppp(points, D, Q=None):
    """
    Procédure PPP : construit un cycle hamiltonien en insérant itérativement le point le plus proche du cycle actuel.
    Args:
        points (list): Liste de tuples (x, y)
        Q (int, optional): Indice du point de départ. Si None, prend 0.
        D (np.ndarray): Matrice des distances. Si None, la calcule.
    Returns:
        tuple: (c, l) cycle hamiltonien (liste d'indices), longueur du cycle
    """
    n = len(points)
    if n == 0:
        return [], 0.0
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

#%% Point le Plus Proche optimisé (OptPPP) :

def decroise(c, D):
    """
    Améliore le cycle en décroisant les arêtes.
    Args:
        c (list): Cycle hamiltonien (liste d'indices)
        D (np.ndarray): Matrice des distances
    Returns:
        tuple: (c, l) cycle optimisé et sa nouvelle longueur
    """
    n = len(c)
    amelioration = True
    while amelioration:
        amelioration = False
        for i in range(n - 2):
            for j in range(i + 2, n):
                u = c[i]
                v = c[i + 1]
                x = c[j]
                y = c[(j + 1) % n]
                d_act = D[u, v] + D[x, y]
                d_nouv = D[u, x] + D[v, y]
                if d_nouv < d_act:
                    # Inversion de la sous-séquence entre i+1 et j
                    c[i+1:j+1] = c[i+1:j+1][::-1]
                    amelioration = True

    # Recalcul de la longueur totale du cycle optimisé
    l = 0.0
    for k in range(n):
        l += D[c[k], c[(k + 1) % n]]

    return c, l

def optppp(c, D):
    """
    Procédure OptPPP : améliore le cycle fourni par PPP en décroisant les arêtes.
    Args:
        c (list): Cycle hamiltonien initial (liste d'indices)
        D (np.ndarray): Matrice des distances
    Returns:
        tuple: (c, l) cycle optimisé et sa nouvelle longueur
    """
    return decroise(c, D)

#%% Prim optimisé (OptPrim) :

class GraphePrim:
    def __init__(self, n):
        """
        Initialise la structure de données pour l'algorithme de Prim.
        Args:
            n (int): Nombre de sommets du graphe.
        """
        self.cle = [float('inf')] * n
        self.pred = [None] * n
        self.noeudTas = list(range(n))
        self.tas = list(range(n))
    
    def echanger(self, i, j):
        """
        Échange deux éléments dans le tas et met à jour leurs positions.
        Args:
            i (int): Indice du premier élément dans le tas.
            j (int): Indice du deuxième élément dans le tas.
        """
        temp = self.tas[i]
        self.tas[i] = self.tas[j]
        self.tas[j] = temp
        self.noeudTas[self.tas[i]] = i
        self.noeudTas[self.tas[j]] = j

    def priorite(self, i):
        """
        Retourne la priorité (clé) d'un élément à une position donnée dans le tas.
        Args:
            i (int): Indice dans le tas.
        Returns:
            float: La valeur de la clé associée.
        """
        return self.cle[self.tas[i]]
        
    def versLeHaut(self, i):
        """
        Fait remonter un élément dans le tas pour respecter la propriété de tas min.
        Args:
            i (int): Indice de l'élément à faire remonter.
        """
        while i > 0 and self.priorite(i) < self.priorite((i - 1) // 2):
            self.echanger(i, (i - 1) // 2)
            i = (i - 1) // 2

    def versLeBas(self, i):
        """
        Fait descendre un élément dans le tas pour respecter la propriété de tas min.
        Args:
            i (int): Indice de l'élément à faire descendre.
        """
        s = 2 * i + 1
        while s < len(self.tas):
            if s + 1 < len(self.tas) and self.priorite(s + 1) < self.priorite(s):
                s += 1
            if self.priorite(i) > self.priorite(s):
                self.echanger(i, s)
                i = s
                s = 2 * i + 1
            else:
                break

def prim(D, r0=0):
    """
    Algorithme de Prim pour trouver l'arbre couvrant de poids minimal.
    Args:
        D (np.ndarray): Matrice des distances
        r0 (int, optional): Sommet de départ. Par défaut 0.
    Returns:
        list: Liste des prédécesseurs (pred[i] est le parent de i dans l'arbre)
    """
    n = len(D)
    graphe = GraphePrim(n)
    pres = [True] * n

    # Initialiser la clé du sommet de départ
    graphe.cle[r0] = 0
    # Placer r0 à la racine du tas
    graphe.echanger(0, graphe.noeudTas[r0])

    while len(graphe.tas) > 0:
        u = graphe.tas[0]
        pres[u] = False
        
        graphe.echanger(0, len(graphe.tas) - 1)
        graphe.tas.pop()
        
        if len(graphe.tas) > 0:
            graphe.versLeBas(0)

        for v in range(n):
            if pres[v] and D[u, v] < graphe.cle[v]:
                graphe.cle[v] = D[u, v]
                graphe.pred[v] = u
                graphe.versLeHaut(graphe.noeudTas[v])
        
    return graphe.pred

def pred_to_tree(pred):
    """
    Convertit la liste des prédécesseurs en une structure d'arbre (dictionnaire d'adjacence).
    Args:
        pred (list): Liste des prédécesseurs où pred[i] est le parent de i.
    Returns:
        tuple: (d, racine) où d est le dictionnaire d'adjacence et racine est l'indice de la racine.
    """
    d = {}
    racine = -1
    for i in range(len(pred)):
        d[i] = []
        if pred[i] is None or pred[i] == -1:
            racine = i

    for i in range(len(pred)):
        if pred[i] is not None and pred[i] != -1:
            d[pred[i]].append(i)

    return d, racine


def parcours_prefixe(d,racine):
    """
    Effectue un parcours préfixe (DFS) de l'arbre pour obtenir l'ordre de visite des sommets.
    Args:
        d (dict): Dictionnaire d'adjacence de l'arbre.
        racine (int): Indice de la racine de l'arbre.
    Returns:
        list: Liste des sommets dans l'ordre du parcours préfixe.
    """
    stack = [racine]
    p = [0] * len(d)
    p_etoile = [racine]
    p[racine] = 1
    count = 2
    while len(stack) > 0 :
        lst_voisin = d[stack[len(stack) -1]]
        rep = False

        for i in range(len(lst_voisin)):
            voisin = lst_voisin[i]
            if p[voisin] ==0 :
                stack.append(voisin)
                p_etoile.append(voisin)
                p[voisin] = count
                count +=1
                rep = True
                break

        if not rep :
            stack.pop()
    return p_etoile

def optPrim(points, D=None, r0=0):
    """
    Procédure OptPrim : construit un cycle hamiltonien à partir de l'arbre couvrant minimal en utilisant un parcours préfixe.
    Args:
        points (list): Liste de tuples (x, y)
        D (np.ndarray, optional): Matrice des distances. Si None, elle est calculée.
        r0 (int, optional): Sommet de départ pour Prim. Par défaut 0.
    Returns:
        tuple: (c, l) cycle hamiltonien (liste d'indices), longueur du cycle
    """
    if D is None:
        D = calculer_matrice_distances(points)

    pred = prim(D, r0)
    d, racine = pred_to_tree(pred)
    c = parcours_prefixe(d, racine)

    # Calcul de la longueur totale du cycle
    l = 0.0
    n = len(c)
    for k in range(n):
        l += D[c[k], c[(k + 1) % n]]

    return c, l

#%% Prim + décroisé (OptOptPrim) :

def optOptPrim(points, D=None, r0=0):
    """
    Procédure OptOptPrim : combine OptPrim (MST + DFS) et décroisement.
    Génère un cycle initial avec l'heuristique de l'arbre couvrant minimum,
    puis l'améliore avec une recherche locale (décroisement).

    Args:
        points (list): Liste de tuples (x, y)
        D (np.ndarray, optional): Matrice des distances. Si None, elle est calculée.
        r0 (int, optional): Sommet de départ pour Prim. Par défaut 0.
    Returns:
        tuple: (c, l) cycle hamiltonien optimisé, longueur du cycle
    """
    if D is None:
        D = calculer_matrice_distances(points)

    # Étape 1: Obtenir le cycle initial via Prim + Parcours Préfixe
    c_init, _ = optPrim(points, D, r0)

    # Étape 2: Optimiser ce cycle avec décroisement
    return decroise(c_init, D)