import pygame
import random
import time

# всякое для игры
WIDTH = 960
HEIGHT = 540
FPS = 180
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_BLUE = (6, 7, 15)
SUMM = 5

# инициализация игры
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Blaster")
clock = pygame.time.Clock()

# Player (зеленый прямоугольник)
player_rect = pygame.Rect(WIDTH // 4, HEIGHT - 270, 50, 50)

# Enemies (красные квадраты)
enemies = []

# враги, движение влево
for i in range(5):  # создадим 5 врагов
    enemy_rect = pygame.Rect(WIDTH - random.randint(50, 150), random.randint(50, HEIGHT - 50), 40, 40)
    enemies.append({'rect': enemy_rect, 'time_collided': None, 'collision_timer': 3})  # добавляем таймер

# стенка (вертикальная)
wall_rect = pygame.Rect(WIDTH // 2, 0, 20, HEIGHT)

# Переменная для видимости стенки
wall_visible = True

# снаряды Player
bullets = []
BULLET_SPEED = 5

# количество жизней Player
lives = 3

# cостояние игры (True=основной экран, False=пауза)
game_active = True

# Размер для спрайта жизни
life_icon_width = 30
life_icon_height = 30
# время через которое Enemy is removed после столкновения со стенкой (сек)
COLLISION_TIME = 3


def show_message_with_buttons(screen, message, button_text, button_action, color, position, font_size=40):
    """Отображает сообщение с кнопкой."""
    font = pygame.font.Font(None, font_size)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(text, text_rect)

    # Создаем кнопку
    button_width, button_height = 200, 50
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT // 2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    pygame.draw.rect(screen, BLUE, button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 3)

    # Отображаем текст на кнопке
    button_font = pygame.font.Font(None, 30)
    button_text_render = button_font.render(button_text, True, WHITE)
    button_text_rect = button_text_render.get_rect(center=button_rect.center)
    screen.blit(button_text_render, button_text_rect)

    return button_rect


running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_active = not game_active
            if event.key == pygame.K_SPACE and game_active:
                bullet_rect = pygame.Rect(player_rect.right, player_rect.centery - 5, 20, 10)
                bullets.append(bullet_rect)

    if game_active:
        # update Enemy (движутся right to left)
        for enemy in enemies[:]:
            enemy_rect = enemy['rect']
            enemy_speed = random.uniform(0.5, 1.0)  # случайная скорость врагов от 0.5 до 1.0

            # check не столкнулся ли Enemy со стенкой
            if enemy_rect.colliderect(wall_rect) and wall_visible:
                # если Enemy столкнулся с стенкой, начинаем отсчет
                if enemy['time_collided'] is None:  # check было или нет уже столкновения
                    enemy['time_collided'] = time.time()  # write время столкновения

            # if Enemy столкнулся со стенкой и прошло достаточно времени, remove
            if enemy['time_collided'] is not None:
                # upd таймер для Enemy
                elapsed_time = time.time() - enemy['time_collided']
                remaining_time = COLLISION_TIME - elapsed_time
                enemy['collision_timer'] = max(0, remaining_time)  # время до remove Enemy

                # if прошло больше времени, чем COLLISION_TIME, снимаем жизнь и remove Enemy
                if elapsed_time > COLLISION_TIME:
                    if lives > 0:
                        lives -= 1  # снимаем жизнь
                    enemies.remove(enemy)  # remove врага

            # враг двигается влево с плавной скоростью, если не столкнулся со стенкой
            if enemy_rect.colliderect(wall_rect) and wall_visible:
                enemy_rect.x += 1  # если враг столкнулся с стенкой, не двигается дальше
            else:
                enemy_rect.x -= enemy_speed  # враг двигается влево

            # если враг выходит за экран, возвращаем его в правую часть
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

        # ограничение Player
        if player_rect.right > WIDTH:
            player_rect.right = WIDTH
        if player_rect.left < 0:
            player_rect.left = 0
        if player_rect.bottom > HEIGHT:
            player_rect.bottom = HEIGHT
        if player_rect.top < 0:
            player_rect.top = 0

        # обновляем пули
        for bullet in bullets[:]:
            bullet.x += BULLET_SPEED
            if bullet.left > WIDTH:  # удаляем пули, которые вышли за экран
                bullets.remove(bullet)

        # проверка столкновений пуль с врагами
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.colliderect(enemy['rect']):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    SUMM -= 1
                    print(SUMM)
                    break

        # Заполняем экран фоном
        screen.fill(DARK_BLUE)

        # Проверка условий выигрыша или проигрыша
        if SUMM == 1:  # Условие выигрыша
            screen.fill(BLACK)
            next_level_button = show_message_with_buttons(screen, 'YOU WIN!', 'Next Level', 'next', WHITE,
                                                          (WIDTH // 2, HEIGHT // 3))
            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting = False
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if next_level_button.collidepoint(event.pos):
                            SUMM = 5
                            enemies.clear()
                            for i in range(5):
                                enemy_rect = pygame.Rect(WIDTH - random.randint(50, 150),
                                                         random.randint(50, HEIGHT - 50), 40, 40)
                                enemies.append({'rect': enemy_rect, 'time_collided': None, 'collision_timer': 3})
                            waiting = False

        if lives <= 0:  # Условие проигрыша
            screen.fill(BLACK)
            try_again_button = show_message_with_buttons(screen, 'YOU LOSE!', 'Try Again', 'retry', WHITE,
                                                         (WIDTH // 2, HEIGHT // 3))
            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting = False
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if try_again_button.collidepoint(event.pos):
                            lives = 3
                            SUMM = 5
                            bullets.clear()
                            enemies.clear()
                            for i in range(5):
                                enemy_rect = pygame.Rect(WIDTH - random.randint(50, 150),
                                                         random.randint(50, HEIGHT - 50), 40, 40)
                                enemies.append({'rect': enemy_rect, 'time_collided': None, 'collision_timer': 3})
                            waiting = False

        # Рисуем игрока (зеленый квадрат)
        pygame.draw.rect(screen, GREEN, player_rect)
        # Рисуем врагов (красные квадраты)
        for enemy in enemies:
            pygame.draw.rect(screen, RED, enemy['rect'])

            # таймер отображаемый для Enemy
            font = pygame.font.Font(None, 30)
            timer_text = font.render(f"{int(enemy['collision_timer'])}", True, WHITE)
            screen.blit(timer_text, (enemy['rect'].x + 10, enemy['rect'].y - 20))

        # Рисуем снаряды (желтые прямоугольники)
        for bullet in bullets:
            pygame.draw.rect(screen, YELLOW, bullet)
        pygame.draw.rect(screen, YELLOW, wall_rect)

        # отображение жизней
        for i in range(lives):
            pygame.draw.rect(screen, GREEN,
                             pygame.Rect(10 + i * (life_icon_width + 5), 10, life_icon_width, life_icon_height))

    else:
        # если игра на паузе
        screen.fill(BLACK)
        font = pygame.font.Font(None, 40)
        text = font.render('PAUSED - Press Esc to resume', True, WHITE)
        screen.blit(text, (WIDTH // 3.4, HEIGHT // 2.2))

    pygame.display.flip()

pygame.quit()
