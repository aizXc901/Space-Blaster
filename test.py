import pygame
from pygame.locals import *

pygame.init()
pygame.font.init()

import pygame
from pygame.locals import *

pygame.init()
pygame.font.init()

# Настройки экрана
WINDOW_SIZE = (1000, 480)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Space Blaster")

# Путь к файлу шрифта
FONT_FILEPATH = r'C:\\Users\\maria\\PycharmProjects\\Space-Blaster\\sprites\\Font\\00218_5X5-B___.ttf'

# Загрузка шрифта из файла
my_font = pygame.font.Font(FONT_FILEPATH, 50)

# Текст для отображения
text = 'YOU PASSED WAVE 1'

# Получение изображения текста
text_surface = my_font.render(text, True, (255, 255, 255))

# Вывод текста на экран
screen.blit(text_surface, (200, 200))

# Обновление экрана
pygame.display.update()

# Основной цикл игры
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    pygame.display.update()