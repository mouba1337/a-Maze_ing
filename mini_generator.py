import random
from collections import deque

# 1=Haut, 2=Droite, 4=Bas, 8=Gauche
DIRS = {1: (0, -1), 2: (1, 0), 4: (0, 1), 8: (-1, 0)}
OPPOSITE = {1: 4, 2: 8, 4: 1, 8: 2}

class MiniMaze:
    def __init__(self, width, height):
        self.w = width
        self.h = height
        # 15 = 0b1111 (Tous les murs sont présents)
        self.grid = [[15 for _ in range(width)] for _ in range(height)]

    def generate_dfs(self, x, y, visited):
        """Génère le labyrinthe avec la Recherche en Profondeur (DFS)"""
        visited.add((x, y))
        ways = [1, 2, 4, 8]
        random.shuffle(ways) # Direction aléatoire

        for w in ways:
            dx, dy = DIRS[w]
            nx, ny = x + dx, y + dy

            # Si la case suivante est dans la grille et n'a pas été visitée
            if 0 <= nx < self.w and 0 <= ny < self.h and (nx, ny) not in visited:
                # On casse le mur de la case actuelle, et le mur opposé de la case cible
                self.grid[y][x] &= ~w
                self.grid[ny][nx] &= ~OPPOSITE[w]
                # Appel récursif
                self.generate_dfs(nx, ny, visited)

    def solve_bfs(self, start, end):
        """Résout le labyrinthe avec la Recherche en Largeur (BFS)"""
        # La file contient : (x, y, chemin_parcouru)
        queue = deque([(start[0], start[1], [])])
        visited = set([start])

        while queue:
            x, y, path = queue.popleft()

            # Si on a trouvé la sortie, on renvoie le chemin + la case finale
            if (x, y) == end:
                return path + [(x, y)]

            # Pour chaque direction possible
            for w in [1, 2, 4, 8]:
                # Si IL N'Y A PAS de mur dans cette direction
                if (self.grid[y][x] & w) == 0:
                    dx, dy = DIRS[w]
                    nx, ny = x + dx, y + dy
                    
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        # On ajoute à la file pour le prochain tour
                        queue.append((nx, ny, path + [(x, y)]))
        return [] # Pas de solution
