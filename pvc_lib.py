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
    # Liste pour stocker les points
    points = []
    # Lecture du fichier
    try:
        with open(chemin_fichier, 'r') as f:
            # Parcourir chaque ligne du fichier
            for ligne in f:
                # Nettoyer la ligne
                ligne = ligne.strip()
                # Ignorer les lignes vides
                if ligne:
                    # Enlever les parenthèses et virgules
                    coords = ligne.replace('(', '').replace(')', '').split(',')
                    
                    # Vérifier qu'on a bien deux coordonnées
                    if len(coords) == 2:
                        # Convertir en float et ajouter à la liste des points
                        try:
                            x = float(coords[0].strip())
                            y = float(coords[1].strip())
                            points.append((x, y))
                        except ValueError:
                            # Gérer le cas où la conversion échoue et ignorer la ligne
                            print(f"Ignoré (format invalide) : {ligne}")
    # Gérer le cas où le fichier n'existe pas
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
    # Nombre de points
    n = len(points)
    # Initialisation de la matrice avec des zéros
    D = np.zeros((n, n))

    # Calcul des distances euclidiennes
    for i in range(n):
        for j in range(n):
            # si les points sont différents
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
    # Initialisation des variables pour suivre la distance minimale et les indices correspondants
    d_min = float('inf')
    Q_i = None
    Q_j = None
    # Parcourir tous les couples (u, v) avec u dans L et v dans c
    for u in L:
        for v in c:
            # Vérifier si la distance D[u, v] est inférieure à la distance minimale actuelle
            if D[u, v] < d_min:
                # Mettre à jour la distance minimale et les indices correspondants
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
    # Taille du cycle
    n = len(c)
    # Index de Q_j dans le cycle
    idx_j = c.index(Q_j)

    # Insertion entre Q_j et le suivant (j+1)
    idx_next = (idx_j + 1) % n
    Q_next = c[idx_next]
    cout_droite = D[Q_j, Q_i] + D[Q_i, Q_next] - D[Q_j, Q_next]

    # Insertion entre le précédent (j-1) et Q_j
    idx_prev = (idx_j - 1) % n
    Q_prev = c[idx_prev]
    cout_gauche = D[Q_prev, Q_i] + D[Q_i, Q_j] - D[Q_prev, Q_j]

    # Choix du meilleur cout d'insertion
    if cout_droite <= cout_gauche:
        c.insert(idx_j + 1, Q_i)
        l += cout_droite
    else:
        c.insert(idx_j, Q_i)
        l += cout_gauche

    return c, l

def ppp(D, Q=0):
    """
    Procédure PPP : construit un cycle hamiltonien en insérant itérativement le point le plus proche du cycle actuel.
    Args:
        D (np.ndarray): Matrice des distances.
        Q (int, optional): Indice du point de départ. Si None, prend 0.
    Returns:
        tuple: (c, l) cycle hamiltonien (liste d'indices), longueur du cycle
    """
    # taille du graphe
    n = len(D)
    if n == 0:
        return [], 0.0
    # Liste des points non encore visités
    L = list(range(n))
    # Initialisation du cycle avec le point de départ Q
    c = [Q]
    # Longueur initiale du cycle
    l = 0.0
    # Retirer Q de la liste des points non visités
    L.remove(Q)

    # Boucle principale d'insertion tant qu'il reste des points à insérer
    while L != []:
        # trouver le couple (Q_i, Q_j) minimisant la distance
        Q_i, Q_j = trouver_couple_min(L, c, D)
        # insérer Q_i dans le cycle c et mettre à jour la longueur
        c, l = inserer_dans_cycle(c, Q_i, Q_j, D, l)
        # retirer Q_i de L
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
    # taille du cycle
    n = len(c)
    amelioration = True
    # Boucle jusqu'à ce qu'il n'y ait plus d'amélioration
    while amelioration:
        amelioration = False
        # Parcourir toutes les paires d'arêtes non adjacentes
        for i in range(n - 2):
            # j doit être au moins i+2 pour éviter les arêtes adjacentes
            for j in range(i + 2, n):
                # u et v sont les extrémités de la première arête
                u = c[i]
                v = c[i + 1]
                # x et y sont les extrémités de la deuxième arête
                x = c[j]
                y = c[(j + 1) % n]
                # calcul des distances actuelles et nouvelles
                d_act = D[u, v] + D[x, y]
                d_nouv = D[u, x] + D[v, y]
                # Si le décroisement améliore la longueur du cycle
                if d_nouv < d_act:
                    # Inversion de la sous-séquence entre i+1 et j
                    c[i+1:j+1] = c[i+1:j+1][::-1]
                    amelioration = True

    # Recalcul de la longueur totale du cycle optimisé
    l = 0.0
    for k in range(n):
        l += D[c[k], c[(k + 1) % n]]

    return c, l

