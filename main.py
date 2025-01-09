import pygame
import random

# всякое для игры
WIDTH = 960
HEIGHT = 540
FPS = 200
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_BLUE = (6, 7, 15)

# инициализация игры
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Blaster")
clock = pygame.time.Clock()

# Игрок (зеленый прямоугольник)
player_rect = pygame.Rect(WIDTH // 4, HEIGHT - 270, 50, 50)

# Враги (красные квадраты)
enemies = []

# враги, движение влево
for i in range(5):  # создадим 5 врагов
    enemy_rect = pygame.Rect(WIDTH - random.randint(50, 150), random.randint(50, HEIGHT - 50), 40, 40)
    enemies.append(enemy_rect)

# стенка (верт)
wall_rect = pygame.Rect(WIDTH // 2, 0, 20, HEIGHT)
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # update враги (движутся по гориз, right to left)
    for enemy_rect in enemies:
        enemy_rect.x -= random.randint(1, 2)
        # if враг выходит за пределы экрана возврат в правую часть
        if enemy_rect.right < 0:
            enemy_rect.left = WIDTH

    # клавиши
    keystate = pygame.key.get_pressed()
    # Управление игроком (стрелочки)
    player_speed = 4
    if keystate[pygame.K_LEFT]:
        player_rect.x -= player_speed
    if keystate[pygame.K_RIGHT]:
        player_rect.x += player_speed
    if keystate[pygame.K_UP]:
        player_rect.y -= player_speed
    if keystate[pygame.K_DOWN]:
        player_rect.y += player_speed
    # Ограничение движения игрока на экране
    if player_rect.right > WIDTH:
        player_rect.right = WIDTH
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.bottom > HEIGHT:
        player_rect.bottom = HEIGHT
    if player_rect.top < 0:
        player_rect.top = 0
    # Заполняем экран фоном
    screen.fill(DARK_BLUE)
    # Рисуем игрока (зеленый квадрат)
    pygame.draw.rect(screen, GREEN, player_rect)
    # Рисуем врагов (красные квадраты)
    for enemy_rect in enemies:
        pygame.draw.rect(screen, RED, enemy_rect)
    # divider
    pygame.draw.rect(screen, YELLOW, wall_rect)
    pygame.display.flip()
pygame.quit()
