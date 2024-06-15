import pygame
import random
import time
import math
import config

# Инициализация Pygame
pygame.init()

# Установка размеров окна
SCREEN_WIDTH = config.FIELD_WIDTH * 20
SCREEN_HEIGHT = config.FIELD_HEIGHT * 20 + 40  # Добавляем место для меню сверху
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

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

    def create_field(self):
        return [['' for _ in range(config.FIELD_WIDTH)] for _ in range(config.FIELD_HEIGHT)]

    def create_snake(self):
        snake = [(config.FIELD_WIDTH // 2, config.FIELD_HEIGHT // 2)]
        for _ in range(config.INITIAL_SNAKE_LENGTH - 1):
            snake.append((snake[-1][0], snake[-1][1] - 1))
        return snake

    def spawn_initial_walls(self):
        wall_choice = random.choices(
            ['none', 'horizontal', 'vertical'],
            [config.NO_WALL_PROBABILITY, config.HORIZONTAL_WALL_PROBABILITY, config.VERTICAL_WALL_PROBABILITY]
        )[0]

        if wall_choice == 'horizontal':
            for x in range(config.FIELD_WIDTH):
                self.field[0][x] = 'W'
                self.field[config.FIELD_HEIGHT - 1][x] = 'W'
        elif wall_choice == 'vertical':
            for y in range(config.FIELD_HEIGHT):
                self.field[y][0] = 'W'
                self.field[y][config.FIELD_WIDTH - 1] = 'W'

    def spawn_food(self, initial=False):
        while len(self.food) < config.MAX_FOOD:
            x = random.randint(0, config.FIELD_WIDTH - 1)
            y = random.randint(0, config.FIELD_HEIGHT - 1)
            if self.field[y][x] == '':
                if initial or len(self.food) == 0:
                    food_type = 'green'
                else:
                    food_type = random.choice([ft for ft in config.FOOD_COLORS.keys() if ft != 'green'])
                self.food.append({
                    'position': (x, y),
                    'type': food_type,
                    'spawn_time': time.time()
                })
                self.field[y][x] = 'F'
                if not initial:
                    break

    def spawn_enemy(self):
        if len(self.enemies) < config.MAX_ENEMIES and time.time() > self.enemy_spawn_blocked_until:
            while True:
                x = random.randint(0, config.FIELD_WIDTH - 1)
                y = random.randint(0, config.FIELD_HEIGHT - 1)
                direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
                if self.field[y][x] == '':
                    self.enemies.append({
                        'position': (x, y),
                        'direction': direction,
                        'bounces': 0,
                        'spawn_time': time.time()
                    })
                    break

    def move_enemies(self):
        for enemy in self.enemies:
            x, y = enemy['position']
            direction = enemy['direction']

            if direction == 'UP':
                y -= 1
            elif direction == 'DOWN':
                y += 1
            elif direction == 'LEFT':
                x -= 1
            elif direction == 'RIGHT':
                x += 1

            if x < 0 or x >= config.FIELD_WIDTH or y < 0 or y >= config.FIELD_HEIGHT or self.field[y][x] == 'W':
                enemy['bounces'] += 1
                if enemy['bounces'] >= config.ENEMY_BOUNCES:
                    self.enemies.remove(enemy)
                else:
                    if direction == 'UP':
                        enemy['direction'] = 'DOWN'
                    elif direction == 'DOWN':
                        enemy['direction'] = 'UP'
                    elif direction == 'LEFT':
                        enemy['direction'] = 'RIGHT'
                    elif direction == 'RIGHT':
                        enemy['direction'] = 'LEFT'
            else:
                enemy['position'] = (x, y)

    def move_snake(self):
        head_x, head_y = self.snake[0]
        if self.direction == 'UP':
            head_y -= 1
        elif self.direction == 'DOWN':
            head_y += 1
        elif self.direction == 'LEFT':
            head_x -= 1
        elif self.direction == 'RIGHT':
            head_x += 1

        head_x %= config.FIELD_WIDTH
        head_y %= config.FIELD_HEIGHT

        if (head_x, head_y) in self.snake or (self.field[head_y][head_x] == 'W' and self.effects['white'] == 0):
            self.game_over = True
        else:
            self.snake.insert(0, (head_x, head_y))
            if (head_x, head_y) in [(f['position'][0], f['position'][1]) for f in self.food]:
                food = next(f for f in self.food if f['position'] == (head_x, head_y))
                self.apply_food_effects(food['type'])
                self.food.remove(food)
                self.spawn_food()
            else:
                self.snake.pop()

    def check_collisions(self):
        head_x, head_y = self.snake[0]
        if self.field[head_y][head_x] == 'W' and self.effects['white'] == 0:
            self.game_over = True
        for enemy in self.enemies:
            ex, ey = enemy['position']
            if (head_x, head_y) == (ex, ey):
                self.game_over = True

    def apply_food_effects(self, food_type):
        multiplier = 3 if self.effects['yellow'] > time.time() else 1
        if food_type == 'yellow':
            self.effects['yellow'] = time.time() + config.YELLOW_FOOD_DURATION
            self.score += 5 * multiplier
        elif food_type == 'red':
            self.effects['red'] = time.time() + config.RED_FOOD_BLOCK_DURATION
            killed_enemies = len(self.enemies)
            self.enemies.clear()
            self.enemy_spawn_blocked_until = time.time() + config.RED_FOOD_BLOCK_DURATION
            self.score += (5 + 50 * killed_enemies) * multiplier
        elif food_type == 'white':
            self.effects['white'] = time.time() + config.WHITE_FOOD_DURATION
            self.score += 10 * multiplier
        else:  # 'green'
            self.score += 5 * multiplier

    def update(self):
        self.move_snake()
        self.check_collisions()
        self.move_enemies()
        if time.time() - self.enemy_spawn_time > config.ENEMY_SPAWN_RATE and time.time() > self.enemy_spawn_blocked_until:
            self.spawn_enemy()
            self.enemy_spawn_time = time.time()
        if time.time() - self.food_spawn_time > config.FOOD_SPAWN_RATE:
            self.spawn_food()
            self.food_spawn_time = time.time()
        for effect in self.effects:
            if self.effects[effect] > 0 and time.time() > self.effects[effect]:
                self.effects[effect] = 0

    def render(self):
        screen.fill(BLACK)
        for x, y in self.snake:
            pygame.draw.circle(screen, BLUE, (x * 20 + 10, y * 20 + 10), 10)
        
        current_time = time.time()

        for food in self.food:
            x, y = food['position']
            food_type = food['type']
            color = config.FOOD_COLORS[food_type]
            elapsed_time = current_time - food['spawn_time']

            if elapsed_time < 0.5:  # Длительность анимации изменения прозрачности 0.5 секунд
                scale = math.sin(math.pi * elapsed_time)  # bounce эффект
                alpha = int(255 * min(elapsed_time * 2, 1))  # Ускоренное изменение прозрачности
                food_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(food_surface, (*color, alpha), (10, 10), int(10 * scale))
                screen.blit(food_surface, (x * 20, y * 20))
            else:
                pygame.draw.circle(screen, color, (x * 20 + 10, y * 20 + 10), 10)

        for enemy in self.enemies:
            x, y = enemy['position']
            elapsed_time = current_time - enemy['spawn_time']

            if elapsed_time < 0.5:  # Длительность анимации изменения прозрачности 0.5 секунд
                scale = math.sin(math.pi * elapsed_time)  # bounce эффект
                alpha = int(255 * min(elapsed_time * 2, 1))  # Ускоренное изменение прозрачности
                enemy_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(enemy_surface, (*ORANGE, alpha), (10, 10), int(10 * scale))
                screen.blit(enemy_surface, (x * 20, y * 20))
            else:
                pygame.draw.circle(screen, ORANGE, (x * 20 + 10, y * 20 + 10), 10)

        for y in range(config.FIELD_HEIGHT):
            for x in range(config.FIELD_WIDTH):
                if self.field[y][x] == 'W':
                    pygame.draw.rect(screen, GRAY, (x * 20, y * 20, 20, 20))
        
        # Отображение очков в меню сверху
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (10, SCREEN_HEIGHT - 30))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != 'DOWN':
                        self.direction = 'UP'
                    elif event.key == pygame.K_DOWN and self.direction != 'UP':
                        self.direction = 'DOWN'
                    elif event.key == pygame.K_LEFT and self.direction != 'RIGHT':
                        self.direction = 'LEFT'
                    elif event.key == pygame.K_RIGHT and self.direction != 'LEFT':
                        self.direction = 'RIGHT'
            self.update()
            self.render()
            clock.tick(config.SNAKE_SPEED if self.effects['yellow'] == 0 else config.SNAKE_SPEED_UP)

# Запуск игры
if __name__ == '__main__':
    game = SnakeGame()
    game.run()
    pygame.quit()