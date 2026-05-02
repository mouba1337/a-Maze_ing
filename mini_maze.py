from mini_generator import MiniMaze

def render_maze(maze, path):
    """Affiche le labyrinthe et le chemin de résolution"""
    for y in range(maze.h):
        top_line = ""
        mid_line = ""
        for x in range(maze.w):
            cell = maze.grid[y][x]
            
            # Dessine le mur du Haut (1)
            if cell & 1:
                top_line += "+---"
            else:
                top_line += "+   "
                
            # Dessine le mur de Gauche (8) et le contenu (le chemin)
            if cell & 8:
                west = "|"
            else:
                west = " "
                
            content = " * " if (x, y) in path else "   "
            mid_line += west + content
            
        print(top_line + "+")
        # On ferme avec un mur à droite pour l'esthétique
        print(mid_line + "|") 

    # Ligne finale en bas
    print("+---" * maze.w + "+")

if __name__ == "__main__":
    WIDTH, HEIGHT = 10, 10
    
    # 1. Instanciation
    maze = MiniMaze(WIDTH, HEIGHT)
    
    # 2. Génération
    print("Génération en cours (DFS)...")
    maze.generate_dfs(0, 0, set())
    
    # 3. Résolution
    print("Calcul du chemin le plus court (BFS)...")
    path = maze.solve_bfs((0, 0), (WIDTH - 1, HEIGHT - 1))
    
    # 4. Affichage
    render_maze(maze, path)
