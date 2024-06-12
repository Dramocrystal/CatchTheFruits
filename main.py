import pygame
import random

pygame.init()

# Display
WIDTH = 800
HEIGHT = 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the fruits")

FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load Images
player_img = pygame.image.load('Assets/player.png').convert_alpha()
player_img = pygame.transform.scale(player_img, (100, 100))

bg = pygame.image.load('Assets/bg.png')
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

fruits = [
    pygame.image.load('Assets/fruit0.png').convert_alpha(),
    pygame.image.load('Assets/fruit1.png').convert_alpha(),
    pygame.image.load('Assets/fruit2.png').convert_alpha(),
    pygame.image.load('Assets/fruit3.png').convert_alpha(),
    pygame.image.load('Assets/fruit4.png').convert_alpha()
]

fruits_img = [pygame.transform.scale(img, (30, 30)) for img in fruits]

bomb_img = pygame.image.load('Assets/bomb.png').convert_alpha()
bomb_img = pygame.transform.scale(bomb_img, (30, 30))

# Fonts
font = pygame.font.SysFont(None, 50)
small_font = pygame.font.SysFont(None, 30)

class Player:
    SPEED = 10

    def __init__(self, x, y, width, height, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

    def move(self, right=True):
        if right:
            self.x += self.SPEED
        else:
            self.x -= self.SPEED

class Fruit:
    

    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.width = image.get_width()
        self.height = image.get_height()
        self.y_vel = random.randint(4, 10)

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

    def move(self):
        self.y += self.y_vel

    def collision_with_player(self, player):
        if (player.x < self.x + self.width and player.x + player.width > self.x and
            player.y < self.y + self.height and player.y + player.height > self.y):
            return True
        return False

class Bomb(Fruit):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

def draw_menu(win):
    win.blit(bg, (0, 0))
    title_text = font.render("Catch the Fruits", True, BLACK)
    play_text = font.render("PLAY", True, BLACK)
    quit_text = font.render("QUIT", True, BLACK)

    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    play_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    win.blit(title_text, title_rect)
    win.blit(play_text, play_rect)
    win.blit(quit_text, quit_rect)
    pygame.display.update()

def draw_game(win, player, items, score):
    win.blit(bg, (0, 0))
    player.draw(win)
    for item in items:
        item.draw(win)
    # Draw score at the top right corner
    score_text = small_font.render("Score: " + str(score), True, BLACK)
    win.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
    pygame.display.update()

def draw_game_over(win, score):
    win.blit(bg, (0, 0))
    game_over_text = font.render("GAME OVER", True, BLACK)
    score_text = small_font.render("Final Score: " + str(score), True, BLACK)
    restart_text = font.render("RESTART", True, BLACK)
    quit_text = font.render("QUIT", True, BLACK)

    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 200))

    win.blit(game_over_text, game_over_rect)
    win.blit(score_text, score_rect)
    win.blit(restart_text, restart_rect)
    win.blit(quit_text, quit_rect)
    pygame.display.update()

def player_move(keys, player):
    # Move left
    if keys[pygame.K_a] and player.x - player.SPEED >= 0:
        player.move(right=False)
    # Move right
    if keys[pygame.K_d] and player.x + player.SPEED + player.width <= WIDTH:
        player.move(right=True)

def main():

    current_state = "MENU"  # Initial state
    player = Player((WIDTH - 100) // 2, HEIGHT - 100, 100, 100, player_img)
    items = [] 
    fruit_spawn_timer = 0 
    fruit_spawn_rate = 500
    score = 0 

    run = True
    while run:
        if current_state == "MENU":
            draw_menu(WINDOW)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    play_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 - 25, 100, 50)
                    quit_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 75, 100, 50)
                    if play_rect.collidepoint(mouse_x, mouse_y):
                        current_state = "GAME"
                        player.x = (WIDTH - player.width) // 2
                        player.y = HEIGHT - player.height
                        items.clear()
                        score = 0
                    elif quit_rect.collidepoint(mouse_x, mouse_y):
                        run = False

        elif current_state == "GAME":
            dt = pygame.time.Clock().tick(FPS)
            fruit_spawn_timer += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()
            player_move(keys, player)

            if fruit_spawn_timer >= fruit_spawn_rate: 
                if random.random() < 0.8:
                    new_item = Fruit(random.randint(0, WIDTH - 30), 0, random.choice(fruits_img))
                else:
                    new_item = Bomb(random.randint(0, WIDTH - 30), 0, bomb_img)
                items.append(new_item)
                fruit_spawn_timer = 0

            for item in items[:]: 
                item.move()
                if item.y > HEIGHT:
                    items.remove(item)
                elif isinstance(item, Bomb) and item.collision_with_player(player):
                    current_state = "GAME_OVER"
                elif isinstance(item, Fruit) and item.collision_with_player(player):
                    score += 1
                    items.remove(item)

            draw_game(WINDOW, player, items, score)

        elif current_state == "GAME_OVER":
            draw_game_over(WINDOW, score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    restart_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 75, 100, 50)
                    quit_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 175, 100, 50)
                    if restart_rect.collidepoint(mouse_x, mouse_y):
                        current_state = "GAME"
                        player.x = (WIDTH - player.width) // 2
                        player.y = HEIGHT - player.height
                        items.clear()
                        score = 0
                    elif quit_rect.collidepoint(mouse_x, mouse_y):
                        run = False

    pygame.quit()

if __name__ == '__main__':
    main()
