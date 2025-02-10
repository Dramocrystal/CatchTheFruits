import pygame
import random
from typing import List, Tuple, Optional

class GameConfig:
    """Game configuration constants"""
    WIDTH = 800
    HEIGHT = 600
    FPS = 60
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    PLAYER_SIZE = (100, 100)
    ITEM_SIZE = (30, 30)

class AssetLoader:
    """Handles loading and scaling of game assets"""
    @staticmethod
    def load_and_scale(path: str, size: Tuple[int, int]) -> pygame.Surface:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    
    @staticmethod
    def load_assets():
        player_img = AssetLoader.load_and_scale('Assets/player.png', GameConfig.PLAYER_SIZE)
        bg = AssetLoader.load_and_scale('Assets/bg.png', (GameConfig.WIDTH, GameConfig.HEIGHT))
        fruits = [AssetLoader.load_and_scale(f'Assets/fruit{i}.png', GameConfig.ITEM_SIZE) 
                 for i in range(5)]
        bomb_img = AssetLoader.load_and_scale('Assets/bomb.png', GameConfig.ITEM_SIZE)
        return player_img, bg, fruits, bomb_img

class GameObject:
    """Base class for all game objects"""
    def __init__(self, x: int, y: int, width: int, height: int, image: pygame.Surface):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
    
    def draw(self, window: pygame.Surface):
        window.blit(self.image, (self.x, self.y))
    
    def collides_with(self, other: 'GameObject') -> bool:
        return (self.x < other.x + other.width and 
                self.x + self.width > other.x and
                self.y < other.y + other.height and 
                self.y + self.height > other.y)

class Player(GameObject):
    """Player character class"""
    SPEED = 10
    
    def move(self, right: bool):
        self.x += self.SPEED if right else -self.SPEED
        self.x = max(0, min(self.x, GameConfig.WIDTH - self.width))

class Item(GameObject):
    """Base class for collectable items"""
    def __init__(self, x: int, y: int, image: pygame.Surface):
        super().__init__(x, y, image.get_width(), image.get_height(), image)
        self.y_vel = random.randint(4, 10)
    
    def move(self):
        self.y += self.y_vel

class Fruit(Item):
    """Collectable fruit class"""
    SCORE_VALUE = 1
    FITNESS_REWARD = 100

class Bomb(Item):
    """Dangerous bomb class"""
    FITNESS_PENALTY = 1000

class GameState:
    """Manages the current state of the game"""
    def __init__(self, player_img: pygame.Surface):
        self.player = Player((GameConfig.WIDTH - 100) // 2, 
                           GameConfig.HEIGHT - 100, 100, 100, player_img)
        self.items: List[Item] = []
        self.score = 0
        self.fruit_spawn_timer = 0
        self.fruit_spawn_rate = 500
        
    def spawn_item(self, fruits_img: List[pygame.Surface], bomb_img: pygame.Surface):
        if random.random() < 0.8:
            return Fruit(random.randint(0, GameConfig.WIDTH - 30), 0, 
                        random.choice(fruits_img))
        return Bomb(self.player.x, 0, bomb_img)
    
    def get_nearest_items(self) -> Tuple[Optional[Item], Optional[Item]]:
        nearest_fruit = None
        nearest_bomb = None
        min_fruit_dist = float('inf')
        min_bomb_dist = float('inf')
        
        for item in self.items:
            dist = ((item.x - self.player.x) ** 2 + 
                   (item.y - self.player.y) ** 2) ** 0.5
            
            if isinstance(item, Fruit) and dist < min_fruit_dist:
                min_fruit_dist = dist
                nearest_fruit = item
            elif isinstance(item, Bomb) and dist < min_bomb_dist:
                min_bomb_dist = dist
                nearest_bomb = item
                
        return nearest_fruit, nearest_bomb

class Game:
    """Main game class"""
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((GameConfig.WIDTH, GameConfig.HEIGHT))
        pygame.display.set_caption("Catch the Fruits")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.player_img, self.bg, self.fruits_img, self.bomb_img = AssetLoader.load_assets()
        self.game_state = GameState(self.player_img)
    
    def draw(self):
        self.window.blit(self.bg, (0, 0))
        self.game_state.player.draw(self.window)
        for item in self.game_state.items:
            item.draw(self.window)
        score_text = self.font.render(f"Score: {self.game_state.score}", True, GameConfig.BLACK)
        self.window.blit(score_text, (GameConfig.WIDTH - score_text.get_width() - 10, 10))
        pygame.display.update()

    def get_game_state(self):
        return self.game_state

    def get_assets(self):
        return self.fruits_img, self.bomb_img