def optppp(D, r0=0):
    """
    Procédure OptPPP : améliore le cycle fourni par PPP en décroisant les arêtes.
    Args:
        D (np.ndarray): Matrice des distances
        r0 (int, optional): Sommet de départ. Par défaut 0.
    Returns:
        tuple: (c, l) cycle optimisé et sa nouvelle longueur
    """
    # Obtenir le cycle initial via PPP
    c, _ = ppp(D, r0)
    # Décroisement
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
        # Remonter tant que l'élément a une priorité inférieure à son parent
        while i > 0 and self.priorite(i) < self.priorite((i - 1) // 2):
            # Échanger avec le parent
            self.echanger(i, (i - 1) // 2)
            # Mettre à jour l'indice pour continuer à remonter
            i = (i - 1) // 2

    def versLeBas(self, i):
        """
        Fait descendre un élément dans le tas pour respecter la propriété de tas min.
        Args:
            i (int): Indice de l'élément à faire descendre.
        """
        # Indice du fils gauche
        s = 2 * i + 1
        # Descendre tant que l'élément a une priorité supérieure à l'un de ses enfants
        while s < len(self.tas):
            # Trouver l'enfant avec la plus petite priorité en comparant les deux fils et si c'est le droit
            if s + 1 < len(self.tas) and self.priorite(s + 1) < self.priorite(s):
                # Prendre le fils droit
                s += 1
            # Si l'élément courant a une priorité supérieure à son enfant
            if self.priorite(i) > self.priorite(s):
                # echanger et continuer à descendre
                self.echanger(i, s)
                # Mettre à jour l'indice courant de l'elément à descendre
                i = s
                # Mettre à jour l'indice avec le fils gauche
                s = 2 * i + 1
            # Sinon, la propriété de tas est respectée
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

    # Boucle principale de Prim
    while len(graphe.tas) > 0:
        # Extraire le sommet u de clé minimale
        u = graphe.tas[0]
        # Marquer u comme inclus dans l'arbre
        pres[u] = False
        
        # Retirer u du tas
        graphe.echanger(0, len(graphe.tas) - 1)
        graphe.tas.pop()
        
        # Reajuster le tas
        if len(graphe.tas) > 0:
            graphe.versLeBas(0)

        # Mettre à jour les clés et prédécesseurs des sommets adjacents
        for v in range(n):
            # Si v est encore dans le tas et l'arête (u, v) est plus petite que la clé actuelle
            if pres[v] and D[u, v] < graphe.cle[v]:
                # Mettre à jour la clé et le prédécesseur
                graphe.cle[v] = D[u, v]
                graphe.pred[v] = u
                # Faire remonter v dans le tas
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
    # Initialisation du dictionnaire d'adjacence
    for i in range(len(pred)):
        # Chaque nœud a une liste vide au départ
        d[i] = []
        # Trouver la racine
        if pred[i] is None or pred[i] == -1:
            racine = i

    # Remplir le dictionnaire d'adjacence
    for i in range(len(pred)):
        # Ajouter i comme enfant de son prédécesseur
        if pred[i] is not None and pred[i] != -1:
            # Ajouter i à la liste des enfants de pred[i]
            d[pred[i]].append(i)

    return d, racine


def parcours_prefixe(d, racine):
    """
    Effectue un parcours préfixe (DFS) de l'arbre pour obtenir l'ordre de visite des sommets.
    Args:
        d (dict): Dictionnaire d'adjacence de l'arbre.
        racine (int): Indice de la racine de l'arbre.
    Returns:
        list: Liste des sommets dans l'ordre du parcours préfixe.
    """
    # Initialisation de la pile avec la racine
    stack = [racine]
    # Marquage des sommets visités en lui attribuant l'ordre de visite
    p = [0] * len(d)
    # Liste du parcours préfixe
    p_etoile = [racine]
    # Marquer la racine comme visitée
    p[racine] = 1
    count = 2

    # Parcours prefixe
    while len(stack) > 0 :
        # Récupérer le sommet au sommet de la pile
        lst_voisin = d[stack[len(stack) -1]]
        rep = False

        # Parcourir les voisins
        for i in range(len(lst_voisin)):
            # voisin courant de i
            voisin = lst_voisin[i]
            # Si le voisin n'a pas été visité
            if p[voisin] ==0 :
                # L'ajouter à la pile
                stack.append(voisin)
                # L'ajouter au parcours préfixe
                p_etoile.append(voisin)
                # Marquer comme visité en lui attribuant l'ordre de visite
                p[voisin] = count
                count +=1
                # Indiquer qu'on a trouvé un voisin non visité
                rep = True
                break

        # Si aucun voisin non visité n'a été trouvé, dépiler
        if not rep :
            stack.pop()

    return p_etoile

def optPrim(D, r0=0):
    """
    Procédure OptPrim : construit un cycle hamiltonien à partir de l'arbre couvrant minimal en utilisant un parcours préfixe.
    Args:
        D (np.ndarray): Matrice des distances.
        r0 (int, optional): Sommet de départ pour Prim. Par défaut 0.
    Returns:
        tuple: (c, l) cycle hamiltonien (liste d'indices), longueur du cycle
    """
    # Obtenir l'arbre couvrant minimal via Prim
    pred = prim(D, r0)
    # Convertir les prédécesseurs en arbre
    d, racine = pred_to_tree(pred)
    # Obtenir le cycle via un parcours préfixe de l'arbre
    c = parcours_prefixe(d, racine)

    # Calcul de la longueur totale du cycle
    l = 0.0
    n = len(c)
    for k in range(n):
        l += D[c[k], c[(k + 1) % n]]

    return c, l

#%% Prim + décroisé (OptOptPrim) :

def optOptPrim(D, r0=0):
    """
    Procédure OptOptPrim : combine OptPrim (MST + DFS) et décroisement.
    Génère un cycle initial avec l'heuristique de l'arbre couvrant minimum,
    puis l'améliore avec une recherche locale (décroisement).

    Args:
        D (np.ndarray): Matrice des distances.
        r0 (int, optional): Sommet de départ pour Prim. Par défaut 0.
    Returns:
        tuple: (c, l) cycle hamiltonien optimisé, longueur du cycle
    """
    # Obtenir le cycle initial via Prim + Parcours Préfixe
    c_init, _ = optPrim(D, r0)
    # Décroisement
    return decroise(c_init, D)

#%% HDS

class Noeud:
    def __init__(self, chemin, cout_actuel, D):
        self.chemin = chemin
        self.cout_actuel = cout_actuel
        self.dernier = chemin[-1]

        self.borne = self.calc_borne(D)

    def calc_borne(self, D):
        """
        Calcule une borne inférieure du coût total pour le noeud courant. (demi somme)
        Args:
            D (np.ndarray): Matrice des distances
        Returns:
            float: Borne inférieure du coût total (demi somme)
        """
        n = len(D)
        some = 0.0
        debut = self.chemin[0]
        fin = self.chemin[-1]

        for i in range(n):
            # Cas 1 : Le sommet est déja completement dans le chemin : A->B->i->C->D
            if i in self.chemin and not i == debut and not i == fin:
                idx = self.chemin.index(i)
                # prendre les deux points adjacents dans le chemin
                some += D[self.chemin[idx - 1], i] + D[i, self.chemin[idx + 1]]

            # Cas 2 : Une extrémité du chemin n'est pas dans le chemin : i->B->C->D ou A->B->C->i
            elif (i == debut or i == fin) and len(self.chemin) > 1:
                # prendre le point adjacent qui est dans le chemin
                if i == debut:
                    some += D[i, self.chemin[1]]
                else:
                    some += D[self.chemin[-2], i]
                # trouve le minimum parmi les autres
                min_val = float('inf')
                for j in range(n):
                    if min_val > D[i, j] and not i == j:
                        if i == debut and j != self.chemin[1]:
                            min_val = D[i, j]
                        elif i == fin and j != self.chemin[-2]:
                            min_val = D[i, j]
                some += min_val

            # Cas 3 : i non dans le chemin : A->B->C->D     Z
            else:
                sorted_indices = np.argsort(D[i])
                # sorted_indices[0] est i (dist 0), on prend [1] et [2]
                some += D[i, sorted_indices[1]] + D[i, sorted_indices[2]]

        borne = some / 2.0
        return borne

    def __lt__(self, other):
        return self.borne < other.borne

class Tas:
    def __init__(self):
        self.tas = []

    def __versLeHaut(self, i):
        """
        Fait remonter un élément dans le tas pour respecter la propriété de tas min.
        Args:
            i (int): Indice de l'élément à faire remonter.
        """
        # Remonter tant que l'élément a une priorité inférieure à son parent
        while i > 0 and self.priorite(i) < self.priorite((i - 1) // 2):
            # Échanger avec le parent
            self.echanger(i, (i - 1) // 2)
            # Mettre à jour l'indice pour continuer à remonter
            i = (i - 1) // 2

    def __versLeBas(self, i):
        """
        Fait descendre un élément dans le tas pour respecter la propriété de tas min.
        Args:
            i (int): Indice de l'élément à faire descendre.
        """
        # Indice du fils gauche
        s = 2 * i + 1
        # Descendre tant que l'élément a une priorité supérieure à l'un de ses enfants
        while s < len(self.tas):
            # Trouver l'enfant avec la plus petite priorité en comparant les deux fils et si c'est le droit
            if s + 1 < len(self.tas) and self.priorite(s + 1) < self.priorite(s):
                # Prendre le fils droit
                s += 1
            # Si l'élément courant a une priorité supérieure à son enfant
            if self.priorite(i) > self.priorite(s):
                # echanger et continuer à descendre
                self.echanger(i, s)
                # Mettre à jour l'indice courant de l'elément à descendre
                i = s
                # Mettre à jour l'indice avec le fils gauche
                s = 2 * i + 1
            # Sinon, la propriété de tas est respectée
            else:
                break

    def insere(self, elem):
        """
        Insère un nouvel élément dans le tas et rétablit la propriété de tas min.

        Args:
            elem: L'élément à insérer.
        """
        self.tas.append(elem)
        self.__versLeHaut(len(self.tas) - 1)

    def extraire_min(self):
        """
        Extrait et retourne l'élément de priorité minimale (la racine du tas).
        Réorganise le tas après l'extraction.

        Returns:
            L'élément minimal, ou None si le tas est vide.
        """
        if len(self.tas) == 0:
            return None
        # Extraire le minimum (racine)
        min_noeud = self.tas[0]
        # Remplacer la racine par le dernier élément
        self.tas[0] = self.tas[-1]
        self.tas.pop()
        # Réajuster le tas
        if len(self.tas) > 0:
            self.__versLeBas(0)
        return min_noeud
    
    def priorite(self, i):
        return self.tas[i].borne

    def echanger(self, i, j):
        self.tas[i], self.tas[j] = self.tas[j], self.tas[i]

def hds(D):
    """
    construire un cycle hamiltonien en utilisant la méthode de Branch and Bound (HDS).
    Args:
        D (np.ndarray): Matrice des distances.
    Returns:
        tuple: (c, l) cycle hamiltonien (liste d'indices), longueur du cycle
    """
    c = []
    l = float('inf')
    n = len(D)

    if n < 3:
        if n == 0:
            return [], 0
        if n == 1:
            return [0, 0], 0
        if n == 2:
            return [0, 1, 0], D[0, 1] * 2

    tas = Tas()
    # Initialisation du tas avec le noeud racine
    noeud_racine = Noeud([0], 0.0, D)
    tas.insere(noeud_racine)

    while True:
        # Extraire le noeud avec la plus petite borne
        noeud_courant = tas.extraire_min()
        if noeud_courant is None:
            break

        # si la borne théorique est supérieure à la meilleure solution trouvée, on ignore ce noeud
        if noeud_courant.borne >= l:
            continue

        # Si le chemin est complet
        if len(noeud_courant.chemin) == n:
            # Ajouter le coût de retour au point de départ
            cout_total = noeud_courant.cout_actuel + D[noeud_courant.dernier, noeud_courant.chemin[0]]
            # Si ce coût est inférieur à la meilleure solution trouvée
            if cout_total < l:
                l = cout_total
                c = noeud_courant.chemin + [noeud_courant.chemin[0]]
        else:
            # Générer les successeurs possibles
            for i in range(n):
                if i not in noeud_courant.chemin:
                    nouveau_chemin = noeud_courant.chemin + [i]
                    nouveau_cout = noeud_courant.cout_actuel + D[noeud_courant.dernier, i]
                    nouveau_noeud = Noeud(nouveau_chemin, nouveau_cout, D)
                    # Insérer le nouveau noeud dans le tas
                    tas.insere(nouveau_noeud)
                    
    return c, l