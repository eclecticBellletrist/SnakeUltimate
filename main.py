import pygame
import random
import time
import math
from pygame.math import Vector2
import colorsys
import config

# Инициализация Pygame
pygame.init()

# Установка размеров окна
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

# Вычисление размера одной клетки в пикселях
cell_width = config.SCREEN_WIDTH / config.FIELD_WIDTH
cell_height = config.SCREEN_HEIGHT / config.FIELD_HEIGHT
cell_size = min(cell_width, cell_height)

# Центрирование поля на экране
offset_x = (config.SCREEN_WIDTH - (cell_size * config.FIELD_WIDTH)) / 2
offset_y = (config.SCREEN_HEIGHT - (cell_size * config.FIELD_HEIGHT)) / 2

# Установка цветов
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = config.SNAKE_COLOR
GREEN = config.FOOD_COLORS['green']
YELLOW = config.FOOD_COLORS['yellow']
RED = config.FOOD_COLORS['red']
ORANGE = config.ENEMY_COLOR
GRAY = config.WALL_COLOR

# Настройки шрифта
font = pygame.font.SysFont('Arial', 20)

# Класс для игры
class SnakeGame:
    def __init__(self):
        self.field = self.create_field()
        self.snake = self.create_snake()
        self.food = []
        self.enemies = []
        self.game_over = False
        self.direction = 'RIGHT'
        self.spawn_initial_walls()
        self.spawn_food(initial=True)
        self.effects = {
            'yellow': 0,
            'red': 0,
            'white': 0
        }
        self.enemy_spawn_time = time.time()
        self.food_spawn_time = time.time()
        self.enemy_spawn_blocked_until = 0
        self.score = 0  # Переменная для отслеживания очков

        self.snake_move_time = time.time()
        self.snake_speed = 1.0 / config.SNAKE_SPEED  # время в секундах на одно перемещение змейки
        self.snake_speed_up = 1.0 / config.SNAKE_SPEED_UP  # время в секундах на одно перемещение змейки при ускорении

        self.enemy_move_times = {}  # Таймеры для движения врагов

    def create_field(self):
        return [['' for _ in range(config.FIELD_WIDTH)] for _ in range(config.FIELD_HEIGHT)]

    def create_snake(self):
        snake = [(config.FIELD_WIDTH // 2, config.FIELD_HEIGHT // 2)]
        for _ in range(config.INITIAL_SNAKE_LENGTH - 1):
            snake.append((snake[-1][0] - 1, snake[-1][1]))
        return snake

    def spawn_initial_walls(self):
        wall_choice = random.choices(
            ['none', 'horizontal', 'vertical'],
            [config.NO_WALL_PROBABILITY, config.HORIZONTAL_WALL_PROBABILITY, config.VERTICAL_WALL_PROBABILITY]
        )[0]

        if (wall_choice == 'horizontal'):
            for x in range(config.FIELD_WIDTH):
                self.field[0][x] = 'W'
                self.field[config.FIELD_HEIGHT - 1][x] = 'W'
        elif (wall_choice == 'vertical'):
            for y in range(config.FIELD_HEIGHT):
                self.field[y][0] = 'W'
                self.field[y][config.FIELD_WIDTH - 1] = 'W'

    def spawn_food(self, initial=False):
        while (len(self.food) < config.MAX_FOOD):
            x = random.randint(0, config.FIELD_WIDTH - 1)
            y = random.randint(0, config.FIELD_HEIGHT - 1)
            if (self.field[y][x] == ''):
                if (initial or len(self.food) == 0):
                    food_type = 'green'
                else:
                    food_type = random.choice([ft for ft in config.FOOD_COLORS.keys() if ft != 'green'])
                self.food.append({
                    'position': (x, y),
                    'type': food_type,
                    'spawn_time': time.time()
                })
                self.field[y][x] = 'F'
                if (not initial):
                    break

    def spawn_enemy(self):
        if (len(self.enemies) < config.MAX_ENEMIES and time.time() > self.enemy_spawn_blocked_until):
            while (True):
                x = random.randint(0, config.FIELD_WIDTH - 1)
                y = random.randint(0, config.FIELD_HEIGHT - 1)
                direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
                if (self.field[y][x] == ''):
                    self.enemies.append({
                        'position': (x, y),
                        'direction': direction,
                        'bounces': 0,
                        'spawn_time': time.time()
                    })
                    self.enemy_move_times[(x, y)] = time.time()  # Инициализация таймера для врага
                    break

    def move_enemies(self):
        for enemy in self.enemies:
            x, y = enemy['position']
            direction = enemy['direction']
            move_time = self.enemy_move_times[(x, y)]

            if (time.time() - move_time >= 1.0 / config.ENEMY_SPEED):  # Движение врага по таймеру
                if (direction == 'UP'):
                    y -= 1
                elif (direction == 'DOWN'):
                    y += 1
                elif (direction == 'LEFT'):
                    x -= 1
                elif (direction == 'RIGHT'):
                    x += 1

                if (x < 0 or x >= config.FIELD_WIDTH or y < 0 or y >= config.FIELD_HEIGHT or self.field[y][x] == 'W'):
                    enemy['bounces'] += 1
                    if (enemy['bounces'] >= config.ENEMY_BOUNCES):
                        self.enemies.remove(enemy)
                        del self.enemy_move_times[(x, y)]
                    else:
                        if (direction == 'UP'):
                            enemy['direction'] = 'DOWN'
                        elif (direction == 'DOWN'):
                            enemy['direction'] = 'UP'
                        elif (direction == 'LEFT'):
                            enemy['direction'] = 'RIGHT'
                        elif (direction == 'RIGHT'):
                            enemy['direction'] = 'LEFT'
                else:
                    del self.enemy_move_times[(enemy['position'][0], enemy['position'][1])]  # Удаление старого таймера
                    enemy['position'] = (x, y)
                    self.enemy_move_times[(x, y)] = time.time()  # Установка нового таймера

    def move_snake(self):
        if (time.time() - self.snake_move_time >= (self.snake_speed if self.effects['yellow'] <= time.time() else self.snake_speed_up)):
            head_x, head_y = self.snake[0]
            if (self.direction == 'UP'):
                head_y -= 1
            elif (self.direction == 'DOWN'):
                head_y += 1
            elif (self.direction == 'LEFT'):
                head_x -= 1
            elif (self.direction == 'RIGHT'):
                head_x += 1

            # Проверка столкновений с краями поля, стенами и врагами
            if (head_x < 0 or head_x >= config.FIELD_WIDTH or head_y < 0 or head_y >= config.FIELD_HEIGHT or
                    (self.field[head_y][head_x] == 'W' and time.time() > self.effects['white']) or
                    any(enemy['position'] == (head_x, head_y) for enemy in self.enemies)):
                self.game_over = True
                return

            # Проверка столкновений с телом змеи
            if ((head_x, head_y) in self.snake):
                self.game_over = True
                return

            # Проверка столкновений с едой
            for food in self.food:
                if (food['position'] == (head_x, head_y)):
                    self.snake.insert(0, (head_x, head_y))
                    self.field[head_y][head_x] = ''
                    self.food.remove(food)
                    if (food['type'] == 'yellow'):
                        self.effects['yellow'] = time.time() + config.YELLOW_FOOD_DURATION
                    elif (food['type'] == 'red'):
                        self.effects['red'] = time.time() + config.RED_FOOD_BLOCK_DURATION
                        self.enemy_spawn_blocked_until = self.effects['red']
                        self.enemies.clear()
                    elif (food['type'] == 'white'):
                        self.effects['white'] = time.time() + config.WHITE_FOOD_DURATION

                    self.score += 1  # Увеличение очков при поедании еды

                    self.spawn_food()
                    return

            # Перемещение змеи
            self.snake.insert(0, (head_x, head_y))
            self.snake.pop()
            self.snake_move_time = time.time()

    def draw_bezier_curve(self, p0, p1, p2, p3, color):
        steps = 100
        for i in range(steps):
            t = i / steps
            x = (1 - t)**3 * p0.x + 3 * (1 - t)**2 * t * p1.x + 3 * (1 - t) * t**2 * p2.x + t**3 * p3.x
            y = (1 - t)**3 * p0.y + 3 * (1 - t)**2 * t * p1.y + 3 * (1 - t) * t**2 * p2.y + t**3 * p3.y
            pygame.draw.circle(screen, color, (int(x), int(y)), int(cell_size / 4))

    def get_rainbow_color(self, index, length):
        hue = (index / length + time.time() * 0.1) % 1
        color = colorsys.hsv_to_rgb(hue, 1, 1)
        return (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))

    def draw_snake(self):
        if len(self.snake) < 2:
            return
        points = [Vector2(offset_x + (segment[0] * cell_size) + cell_size / 2,
                          offset_y + (segment[1] * cell_size) + cell_size / 2) for segment in self.snake]
        for i in range(len(points)):
            p0 = points[i - 1] if i > 0 else points[i]
            p3 = points[i]
            p1 = p0 + (p3 - p0) / 3
            p2 = p3 - (p3 - p0) / 3
            color = self.get_rainbow_color(i, len(points)) if self.effects['yellow'] > time.time() else BLUE
            if i == 0:
                pygame.draw.circle(screen, color, (int(p0.x), int(p0.y)), int(cell_size / 2))
            else:
                self.draw_bezier_curve(p0, p1, p2, p3, color)
                pygame.draw.circle(screen, color, (int(p3.x), int(p3.y)), int(cell_size / 2))

    def run(self):
        clock = pygame.time.Clock()

        while not self.game_over:
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    self.game_over = True
                elif (event.type == pygame.KEYDOWN):
                    if (event.key == pygame.K_UP and self.direction != 'DOWN'):
                        self.direction = 'UP'
                    elif (event.key == pygame.K_DOWN and self.direction != 'UP'):
                        self.direction = 'DOWN'
                    elif (event.key == pygame.K_LEFT and self.direction != 'RIGHT'):
                        self.direction = 'LEFT'
                    elif (event.key == pygame.K_RIGHT and self.direction != 'LEFT'):
                        self.direction = 'RIGHT'

            if (time.time() - self.food_spawn_time >= config.FOOD_SPAWN_RATE):
                self.spawn_food()
                self.food_spawn_time = time.time()

            if (time.time() - self.enemy_spawn_time >= config.ENEMY_SPAWN_RATE):
                self.spawn_enemy()
                self.enemy_spawn_time = time.time()

            self.move_enemies()
            self.move_snake()

            # Отрисовка игрового поля
            screen.fill(BLACK)
            for y in range(config.FIELD_HEIGHT):
                for x in range(config.FIELD_WIDTH):
                    cell_x = offset_x + (x * cell_size)
                    cell_y = offset_y + (y * cell_size)
                    rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
                    if (self.field[y][x] == 'W'):
                        pygame.draw.rect(screen, GRAY, rect)

            # Отрисовка змеи
            self.draw_snake()

            # Отрисовка еды
            for food in self.food:
                food_x = offset_x + (food['position'][0] * cell_size)
                food_y = offset_y + (food['position'][1] * cell_size)
                pygame.draw.circle(screen, config.FOOD_COLORS[food['type']], (int(food_x + cell_size / 2), int(food_y + cell_size / 2)), int(cell_size / 2))

            # Отрисовка врагов
            for enemy in self.enemies:
                enemy_x = offset_x + (enemy['position'][0] * cell_size)
                enemy_y = offset_y + (enemy['position'][1] * cell_size)
                pygame.draw.circle(screen, ORANGE, (int(enemy_x + cell_size / 2), int(enemy_y + cell_size / 2)), int(cell_size / 2))

            # Отображение очков
            score_text = font.render(f'Score: {self.score}', True, WHITE)
            screen.blit(score_text, (10, 10))

            pygame.display.flip()
            clock.tick(60)

# Запуск игры
game = SnakeGame()
game.run()

# Завершение Pygame
pygame.quit()