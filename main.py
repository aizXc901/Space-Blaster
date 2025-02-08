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
BULLET_SPEED = 5
current_wave = 1  # Первая волна
final_enemy = {'rect': pygame.Rect(WIDTH - 200, random.randint(50, HEIGHT - 50), 120, 120), 'hp': 10,
                       'speed': 1}
show_kills = True  # Флаг для отображения количества убийств
wall_visible = True  # Флаг для отображения стенки

# Загрузка спрайтов для анимации
player_sprite1 = pygame.image.load("C:\\Users\\maria\\PycharmProjects\\Space-Blaster\\sprites\\player\\sprites\\player1.png")
player_sprite2 = pygame.image.load("C:\\Users\\maria\\PycharmProjects\\Space-Blaster\\sprites\\player\\sprites\\player2.png")
player_sprite3 = pygame.image.load("C:\\Users\\maria\\PycharmProjects\\Space-Blaster\\sprites\\player\\sprites\\player3.png")

# Преобразуем их в нужный размер
player_sprite1 = pygame.transform.scale(player_sprite1, (50, 50))
player_sprite2 = pygame.transform.scale(player_sprite2, (50, 50))
player_sprite3 = pygame.transform.scale(player_sprite3, (50, 50))

# Список изображений для анимации
player_sprites = [player_sprite1, player_sprite2, player_sprite3]

# Переменные для анимации
player_animation_index = 0  # Индекс текущего спрайта
player_animation_timer = 0  # Таймер для анимации
animation_delay = 45  # Задержка между сменой спрайтов (в кадрах)

# Загрузка спрайтов для пули
bullet_sprite1 = pygame.image.load("C:\\Users\\maria\\PycharmProjects\\Space-Blaster\\sprites\\shoot\\shoot1.png")
bullet_sprite2 = pygame.image.load("C:\\Users\\maria\\PycharmProjects\\Space-Blaster\\sprites\\shoot\\shoot2.png")

# Преобразуем их в нужный размер
bullet_sprite1 = pygame.transform.scale(bullet_sprite1, (20, 10))
bullet_sprite2 = pygame.transform.scale(bullet_sprite2, (20, 10))

# Список спрайтов для анимации пули
bullet_sprites = [bullet_sprite1, bullet_sprite2]

# Загрузка спрайта для обычных врагов
enemy_sprite\
    = pygame.image.load("C:\\Users\\maria\\PycharmProjects\\Space-Blaster\\sprites\\asteroids\\asteroid-small.png")
enemy_sprite = pygame.transform.scale(enemy_sprite, (50, 50))

# Инициализация игры
pygame.init()
pygame.mixer.init()

# Инициализация шрифтов
my_font = 'C:\\Users\\maria\\PycharmProjects\\Space-Blaster\\sprites\\Font\\00218_5X5-B___.ttf'
pygame.font.Font(my_font,30)

# Создание экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Blaster")
clock = pygame.time.Clock()

# Обновление экрана
pygame.display.update()
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

def render_text(text, color=(255, 255, 255)):
    font = pygame.font.Font(my_font, 20)
    return font.render(text, True, color)

def show_message_with_buttons(screen, message, button_text, button_action, color, position, font_size=40):
    """Отображает сообщение с кнопкой."""
    text = render_text(message)
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
    button_text_render = render_text(button_text)
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

