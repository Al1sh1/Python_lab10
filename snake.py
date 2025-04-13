import pygame
import random
import sys
import time
import json
import os

pygame.init()

# Настройки
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
FPS = 30

# Цвета
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Настройка экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake")

# Характеристики змеи
SNAKE_SIZE = 10
SNAKE_SPEED = 10

# Время игры
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.SysFont("Comicsans", 24)
font_small = pygame.font.SysFont("Comicsans", 16)

# Определение уровней
LEVELS = {
    1: {"speed": 10, "walls": [], "food_timeout": 5},  # Уровень 1: базовый
    2: {"speed": 13, "walls": [(100, 100), (100, 110), (100, 120)], "food_timeout": 4},  # Уровень 2: стены
    3: {"speed": 16, "walls": [(200, 200), (200, 210), (210, 200), (210, 210)], "food_timeout": 3}  # Уровень 3: больше стен, быстрее
}

# Класс для управления данными пользователя (без базы данных)
class UserData:
    def __init__(self, username):
        self.username = username
        self.current_level = 1
        self.state_file = "game_state.json"
        # Загружаем сохраненное состояние, если есть
        self.load_user_level()

    def load_user_level(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    if data.get("username") == self.username:
                        self.current_level = data.get("current_level", 1)
            except Exception as e:
                print(f"Ошибка загрузки уровня: {e}")

    def save_user_level(self, level):
        self.current_level = level
        try:
            with open(self.state_file, 'w') as f:
                json.dump({"username": self.username, "current_level": level}, f)
        except Exception as e:
            print(f"Ошибка сохранения уровня: {e}")

    def save_game_state(self, score, level, snake_body, snake_direction, food_x, food_y, food_weight, food_timer, speed):
        try:
            state = {
                "username": self.username,
                "score": score,
                "level": level,
                "snake_body": snake_body,
                "snake_direction": snake_direction,
                "food_x": food_x,
                "food_y": food_y,
                "food_weight": food_weight,
                "food_timer": food_timer,
                "speed": speed
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Ошибка сохранения состояния игры: {e}")

    def load_game_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    if state.get("username") == self.username:
                        return state
            except Exception as e:
                print(f"Ошибка загрузки состояния игры: {e}")
        return None

# Функции игры
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)

def generate_food(snake_body, walls):
    food_x = random.randint(0, (SCREEN_WIDTH - SNAKE_SIZE) // SNAKE_SIZE) * SNAKE_SIZE
    food_y = random.randint(0, (SCREEN_HEIGHT - SNAKE_SIZE) // SNAKE_SIZE) * SNAKE_SIZE
    while (food_x, food_y) in snake_body or (food_x, food_y) in walls:
        food_x = random.randint(0, (SCREEN_WIDTH - SNAKE_SIZE) // SNAKE_SIZE) * SNAKE_SIZE
        food_y = random.randint(0, (SCREEN_HEIGHT - SNAKE_SIZE) // SNAKE_SIZE) * SNAKE_SIZE
    food_weight = random.randint(1, 5)
    food_timer = time.time()
    return food_x, food_y, food_weight, food_timer

def get_username():
    username = ""
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username:
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode

        screen.fill(BLACK)
        draw_text("Enter your username:", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        draw_text(username, font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.display.update()

    return username

def game_loop(user_data, load_state=None):
    # Загрузка состояния, если есть
    if load_state:
        score = load_state["score"]
        level = load_state["level"]
        snake_body = load_state["snake_body"]
        snake_direction = load_state["snake_direction"]
        food_x = load_state["food_x"]
        food_y = load_state["food_y"]
        food_weight = load_state["food_weight"]
        food_timer = load_state["food_timer"]
        speed = load_state["speed"]
    else:
        # Исходное положение змеи
        snake_x = SCREEN_WIDTH // 2
        snake_y = SCREEN_HEIGHT // 2
        snake_body = [(snake_x, snake_y)]
        snake_direction = "RIGHT"
        food_x, food_y, food_weight, food_timer = generate_food(snake_body, LEVELS[user_data.current_level]["walls"])
        score = 0
        level = user_data.current_level
        speed = LEVELS[level]["speed"]

    running = True
    paused = False

    while running:
        clock.tick(speed)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Пауза и сохранение при нажатии P
                    paused = not paused
                    if paused:
                        user_data.save_game_state(score, level, snake_body, snake_direction, food_x, food_y, food_weight, food_timer, speed)
                        screen.fill(BLACK)
                        draw_text("Paused", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                        draw_text("Press P to resume", font_small, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)
                        pygame.display.update()
                if not paused:
                    if event.key == pygame.K_LEFT and snake_direction != "RIGHT":
                        snake_direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and snake_direction != "LEFT":
                        snake_direction = "RIGHT"
                    elif event.key == pygame.K_UP and snake_direction != "DOWN":
                        snake_direction = "UP"
                    elif event.key == pygame.K_DOWN and snake_direction != "UP":
                        snake_direction = "DOWN"

        if paused:
            continue

        # Движение змеи
        snake_x, snake_y = snake_body[0]
        if snake_direction == "LEFT":
            snake_x -= SNAKE_SIZE
        elif snake_direction == "RIGHT":
            snake_x += SNAKE_SIZE
        elif snake_direction == "UP":
            snake_y -= SNAKE_SIZE
        elif snake_direction == "DOWN":
            snake_y += SNAKE_SIZE

        new_head = (snake_x, snake_y)
        snake_body.insert(0, new_head)

        # Проверка на столкновение с едой
        if snake_x == food_x and snake_y == food_y:
            score += food_weight
            if score >= level * 10:  # Переход на следующий уровень каждые 10 очков
                level = min(level + 1, len(LEVELS))  # Не превышаем максимальный уровень
                speed = LEVELS[level]["speed"]
                user_data.save_user_level(level)
            food_x, food_y, food_weight, food_timer = generate_food(snake_body, LEVELS[level]["walls"])
        else:
            snake_body.pop()

        # Проверка столкновений
        if (snake_x < 0 or snake_x >= SCREEN_WIDTH or snake_y < 0 or snake_y >= SCREEN_HEIGHT or
            (snake_x, snake_y) in snake_body[1:] or (snake_x, snake_y) in LEVELS[level]["walls"]):
            running = False

        # Проверка таймера еды
        if time.time() - food_timer > LEVELS[level]["food_timeout"]:
            food_x, food_y, food_weight, food_timer = generate_food(snake_body, LEVELS[level]["walls"])

        # Отрисовка
        screen.fill(BLACK)
        for segment in snake_body:
            pygame.draw.rect(screen, GREEN, pygame.Rect(segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE))
        pygame.draw.rect(screen, RED, pygame.Rect(food_x, food_y, SNAKE_SIZE, SNAKE_SIZE))
        for wall in LEVELS[level]["walls"]:
            pygame.draw.rect(screen, BLUE, pygame.Rect(wall[0], wall[1], SNAKE_SIZE, SNAKE_SIZE))
        draw_text(f"Score: {score}", font, WHITE, screen, 70, 20)
        draw_text(f"Level: {level}", font, WHITE, screen, SCREEN_WIDTH - 70, 20)
        draw_text("Press P to pause", font_small, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)
        pygame.display.update()

    # Конец игры
    screen.fill(BLACK)
    draw_text("GAME OVER", font, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    draw_text(f"Final Score: {score}", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text("Press Q to Quit or R to Restart", font_small, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    game_loop(user_data)

# Старт игры
if __name__ == "__main__":
    username = get_username()
    user_data = UserData(username)
    
    screen.fill(BLACK)
    draw_text(f"Welcome, {username}!", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    draw_text(f"Current Level: {user_data.current_level}", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text("Press any key to start", font_small, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

    # Проверяем, есть ли сохраненное состояние
    saved_state = user_data.load_game_state()
    if saved_state:
        screen.fill(BLACK)
        draw_text("Saved game found!", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        draw_text("Press S to load saved game", font_small, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text("Press N for new game", font_small, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)
        pygame.display.update()

        loading = True
        while loading:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        game_loop(user_data, saved_state)
                        loading = False
                    elif event.key == pygame.K_n:
                        game_loop(user_data)
                        loading = False
    else:
        game_loop(user_data)