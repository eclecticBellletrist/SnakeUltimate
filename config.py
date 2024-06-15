# Размеры игрового поля в клетках (тайлах)
FIELD_WIDTH = 40
FIELD_HEIGHT = 30

# Размеры экрана в пикселях
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Цвета
SNAKE_COLOR = (0, 0, 255)  # Синий
FOOD_COLORS = {
    'green': (0, 255, 0),   # Зеленый
    'yellow': (255, 255, 0), # Желтый
    'red': (255, 0, 0),     # Красный
    'white': (255, 255, 255) # Белый
}
ENEMY_COLOR = (255, 165, 0) # Оранжевый
WALL_COLOR = (128, 128, 128) # Серый

# Параметры начальной змейки
INITIAL_SNAKE_LENGTH = 5

# Параметры еды
MAX_FOOD = 5
FOOD_SPAWN_RATE = 5  # Частота появления еды (в секундах)
YELLOW_FOOD_DURATION = 5  # Длительность эффекта ускорения от желтой еды (в секундах)
RED_FOOD_BLOCK_DURATION = 10  # Длительность блокировки появления врагов от красной еды (в секундах)
WHITE_FOOD_DURATION = 5  # Длительность прохождения сквозь стены от белой еды (в секундах)

# Параметры врагов
MAX_ENEMIES = 3
ENEMY_SPAWN_RATE = 10  # Частота появления врагов (в секундах)
ENEMY_BOUNCES = 5  # Количество отскоков врагов перед исчезновением

# Вероятности появления стен
NO_WALL_PROBABILITY = 0.7
HORIZONTAL_WALL_PROBABILITY = 0.15
VERTICAL_WALL_PROBABILITY = 0.15

# Скорость змейки
SNAKE_SPEED = 12  # Количество клеток в секунду
SNAKE_SPEED_UP = 25  # Количество клеток в секунду при эффекте от желтой еды