def show_game_over(screen):
    """Отображает экран GAME OVER с кнопкой Restart."""
    screen.fill(BLACK)
    font = pygame.font.Font(my_font, 72)
    text = font.render("GAME OVER", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3.2))  # Центрирование текста
    screen.blit(text, text_rect)

    # Кнопка перезапуска
    button_position = (WIDTH // 2, HEIGHT * 2 // 2.5)
    restart_button = show_message_with_buttons(screen, 'Restart', 'Restart', 'restart', WHITE, button_position)
    pygame.display.flip()

    # Ожидание нажатия кнопки
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_button.collidepoint(event.pos):
                    reset_game()  # Сбрасываем игру для новой попытки
                    waiting = False

def save_record(player_name, score):
    """Сохраняет рекорд игрока в базу данных."""
    cursor.execute('INSERT INTO records (player_name, score) VALUES (?, ?)', (player_name, score))
    conn.commit()

def show_high_scores(screen):
    """Отображает таблицу рекордов."""
    screen.fill(BLACK)
    font = pygame.font.Font(my_font, 40)
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
    back_button = show_message_with_buttons(screen, '', 'Back', 'back', WHITE,
                                            (WIDTH // 2, HEIGHT - 100))
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
    font = pygame.font.Font(my_font, 32)
    done = False

    # Отображаем надпись "please enter your username" по центру
    font_message = pygame.font.Font(my_font, 40)
    message_text = font_message.render("please enter your username", True, WHITE)
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
    font = pygame.font.Font(my_font, 30)

    # Создаем текст
    stats_text1 = font.render(f"Player {player_name}", True, WHITE)
    stats_text2 = font.render(f"Kills {kills}", True, WHITE)

    # Получаем размеры текстов
    text1_width, text1_height = stats_text1.get_size()
    text2_width, text2_height = stats_text2.get_size()

    # Центрируем тексты относительно центра экрана
    screen_center_x = WIDTH // 2
    screen_center_y = HEIGHT // 2

    # Рисуем первый текст, с учетом его ширины и высоты
    screen.blit(stats_text1, (screen_center_x - text1_width // 2, screen_center_y - text1_height // 2))

    # Рисуем второй текст с учетом его ширины и высоты, немного сдвигаем по вертикали
    screen.blit(stats_text2, (screen_center_x - text2_width // 2, screen_center_y - text2_height // 2 - 50))

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

# Отображение текущей волны
def display_wave(screen, current_wave):
    font = pygame.font.Font(my_font, 30)
    wave_text = font.render(f"WAVE {current_wave}", True, WHITE)
    screen.blit(wave_text, (WIDTH - 150, 10))  # Отображение справа

# Внесем изменения в основной игровой цикл:
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_active = not game_active
            if event.key == pygame.K_SPACE and game_active:
                new_bullet = create_bullet()  # Создание новой пули
                bullets.append(new_bullet)

    if game_active:
        # Таймер для появления врагов
        current_time = time.time()
        for bullet in bullets[:]:
            bullet['animation_timer'] += 1
            if bullet['animation_timer'] >= 5:  # Задержка между сменой спрайтов (в кадрах)
                bullet['animation_index'] = (bullet['animation_index'] + 1) % len(bullet_sprites)
                bullet['animation_timer'] = 0  # Сбрасываем таймер

            # Получаем текущий спрайт пули
            current_bullet_sprite = bullet_sprites[bullet['animation_index']]

            # Двигаем пулю
            bullet['rect'].x += BULLET_SPEED  # Изменяем x через rect
            if bullet['rect'].left > WIDTH:
                bullets.remove(bullet)  # Удаляем пулю, если она выходит за экран

            # Рисуем пулю с анимацией
            screen.blit(current_bullet_sprite, bullet['rect'])
        # Логика анимации игрока
        player_animation_timer += 1
        if player_animation_timer >= animation_delay:
            # Переход к следующему спрайту
            player_animation_index = (player_animation_index + 1) % len(player_sprites)
            player_animation_timer = 0  # Сбрасываем таймер
            # Получаем текущий спрайт игрока
        current_player_sprite = player_sprites[player_animation_index]
        # Если прошло достаточно времени, создаем врагов
        if current_time - last_enemy_spawn_time >= enemy_spawn_interval:
            # Появление врагов только на 1 и 2 волне
            if current_wave == 1 or current_wave == 2:
                # Для первой волны создаем 2-3 врагов
                if current_wave == 1:
                    number_of_enemies_to_spawn = random.randint(2, 3)
                # Для второй волны создаем от 3 до 4 врагов
                elif current_wave == 2:
                    number_of_enemies_to_spawn = random.randint(3, 4)

                for _ in range(number_of_enemies_to_spawn):
                    # Создание прямоугольника для врага
                    enemy_rect = pygame.Rect(WIDTH - random.randint(50, 150), random.randint(50, HEIGHT - 50), 40, 40)
                    # Добавление спрайта и других данных в словарь врага
                    enemy = {'rect': enemy_rect, 'sprite': enemy_sprite, 'time_collided': None, 'collision_timer': 3}
                    enemies.append(enemy)

                # Обновляем время последнего появления врага
                last_enemy_spawn_time = current_time

                # Обновляем интервал между появлениями врагов
                if current_wave == 1:
                    enemy_spawn_interval = random.uniform(4, 5)
                elif current_wave == 2:
                    enemy_spawn_interval = random.uniform(2, 3)  # Для второй волны уменьшаем интервал

        # update Enemy (движутся right to left)
        for enemy in enemies[:]:
            enemy_rect = enemy['rect']
            enemy_speed = 0.525  # случайная скорость врагов от 0.5 до 1.0

            # check не столкнулся ли Enemy со стенкой
            if enemy_rect.colliderect(wall_rect) and wall_visible:
                if 'time_collided' in enemy and enemy['time_collided'] is None:
                    enemy['time_collided'] = time.time()

            # Обработка времени столкновения врагов с стенкой
            if 'time_collided' in enemy and enemy['time_collided'] is not None:
                elapsed_time = time.time() - enemy['time_collided']
                remaining_time = COLLISION_TIME - elapsed_time
                enemy['collision_timer'] = max(0, remaining_time)  # время до удаления врага

                if elapsed_time > COLLISION_TIME:
                    if lives > 0:
                        lives -= 1
                    enemies.remove(enemy)
                elif lives == 0:
                    screen.fill(BLACK)
                    font = pygame.font.Font(my_font, 72)
                    text = font.render("GAME OVER", True, WHITE)
                    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3.2))
                    screen.blit(text, text_rect)

                    # Кнопка для перезапуска игры
                    button_position = (WIDTH // 2, HEIGHT * 2 // 2.5)
                    restart_button = show_message_with_buttons(screen, 'Restart', 'Restart', 'restart', WHITE,
                                                               button_position)
                    pygame.display.flip()

                    waiting = True
                    while waiting:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                waiting = False
                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                if restart_button.collidepoint(event.pos):
                                    reset_game()  # Сбрасываем игру для новой попытки
                                    waiting = False

            # движение врагов (и босса)
            if enemy_rect.colliderect(wall_rect) and wall_visible:
                enemy_rect.x += 1  # если враг столкнулся с стенкой, не двигается дальше
            else:
                enemy_rect.x -= enemy_speed  # враг двигается влево

            # если враг выходит за экран, возвращаем его в правую часть
            if enemy_rect.right < 0:
                enemy_rect.left = WIDTH + enemy_speed * 10  # Возвращаемся плавно, смещая чуть правее края экрана
            screen.blit(enemy_sprite, enemy_rect)
        # После проверки условий для босса
        if current_wave == 3 and final_enemy is not None and final_enemy['hp'] > 0:
            final_enemy_rect = final_enemy['rect']
            if enemy_rect.colliderect(wall_rect) and wall_visible:
                enemy_rect.x += 1  # если враг столкнулся с стенкой, не двигается дальше
            else:
                enemy_rect.x -= enemy_speed  # враг двигается влево

            # Рисуем босс (пока он один)
            pygame.draw.rect(screen, RED, final_enemy_rect)
        elif current_wave == 3:  # Если босса нет, значит игрок победил
            screen.fill(BLACK)  # Очистка экрана
            font = pygame.font.Font(my_font, 72)  # Заголовок шрифтом размером 72
            text = font.render("YOU WON", True, WHITE)  # Создаем текст "YOU WON"
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3.2))  # Центрирование текста
            screen.blit(text, text_rect)  # Отображение текста на экране

            # Определение положения кнопки
            button_position = (WIDTH // 2, HEIGHT * 2 // 2.5)
            # Вызов функции с передачей всех необходимых аргументов
            restart_button = show_message_with_buttons(screen, 'Restart', 'Restart',
                                                       'restart', WHITE, button_position)
            pygame.display.flip()  # Обновляем экран

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting = False
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if restart_button.collidepoint(event.pos):
                            reset_game()  # Сбрасываем игру для новой попытки
                            waiting = False
        # клавиши
        keystate = pygame.key.get_pressed()

        # Управление игроком (стрелочки)
        player_speed = 3
        if keystate[pygame.K_LEFT]:
            player_rect.x -= player_speed
        if keystate[pygame.K_RIGHT]:
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

        # Обновляем пули
        for bullet in bullets[:]:
            bullet['rect'].x += BULLET_SPEED  # Изменяем позицию пули через 'rect'

            if bullet['rect'].left > WIDTH:  # Удаляем пули, которые вышли за экран
                bullets.remove(bullet)

        # Проверка столкновений пуль с врагами
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet['rect'].colliderect(enemy['rect']):  # Проверяем столкновение с врагом
                    bullets.remove(bullet)  # Удаляем пулю при попадании
                    enemies.remove(enemy)  # Удаляем врага
                    SUMM -= 1  # Уменьшаем счет
                    enemies_killed += 1  # Увеличиваем счетчик убитых врагов
                    break  # Прерываем цикл, чтобы не удалять несколько врагов за один выстрел

        # Проверка столкновения пуль с боссом (в третьей волне)
        if current_wave == 3 and final_enemy is not None:
            for bullet in bullets[:]:
                if bullet['rect'].colliderect(final_enemy['rect']):  # Проверяем столкновение с боссом
                    bullets.remove(bullet)  # Удаляем пулю при попадании
                    final_enemy['hp'] -= 1  # Уменьшаем здоровье босса
                    if final_enemy['hp'] <= 0:
                        if final_enemy in enemies:
                            enemies.remove(final_enemy)  # Удаляем босса, если он погиб
                    break  # Прерываем цикл, чтобы не удалять несколько пуль за одно попадание

        # Заполняем экран фоном
        screen.fill(DARK_BLUE)
        def create_bullet():
            bullet_rect = pygame.Rect(player_rect.right, player_rect.centery - 5, 20, 10)
            return {'rect': bullet_rect, 'animation_index': 0, 'animation_timer': 0}
        # Логика движения босса
        def move_boss(final_enemy_rect, wall_rect, wall_visible, boss_speed):
            if final_enemy_rect.colliderect(wall_rect) and wall_visible:
                final_enemy_rect.x += 1  # Если он сталкивается с стеной, он не двигается дальше
            else:
                final_enemy_rect.x -= boss_speed  # Босс медленно движется влево

        # Проверка условий выигрыша или проигрыша
        if current_wave == 1 and enemies_killed == 6:  # Условие победы в первой волне
            screen.fill(BLACK)
            if player_name:
                save_record(player_name, enemies_killed)
            show_final_stats(screen, player_name, enemies_killed)  # Показываем финальную статистику

            # Переход к следующей волне
            current_wave += 1
            if current_wave == 2:
                # Условия второй волны
                enemy_spawn_interval = random.uniform(3, 4)  # Уменьшаем интервал между врагами, чтобы усложнить игру

            next_level_button = show_message_with_buttons(screen, 'YOU WIN!', 'Next Wave', 'next', WHITE,
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
                            reset_game()  # Сбрасываем игру для новой волны
                            waiting = False

        elif current_wave == 2 and enemies_killed == 12:  # Условие победы во второй волне
            screen.fill(BLACK)
            if player_name:
                save_record(player_name, enemies_killed)
            show_final_stats(screen, player_name, enemies_killed)  # Показываем финальную статистику
            # Переход к третьей, финальной волне
            current_wave += 1  # Переход к финальной волне
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting = False
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if next_level_button.collidepoint(event.pos):
                            reset_game()  # Сбрасываем игру для финальной битвы
                            waiting = False
            next_level_button = show_message_with_buttons(screen, 'YOU WIN!', 'Next Wave', 'next', WHITE,
                                                          (WIDTH // 2, HEIGHT // 3))

        elif current_wave == 3:
            screen.fill(BLACK)
            # Восстановление здоровья игрока до максимума
            lives = 3
            enemies_killed = 0
            # Удаляем всех врагов перед финальной волной
            enemies.clear()

            # Убедитесь, что финальный враг существует
            if final_enemy:
                final_enemy_rect = final_enemy['rect']
                final_enemy_rect.centery = HEIGHT // 2

                boss_speed = 1  # Устанавливаем скорость босса

                # Перемещаем босса каждый кадр
                move_boss(final_enemy_rect, wall_rect, wall_visible, boss_speed)

            # Рисуем босса
                pygame.draw.rect(screen, RED, final_enemy_rect)  # Добавляем финального врага

            # Удаление пуль при попадании
            for bullet in bullets[:]:
                if bullet['rect'].colliderect(final_enemy['rect']):
                    bullets.remove(bullet)  # Удаляем пулю при попадании
                    final_enemy['hp'] -= 1  # Уменьшаем HP босса
                    print(f"Босс получил урон! Осталось HP: {final_enemy['hp']}")  # Отладочный вывод в консоль
                    if final_enemy['hp'] <= 0:
                        final_enemy = None  # Удаляем босса
                        break

            # Отображение HP босса над ним
            if current_wave == 3 and final_enemy:
                font = pygame.font.Font(None, 30)
                hp_text = font.render(f"HP {final_enemy['hp']}", True, WHITE)
                screen.blit(hp_text,
                            (final_enemy['rect'].x + 40, final_enemy['rect'].y - 20))  # Располагаем текст над боссом

            # Логика завершения уровня
            if current_wave == 3 and not final_enemy:
                screen.fill(BLACK)
                font = pygame.font.Font(my_font, 72)  # Заголовок шрифтом размером 72
                text = font.render("YOU WON", True, WHITE)  # Создаем текст "YOU WON"
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3.2))  # Центрирование текста
                screen.blit(text, text_rect)  # Отображение текста на экране

                # Определение положения кнопки
                button_position = (WIDTH // 2, HEIGHT * 2 // 2.5)
                pygame.display.flip()

        # рисуем игрока с анимацией
        screen.blit(current_player_sprite, player_rect)  # Используем текущий спрайт игрока
        # Рисуем врагов (красные квадраты)
        for enemy in enemies:
            if 'sprite' in enemy:  # Если спрайт существует
                screen.blit(enemy['sprite'], enemy['rect'])  # Отображаем спрайт врага
            else:
                pygame.draw.rect(screen, RED, enemy['rect'])  # Временно рисуем прямоугольник, если нет спрайта

            # Таймер отображаемый для Enemy
            font = pygame.font.Font(None, 30)
            if 'collision_timer' in enemy:  # Проверяем, есть ли этот ключ у врага
                timer_text = font.render(f"{int(enemy['collision_timer'])}", True, WHITE)
                screen.blit(timer_text, (enemy['rect'].x + 10, enemy['rect'].y - 20))

        # Рисуем снаряды (желтые прямоугольники)
        for bullet in bullets:
            current_bullet_sprite = bullet_sprites[bullet['animation_index']]  # Получаем текущий спрайт пули
            screen.blit(current_bullet_sprite, bullet['rect'])

        # отображение жизней
        for i in range(lives):
            pygame.draw.rect(screen, GREEN,
                             pygame.Rect(10 + i * (life_icon_width + 5), 10, life_icon_width, life_icon_height))

        # Отображение счета убитых врагов (если включен флаг)
        if show_kills:
            font = pygame.font.Font(my_font, 30)
            kills_text = font.render(f"KILLS {enemies_killed}", True, WHITE)
            screen.blit(kills_text, (WIDTH // 2 - 75, 10))

        # Отображение текущей волны
        display_wave(screen, current_wave)
    else:
        # Если игра на паузе
        screen.fill(BLACK)
        font = pygame.font.Font(my_font, 40)
        text = font.render('PAUSED press ESC to resume', True, WHITE)

        # Получаем размеры текста
        text_rect = text.get_rect()
        text_width, text_height = text_rect.width, text_rect.height

        # Центрируем текст по горизонтали
        center_x = WIDTH // 2
        text_rect.centerx = center_x

        # Центрируем текст по вертикали
        center_y = HEIGHT // 2
        text_rect.centery = center_y

        # Рисуем текст на экране
        screen.blit(text, text_rect)

    pygame.display.flip()

# Закрываем соединение с базой данных
conn.close()
pygame.quit()
