import os
from game import Game
from AI import NEATHandler
import multiprocessing

def main():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    neat_handler = NEATHandler(config_path)
    
    print("1. Watch the winner play")
    print("2. Start from last checkpoint (if available)")
    print("3. Train a new AI")
    choice = input("Enter your choice: ")
    
    if choice == '1':
        winner_path = os.path.join(local_dir, 'winner.pkl')
        if os.path.exists(winner_path):
            neat_handler.play_winner(winner_path)
        else:
            print("No trained AI found! Train one first.")
    
    elif choice == '2':
        checkpoint_files = [f for f in os.listdir(local_dir) if f.startswith("neat-checkpoint-")]
        if checkpoint_files:
            latest_checkpoint = max(checkpoint_files, key=lambda f: int(f.split('-')[-1]))
            neat_handler.train(os.path.join(local_dir, latest_checkpoint))
        else:
            print("No checkpoint found! Starting new training session...")
            neat_handler.train()
    
    elif choice == '3':
        neat_handler.train()

if __name__ == '__main__':
    multiprocessing.freeze_support()  # Required for Windows
    main()