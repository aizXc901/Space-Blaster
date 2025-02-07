import pygame
import random
import time
import sqlite3

# Всякое для игры
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
COLLISION_TIME = 3  # Время, которое враг проводит у стенки перед удалением
BULLET_SPEED = 5  # Скорость пуль
show_kills = True  # Флаг для отображения количества убийств
wall_visible = True  # Флаг для отображения стенки

# Инициализация игры
pygame.init()
pygame.mixer.init()

# Инициализация шрифтов
pygame.font.init()

# Проверка, что шрифты инициализированы
if not pygame.font.get_init():
    raise RuntimeError("Шрифты не инициализированы")

# Создание экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Blaster")
clock = pygame.time.Clock()

# Подключение к базе данных SQLite
conn = sqlite3.connect('records.db')
cursor = conn.cursor()

# Создание таблицы для хранения рекордов
cursor.execute('''
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    score INTEGER NOT NULL
)
''')
conn.commit()

# Состояние игры (True=основной экран, False=пауза)
game_active = True

# Таймер для появления новых врагов
last_enemy_spawn_time = time.time()
enemy_spawn_interval = random.uniform(4, 5)  # интервал от 4 до 5 секунд для появления новых врагов

# Стенка (вертикальная)
wall_rect = pygame.Rect(WIDTH // 2, 0, 20, HEIGHT)

# Размер для спрайта жизни
life_icon_width = 30  # Добавляем определение переменной
life_icon_height = 30  # Добавляем определение переменной

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

def reset_game():
    """Сброс всех переменных для начала новой игры."""
    global player_rect, enemies, bullets, lives, enemies_killed, last_enemy_spawn_time, SUMM
    player_rect = pygame.Rect(WIDTH // 4, HEIGHT - 270, 50, 50)
    enemies = []
    bullets = []
    lives = 3
    enemies_killed = 0
    last_enemy_spawn_time = time.time()
    SUMM = 5

def save_record(player_name, score):
    """Сохраняет рекорд игрока в базу данных."""
    cursor.execute('INSERT INTO records (player_name, score) VALUES (?, ?)', (player_name, score))
    conn.commit()

def show_high_scores(screen):
    """Отображает таблицу рекордов."""
    screen.fill(BLACK)
    font = pygame.font.Font(None, 40)
    title_text = font.render('High Scores', True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - 100, 50))

    # Получаем рекорды из базы данных
    cursor.execute('SELECT player_name, score FROM records ORDER BY score DESC LIMIT 10')
    records = cursor.fetchall()

    # Отображаем рекорды
    y_offset = 150
    for idx, (name, score) in enumerate(records):
        record_text = font.render(f"{idx + 1}. {name}: {score}", True, WHITE)
        screen.blit(record_text, (WIDTH // 2 - 100, y_offset))
        y_offset += 50

    # Кнопка возврата в меню
    back_button = show_message_with_buttons(screen, '', 'Back', 'back', WHITE, (WIDTH // 2, HEIGHT - 100))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.collidepoint(event.pos):
                    waiting = False

def get_player_name(screen):
    """Получает имя игрока через текстовый ввод."""
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)  # сдвигаем поле ввода
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    font = pygame.font.Font(None, 32)
    done = False

    # Отображаем надпись "Please enter your username" по центру
    font_message = pygame.font.Font(None, 40)
    message_text = font_message.render("Please enter your username", True, WHITE)
    message_text_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))  # Центрируем надпись
    screen.blit(message_text, message_text_rect)  # Отображаем текст

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(BLACK)
        # Отображаем надпись снова, чтобы она не исчезала
        screen.blit(message_text, message_text_rect)

        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()
        clock.tick(30)

    return text

def show_final_stats(screen, player_name, kills):
    """Отображает финальную статистику (ник и количество убийств)."""
    screen.fill(BLACK)
    font = pygame.font.Font(None, 40)
    stats_text = font.render(f"Player: {player_name}, Kills: {kills}", True, WHITE)
    screen.blit(stats_text, (WIDTH // 2 - 150, HEIGHT // 2))
    pygame.display.flip()
    time.sleep(3)  # Показываем статистику 3 секунды
    screen.fill(BLACK)
    pygame.display.flip()

# Основной игровой цикл
running = True

# Запрос ника игрока в начале игры
player_name = get_player_name(screen)
if not player_name:
    running = False  # Если игрок не ввел имя, завершаем игру

# Инициализация игровых объектов
player_rect = pygame.Rect(WIDTH // 4, HEIGHT - 270, 50, 50)
enemies = []
bullets = []
lives = 3
enemies_killed = 0

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
        # Таймер для появления врагов
        current_time = time.time()

        # Если прошло достаточно времени, создаем врагов
        if current_time - last_enemy_spawn_time >= enemy_spawn_interval:
            # Создаем 2-3 врагов
            number_of_enemies_to_spawn = random.randint(2, 3)
            for _ in range(number_of_enemies_to_spawn):
                enemy_rect = pygame.Rect(WIDTH - random.randint(50, 150), random.randint(50, HEIGHT - 50), 40, 40)
                enemies.append({'rect': enemy_rect, 'time_collided': None, 'collision_timer': 3})

            # Обновляем время последнего появления врага
            last_enemy_spawn_time = current_time

            # Обновляем интервал между появлениями
            enemy_spawn_interval = random.uniform(4, 5)  # случайный интервал от 4 до 5 секунд

        # update Enemy (движутся right to left)
        for enemy in enemies[:]:
            enemy_rect = enemy['rect']
            enemy_speed = 0.525  # случайная скорость врагов от 0.5 до 1.0

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
        player_speed = 3
        if keystate[pygame.K_LEFT]:
            player_rect.x -= player_speed
        if keystate[pygame.K_RIGHT]:
            # Проверка, если игрок не должен пройти через стенку
            if player_rect.right < wall_rect.left:
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
                    enemies_killed += 1  # Увеличиваем счетчик убитых врагов
                    print(SUMM)
                    break

        # Заполняем экран фоном
        screen.fill(DARK_BLUE)

        # Проверка условий выигрыша или проигрыша
        if enemies_killed == 9:  # Условие выигрыша
            screen.fill(BLACK)
            if player_name:
                save_record(player_name, enemies_killed)
            show_final_stats(screen, player_name, enemies_killed)  # Показываем финальную статистику
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
                            reset_game()  # Сбрасываем игру
                            waiting = False

        if lives <= 0:  # Условие проигрыша
            screen.fill(BLACK)
            if player_name:
                save_record(player_name, enemies_killed)
            show_final_stats(screen, player_name, enemies_killed)  # Показываем финальную статистику
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
                            reset_game()  # Сбрасываем игру
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

        # Отображение счета убитых врагов (если включен флаг)
        if show_kills:
            font = pygame.font.Font(None, 40)
            kills_text = font.render(f"Kills: {enemies_killed}", True, WHITE)
            screen.blit(kills_text, (WIDTH // 2 - 100, 10))

    else:
        # если игра на паузе
        screen.fill(BLACK)
        font = pygame.font.Font(None, 40)
        text = font.render('PAUSED - Press Esc to resume', True, WHITE)
        screen.blit(text, (WIDTH // 3.4, HEIGHT // 2.2))

    pygame.display.flip()

# Закрываем соединение с базой данных
conn.close()
pygame.quit()
