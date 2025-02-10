# AI.py
import neat
import os
import pickle
import pygame
import multiprocessing
from typing import Tuple, Optional, List
from game import GameConfig, Item, Bomb, Fruit, Game

class ParallelEvaluator:
    def __init__(self, num_workers: int, eval_function):
        self.num_workers = num_workers
        self.eval_function = eval_function
        self.pool = multiprocessing.Pool(num_workers)

    def evaluate(self, genomes, config):
        jobs = []
        for genome_id, genome in genomes:
            jobs.append((genome_id, genome))

        results = self.pool.starmap(self.eval_function, [(genome, config) for _, genome in jobs])
        
        for (genome_id, genome), fitness in zip(jobs, results):
            genome.fitness = fitness

class NEATHandler:
    """Handles NEAT AI implementation with parallel processing"""
    def __init__(self, config_path: str):
        self.config = neat.Config(
            neat.DefaultGenome, neat.DefaultReproduction,
            neat.DefaultSpeciesSet, neat.DefaultStagnation,
            config_path
        )
        
    @staticmethod
    def eval_genome_parallel(genome: neat.DefaultGenome, config: neat.Config) -> float:
        """Evaluate a single genome"""
        pygame.init()
        game = Game()  # Create new game instance for each process
        
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game_state = game.get_game_state()
        fruits_img, bomb_img = game.get_assets()
        fitness = 0
        
        max_steps = 2000  # Limit evaluation time
        step_count = 0
        
        while step_count < max_steps:
            step_count += 1
            
            game_state.fruit_spawn_timer += 16  # Approximate for 60 FPS
            
            if game_state.fruit_spawn_timer >= game_state.fruit_spawn_rate:
                game_state.items.append(
                    game_state.spawn_item(fruits_img, bomb_img))
                game_state.fruit_spawn_timer = 0
            
            # Get nearest items
            nearest_fruit, nearest_bomb = game_state.get_nearest_items()
            
            # Calculate normalized inputs
            max_dist = (GameConfig.WIDTH ** 2 + GameConfig.HEIGHT ** 2) ** 0.5
            
            def normalize_item_data(item: Optional[Item], max_dist: float) -> tuple:
                if not item:
                    return 0, 0, 0, 0
                dist = ((item.x - game_state.player.x) ** 2 + 
                       (item.y - game_state.player.y) ** 2) ** 0.5
                return (item.x / GameConfig.WIDTH,
                       item.y / GameConfig.HEIGHT,
                       dist / max_dist,
                       item.y_vel / 10)
            
            fruit_data = normalize_item_data(nearest_fruit, max_dist)
            bomb_data = normalize_item_data(nearest_bomb, max_dist)
            
            network_inputs = (game_state.player.x / GameConfig.WIDTH,) + fruit_data + bomb_data
            
            # Get AI's decision
            move_decision, action_decision = net.activate(network_inputs)
            
            if action_decision > 0.5:
                game_state.player.move(move_decision >= 0.5)
            
            fitness += 0.1
            
            # Update items and check collisions
            for item in game_state.items[:]:
                item.move()
                if item.y > GameConfig.HEIGHT:
                    game_state.items.remove(item)
                elif item.collides_with(game_state.player):
                    if isinstance(item, Bomb):
                        fitness -= Bomb.FITNESS_PENALTY
                        pygame.quit()
                        return fitness
                    game_state.items.remove(item)
                    fitness += Fruit.FITNESS_REWARD
        
        pygame.quit()
        return fitness

    def train(self, checkpoint_file: Optional[str] = None):
        if checkpoint_file and os.path.isfile(checkpoint_file):
            print(f"Restoring checkpoint: {checkpoint_file}")
            population = neat.Checkpointer.restore_checkpoint(checkpoint_file)
        else:
            print("Starting new population")
            population = neat.Population(self.config)
        
        # Set up parallel evaluation
        num_workers = multiprocessing.cpu_count() - 1  # Leave one CPU core free
        evaluator = ParallelEvaluator(num_workers, self.eval_genome_parallel)
        
        # Add reporters
        population.add_reporter(neat.StdOutReporter(True))
        population.add_reporter(neat.StatisticsReporter())
        population.add_reporter(neat.Checkpointer(10))
        
        # Run training with parallel evaluation
        winner = population.run(evaluator.evaluate, 50)
        
        # Save the winner
        with open('winner.pkl', 'wb') as f:
            pickle.dump(winner, f)
        
        return winner

    def play_winner(self, winner_path: str):
        """Play the game with the winner genome"""
        game = Game()
        with open(winner_path, 'rb') as f:
            winner = pickle.load(f)
        
        net = neat.nn.FeedForwardNetwork.create(winner, self.config)
        game_state = game.get_game_state()
        fruits_img, bomb_img = game.get_assets()
        
        while True:
            dt = game.clock.tick(GameConfig.FPS)
            game_state.fruit_spawn_timer += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            if game_state.fruit_spawn_timer >= game_state.fruit_spawn_rate:
                game_state.items.append(
                    game_state.spawn_item(fruits_img, bomb_img))
                game_state.fruit_spawn_timer = 0
            
            # Get AI's decision using the same logic as in training
            nearest_fruit, nearest_bomb = game_state.get_nearest_items()
            max_dist = (GameConfig.WIDTH ** 2 + GameConfig.HEIGHT ** 2) ** 0.5
            
            def normalize_item_data(item: Optional[Item], max_dist: float) -> tuple:
                if not item:
                    return 0, 0, 0, 0
                dist = ((item.x - game_state.player.x) ** 2 + 
                       (item.y - game_state.player.y) ** 2) ** 0.5
                return (item.x / GameConfig.WIDTH,
                       item.y / GameConfig.HEIGHT,
                       dist / max_dist,
                       item.y_vel / 10)
            
            fruit_data = normalize_item_data(nearest_fruit, max_dist)
            bomb_data = normalize_item_data(nearest_bomb, max_dist)
            
            network_inputs = (game_state.player.x / GameConfig.WIDTH,) + fruit_data + bomb_data
            move_decision, action_decision = net.activate(network_inputs)
            
            if action_decision > 0.5:
                game_state.player.move(move_decision >= 0.5)
            
            # Update game state
            for item in game_state.items[:]:
                item.move()
                if item.y > GameConfig.HEIGHT:
                    game_state.items.remove(item)
                elif item.collides_with(game_state.player):
                    if isinstance(item, Bomb):
                        pygame.quit()
                        return
                    game_state.items.remove(item)
                    game_state.score += Fruit.SCORE_VALUE
            
            game.draw()