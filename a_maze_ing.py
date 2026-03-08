from sys import argv
from typing import Dict, Any, List

# On importe les outils depuis le dossier mazegen
from mazegen import LabyrinthBuilder
from mazegen import load_maze_config

if __name__ == "__main__":
    if len(argv) != 2:
        print("Usage: python a_maze_ing.py <config_file>")
        exit(1)
        
    R: bool = False
    
    try:
        config: Dict[str, Any] = load_maze_config(argv[1])  # <-- Le bon nom !
    except ValueError as ve:
        print(f"A_MAZE_ING: Config file error: {ve}")
        exit(1)
    except Exception as e:
        print(f"A_MAZE_ING: An error occurred: {e}")
        exit(1)

    try:
        # Lancement de la nouvelle classe LabyrinthBuilder avec le dico du peer
        builder = LabyrinthBuilder(config, True)
        
        choices: List[str] = ["1", "2", "3", "4"]
        i: str = "1"
        f: bool = True
        
        while i != "4":
            print("=== A-MAZE-ING ===")
            print("1 - Re-generate a new maze")
            print("2 - Show/hide path from entry to exit")
            print("3 - Change maze colors randomly") # <-- On a changé le texte du menu
            print("4 - Quit")
            i = input("choice? (1-4): ")
            
            while i not in choices:
                print("invalid choice")
                i = input("choice? (1-4): ")
                
            if i == "1":
                LabyrinthBuilder.wipe_screen()
                builder = LabyrinthBuilder(config, True)
                
            if i == "2":
                f = not f
                builder.wipe_screen()
                if f:
                    builder.render_grid(False, builder.solution_coords)
                else:
                    builder.render_grid(False)
                    
            if i == "3":
                builder.wipe_screen()
                # On envoie True au premier paramètre pour dire "Tire une nouvelle couleur !"
                if f:
                    builder.render_grid(True, builder.solution_coords)
                else:
                    builder.render_grid(True)
                    
    except Exception as e:
        print(f"A_MAZE_ING: an error occurred: {e}")
        exit(1)