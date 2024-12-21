import pygame
import random
import os
import sys

# Constants for the game
WIDTH = 1000
HEIGHT = 800
FPS = 200

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialize the game
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blaster")
clock = pygame.time.Clock()


def load_image(name):
    fullname = os.path.join('sprites', name)
    if not os.path.isfile(fullname):
        print(f"Image file '{fullname}' not found.")
        sys.exit()
    return pygame.image.load(fullname)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_image = load_image("cosmo.jpg")

        # Scale the image to be half the original size
        self.image = pygame.transform.scale(original_image,
                                            (original_image.get_width() // 10, original_image.get_height() // 10))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speedx = 0
        self.speedy = 0

    def update(self):
        """Update the player's position based on input."""
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_UP]:
            self.speedy = -8
        if keystate[pygame.K_DOWN]:
            self.speedy = 8

        # Move the sprite
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # Keep player within screen limits
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT


# Main game loop
def main():
    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update()

        screen.fill(BLACK)
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
