# Notice d’utilisation

Ce projet dépend des bibliothèques numpy et ...
Il dépend aussi de flask pour l'application web.

```bash
pip install numpy # (tout)
pip install flask # (web app)
```

ou plus simplement

```bash
pip install requirement.txt
```

# Algorithme

## Point le Plus Proche (PPP)

**$Procédure PPP (L, Q, D)$**

<u>Description :</u> Construit un cycle hamiltonien en insérant itérativement le point le plus proche du cycle actuel.

<u>Entrées :</u>

- $L$ : Liste de points $\{P_{1},...,P_{n}\}$
- $Q$ : Un point de départ choisi dans $L$
- $D$ : La matrice des distances $n \times n$

<u>Sorties :</u>

- $c$ : Un cycle hamiltonien
- $l$ : La longueur du cycle

<u>Début :</u>

- $c \leftarrow$ cycle trivial composé du seul point $Q$
- $l \leftarrow 0$
- Retirer $Q$ de $L$
- <u>Tant que</u> $L$ n'est pas vide <u>faire</u>
  - ($Q_i$, $Q_j$) <- TrouverCoupleMin($L$, $c$, $D$)
  - ($c$, $l$) <- InsérerDansCycle($c$, $Q_i$, $Q_j$, $D$, $l$)
  - Retirer $Q_i$ de $L$
- <u>Fin Tant que</u>
- Renvoyer $c, l$

<u>Fin</u>

---

**$InsérerDansCycle(c, Q_i, Q_j, D, l)$**

<u>Description :</u> Insère $Q_i$ dans $c$ soit entre $Q_j$ et son successeur, soit entre son prédécesseur et $Q_j$, selon le coût minimal, et met à jour la longueur du cycle.

<u>Entrées :</u>

- $c$ : Cycle partiel
- $Q_i$ : Point à insérer
- $Q_j$ : Point d’ancrage dans $c$
- $D$ : Matrice des distances
- $l$ : Longueur actuelle du cycle

<u>Sorties :</u>

- $c$ : Cycle mis à jour
- $l$ : Nouvelle longueur du cycle

<u>Début :</u>

- Soit $Q_{next}$ le successeur de $Q_j$ dans $c$
- Soit $Q_{prev}$ le prédécesseur de $Q_j$ dans $c$
- $coût_{droite} \leftarrow D[Q_j, Q_i] + D[Q_i, Q_{next}] - D[Q_j, Q_{next}]$
- $coût_{gauche} \leftarrow D[Q_{prev}, Q_i] + D[Q_i, Q_j] - D[Q_{prev}, Q_j]$
- <u>Si</u> $coût_{droite} \leq coût_{gauche}$ <u>alors</u>
  - Insérer $Q_i$ entre $Q_j$ et $Q_{next}$ dans $c$
  - $l \leftarrow l + coût_{droite}$
- <u>Sinon</u>
  - Insérer $Q_i$ entre $Q_{prev}$ et $Q_j$ dans $c$
  - $l \leftarrow l + coût_{gauche}$
- <u>Fin Si</u>
- Renvoyer $c, l$

<u>Fin</u>

---

**$TrouverCoupleMin(L, c, D)$**

<u>Description :</u> Trouve le couple $(Q_i, Q_j)$ tel que $Q_i \in L$, $Q_j \in c$ et la distance $D[Q_i, Q_j]$ est minimale.

<u>Entrées :</u>

- $L$ : Liste des points non encore visités
- $c$ : Le cycle partiel actuel
- $D$ : La matrice des distances $n \times n$

<u>Sorties :</u>

- $Q_i$ : Le point sélectionné dans $L$
- $Q_j$ : Le point d'ancrage dans $c$

<u>Début</u>

- $d_{min} \leftarrow \infty$
- $Q_i \leftarrow$ vide
- $Q_j \leftarrow$ vide
- <u>Pour</u> chaque point $u$ appartenant à $L$ <u>faire</u>
  - <u>Pour</u> chaque point $v$ appartenant à $c$ <u>faire</u>
    - <u>Si</u> $D[u, v] < d_{min}$ <u>alors</u>
      - $d_{min} \leftarrow D[u, v]$
      - $Q_i \leftarrow u$
      - $Q_j \leftarrow v$
    - <u>Fin Si</u>
  - <u>Fin Pour</u>
- <u>Fin Pour</u>
- <u>Renvoyer</u> $Q_i, Q_j$

<u>Fin</u>

## Point le Plus Proche Optimisé (OptPPP)

## Arbre couvrant de poids minimum (OptPrim)

## évalutation et séparation progressive (“brunch and bound”) (HDS)
