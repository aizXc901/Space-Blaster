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


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(self.image, GREEN, (0, 0, 50, 50), 2)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 4
        self.rect.bottom = HEIGHT - 270
        self.speedx = 0
        self.speedy = 0
# движение игрока (стрелочки)
    def update(self):
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -4
        if keystate[pygame.K_RIGHT]:
            self.speedx = 4
        if keystate[pygame.K_UP]:
            self.speedy = -4
        if keystate[pygame.K_DOWN]:
            self.speedy = 4

        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # Сохраняем игрока на экране
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# enemy (пока неподвижен)
rectangle_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.rect(rectangle_surface, RED, (0, 0, 40, 40), 2)
rectangle = pygame.Rect(WIDTH // 2, HEIGHT // 2, 2, 2)

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    all_sprites.update()
    screen.fill(DARK_BLUE)
    all_sprites.draw(screen)
    screen.blit(rectangle_surface, rectangle)
    pygame.display.flip()

pygame.quit()
