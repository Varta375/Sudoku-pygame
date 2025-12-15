import copy
import random
import pygame
import argparse
from pathlib import Path
class SudokuError(Exception):
    """Базовый класс для логических ошибок игры Судоку"""
    pass

WIDTH = 540
"""int: Ширина окна приложения в пикселях"""

HEIGHT = 660
"""int: Высота окна приложения в пикселях (включая область статистики)"""

CELL_SIZE = 540 // 9
"""int: Размер одной клетки поля (ширина поля / 9)"""

WHITE = (255, 255, 255)
"""tuple: Белый цвет. Используется для исходных (неизменяемых) цифр"""

BLACK = (0, 0, 0)
"""tuple: Черный цвет. Используется для линий сетки и текста меню"""

GRAY = (128, 128, 128)
"""tuple: Серый цвет. Фоновая заливка игрового поля"""

GREEN = (0, 255, 0)
"""tuple: Зеленый цвет. Используется для правильных ответов и кнопок"""

RED = (255, 0, 0)
"""tuple: Красный цвет. Используется для ошибок, выделения и кнопок"""

YELLOW = (255, 255, 0)
"""tuple: Желтый цвет. Используется для подсказок и таймера"""

screen = None
"""pygame.Surface: Основная поверхность окна, на которой происходит отрисовка"""

font = None
"""pygame.font.Font: Шрифт для отрисовки текста и цифр"""

clock = None
"""pygame.time.Clock: Объект для контроля FPS (кадров в секунду)"""
#Заимствованный код (снизу, источник: https://habr.com/ru/companies/otus/articles/746408/)
def is_valid_move(game_board, row, col, num):
    """
    Проверяет валидность хода по правилам Судоку

    :param game_board: Текущее поле 9x9
    :param row: Индекс строки
    :param col: Индекс столбца
    :param num: Число для проверки
    :return: True, если ход возможен
    :raises ValueError: Если индексы вне диапазона
    """
    if not (0 <= row < 9 and 0 <= col < 9):
        raise ValueError(f"Координаты ({row}, {col}) выходят за пределы поля")

    if num in game_board[row]:
        return False

    for i in range(9):
        if game_board[i][col] == num:
            return False

    start_row = (row // 3) * 3
    start_col = (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if game_board[start_row + i][start_col + j] == num:
                return False
    return True

def solved_board(game_board):
    """
    Рекурсивно решает доску. Использует случайный порядок чисел для генерации

    :param game_board: Поле для решения
    :return: Решенное поле или False
    """
    for i in range(9):
        for j in range(9):
            if game_board[i][j] == 0:
                random_numbers = list(range(1, 10))
                random.shuffle(random_numbers)
                for key in random_numbers:
                    try:
                        if is_valid_move(game_board, i, j, key):
                            game_board[i][j] = key
                            if solved_board(game_board):
                                return game_board
                            else:
                                game_board[i][j] = 0
                    except ValueError as error:
                        print(f"Внутренняя ошибка валидации: {error}")
                        return False
                return False
    return game_board
#Заимствованный код (сверху, источник: https://habr.com/ru/companies/otus/articles/746408/)

def generate_board(difficulty):
    """
    Генерирует игровое поле и решение

    :param difficulty: Сложность (1, 2 или 3)
    :return: (game_board, solution_board, hints, mistakes)
    :raises SudokuError: Если сложность указана неверно
    """
    hints_map = {1: 6, 2: 4, 3: 2}

    if difficulty not in hints_map:
        raise SudokuError(f"Неверный уровень сложности: {difficulty}. Ожидался 1, 2 или 3 (Easy, Medium, Hard)")

    hints_left = hints_map[difficulty]
    mistakes_left = hints_map[difficulty] - 1

    puzzle = [[0] * 9 for _ in range(9)]
    solved_board(puzzle)

    solution = copy.deepcopy(puzzle)
    copied_board = copy.deepcopy(puzzle)

    counter_of_deleted_elements = 0
    target_deleted = difficulty * 20

    while counter_of_deleted_elements != target_deleted:
        row = random.randint(0, 8)
        col = random.randint(0, 8)

        if copied_board[row][col] != 0:
            copied_board[row][col] = 0
            counter_of_deleted_elements += 1

    return copied_board, solution, hints_left, mistakes_left


def draw_selected_cell(surface, row, col):
    """Рисует рамку вокруг выбранной клетки"""
    if row is not None and col is not None:
        try:
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            pygame.draw.rect(surface, RED, (x, y, CELL_SIZE, CELL_SIZE), 3)
        except:
            raise AttributeError("Не удалось нарисовать рамку")


def draw_numbers(surface, game_board, original_grid, solution_grid, mistake_number=None):
    """Отрисовывает числа на доске с учетом цветов и подсветки ошибок"""
    for row in range(9):
        for col in range(9):
            val = game_board[row][col]
            if val != 0:
                color = RED
                if original_grid[row][col] != 0:
                    color = WHITE
                elif val == solution_grid[row][col]:
                    color = GREEN
                if val == mistake_number:
                    color = RED

                text_layer = font.render(str(val), True, color)
                coord_x = col * CELL_SIZE + (CELL_SIZE - text_layer.get_width()) // 2
                coord_y = row * CELL_SIZE + (CELL_SIZE - text_layer.get_height()) // 2
                surface.blit(text_layer, (coord_x, coord_y))


def draw_board(surface):
    """Рисует сетку поля (линии)"""
    surface.fill(GRAY)
    for i in range(10):
        line_width = 3 if i % 3 == 0 else 1
        pygame.draw.line(surface, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, 540), line_width)
        pygame.draw.line(surface, BLACK, (0, i * CELL_SIZE), (540, i * CELL_SIZE), line_width)


def draw_game_info(surface, hints, time_ms, mistakes):
    """Рисует нижнюю панель статистики"""
    minutes = (time_ms // 1000) // 60
    seconds = (time_ms // 1000) % 60
    text_hints = font.render(f"Hints: {hints}", True, YELLOW)
    time_info = font.render(f"Time: {minutes:02}:{seconds:02}", True, YELLOW)
    game_mistakes_info = font.render(f"Mistakes left: {mistakes}", True, RED)
    surface.blit(text_hints, (10, 540))
    surface.blit(time_info, (350, 540))
    surface.blit(game_mistakes_info, (100, 590))

def draw_restart_offer(surface):
    """Рисует кнопку 'Restart'"""
    try:
        restart_text = font.render("Restart", True, BLACK)
        rect_width = restart_text.get_width() + 20
        rect_height = restart_text.get_height() + 10
        rect_x = (WIDTH - rect_width) // 2
        rect_y = 395
        pygame.draw.rect(surface, GREEN, (rect_x, rect_y, rect_width, rect_height))
        surface.blit(restart_text, (rect_x + 10, rect_y + 5))
    except (AttributeError, TypeError):
        raise AttributeError("Ошибка отрисовки меню: неверная поверхность или шрифт")

def draw_intro(surface):
    """Рисует стартовое меню"""
    try:
        pygame.draw.rect(surface, GREEN, (0, 0, 180, HEIGHT))
        pygame.draw.rect(surface, YELLOW, (180, 0, 360, HEIGHT))
        pygame.draw.rect(surface, RED, (360, 0, 540, HEIGHT))
        easy_level = font.render("Easy", True, BLACK)
        medium_level = font.render("Medium", True, BLACK)
        hard_level = font.render("Hard", True, BLACK)
        surface.blit(easy_level, (WIDTH // 12, HEIGHT // 2))
        surface.blit(medium_level, (WIDTH // 2.7, HEIGHT // 2))
        surface.blit(hard_level, (WIDTH // 1.3, HEIGHT // 2))
    except (AttributeError, TypeError):
        raise AttributeError("Ошибка отрисовки кнопки рестарта: неверная поверхность или шрифт")

def main(save_path):
    """Основная функция, содержащая игровой цикл"""

    game_state = "start"
    """str: Текущее состояние игры. Возможные значения: 'start', 'playing', 'win', 'lose'"""

    done = False
    """bool: Флаг управления главным циклом. Если True, программа завершается"""

    grid = None
    """list[list[int]]: Текущее состояние игрового поля 9x9, которое видит и меняет игрок"""

    solution_grid = None
    """list[list[int]]: Полностью решенное поле 9x9, используется для проверки ответов"""

    original_grid = None
    """list[list[int]]: Исходное состояние поля при генерации. Используется для определения неизменяемых клеток"""

    hints_count = 0
    """int: Количество доступных подсказок у игрока"""

    mistakes_left = 0
    """int: Количество оставшихся жизней (прав на ошибку)"""

    start_game_time = 0
    """int: Время системного таймера (в мс) в момент начала партии. Точка отсчета для секундомера"""

    game_time = 0
    """int: Текущее время игры в миллисекундах (разница между текущим временем и start_game_time)"""

    game_data = None
    """tuple: Кортеж данных от генератора уровня, содержащий (grid, solution, hints, mistakes)"""

    selected_row = None
    """int or None: Индекс строки (0-8) текущей выбранной клетки"""

    selected_col = None
    """int or None: Индекс столбца (0-8) текущей выбранной клетки"""

    pos = None
    """tuple[int, int]: Координаты курсора мыши (x, y) в момент события клика"""

    col = 0
    """int: Индекс столбца, рассчитанный на основе координат клика мыши"""

    row = 0
    """int: Индекс строки, рассчитанный на основе координат клика мыши"""

    digit = 0
    """int: Цифра (1-9), введенная пользователем с клавиатуры"""

    mistake_number_reasoner = None
    """int or None: Цифра (1-9), которая была введена неверно. Используется для подсветки всех таких цифр на поле"""

    restart_button_rect = pygame.Rect(170, 395, 200, 50)
    """pygame.Rect: Область кнопки перезапуска игры для обработки кликов мыши"""

    text = None
    """pygame.Surface: Объект отрисованного текста (для заголовков Win/Lose)"""

    text_rect = None
    """pygame.Rect: Прямоугольник, содержащий координаты и размер заголовка текста"""

    numbers_map = {
        pygame.K_KP1: 1, pygame.K_1: 1, pygame.K_KP2: 2, pygame.K_2: 2,
        pygame.K_KP3: 3, pygame.K_3: 3, pygame.K_KP4: 4, pygame.K_4: 4,
        pygame.K_KP5: 5, pygame.K_5: 5, pygame.K_KP6: 6, pygame.K_6: 6,
        pygame.K_KP7: 7, pygame.K_7: 7, pygame.K_KP8: 8, pygame.K_8: 8,
        pygame.K_KP9: 9, pygame.K_9: 9
    }
    """dict: Словарь сопоставления клавиш клавиатуры (основных и numpad) с целыми числами 1-9"""

    try:
        while not done:
            if game_state == "playing":
                game_time = pygame.time.get_ticks() - start_game_time
                if mistakes_left <= 0:
                    game_state = "lose"
                if grid == solution_grid:
                    game_state = "win"

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

                if game_state == "start":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        try:
                            difficulty = 0
                            if 0 <= pos[0] <= 180:
                                difficulty = 1
                            elif 180 <= pos[0] <= 360:
                                difficulty = 2
                            else:
                                difficulty = 3

                            game_data = generate_board(difficulty)
                            grid = game_data[0]
                            solution_grid = game_data[1]
                            hints_count = game_data[2]
                            mistakes_left = game_data[3]
                            original_grid = copy.deepcopy(grid)

                            start_game_time = pygame.time.get_ticks()
                            game_state = "playing"
                        except SudokuError as error:
                            print(f"Ошибка при создании уровня: {error}")

                elif game_state == "playing":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if 0 <= pos[0] <= WIDTH and 0 <= pos[1] <= HEIGHT:
                            col = pos[0] // CELL_SIZE
                            row = pos[1] // CELL_SIZE
                            if 0 <= row <= 8 and 0 <= col <= 8:
                                selected_row = row
                                selected_col = col

                    if selected_col is not None and selected_row is not None:
                        if event.type == pygame.KEYDOWN:
                            if event.key in numbers_map:
                                digit = numbers_map[event.key]

                                if original_grid[selected_row][selected_col] == 0:
                                    if grid[selected_row][selected_col] == 0 or grid[selected_row][
                                        selected_col] != digit:
                                        if digit != solution_grid[selected_row][selected_col]:
                                            mistakes_left -= 1
                                            grid[selected_row][selected_col] = digit
                                            mistake_number_reasoner = digit
                                        else:
                                            grid[selected_row][selected_col] = digit
                                            mistake_number_reasoner = None

                            elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                                if original_grid[selected_row][selected_col] == 0:
                                    grid[selected_row][selected_col] = 0

                            elif event.key == pygame.K_RETURN:
                                grid = copy.deepcopy(solution_grid)

                            elif event.key == pygame.K_h:
                                if hints_count > 0:
                                    if grid[selected_row][selected_col] == 0:
                                        grid[selected_row][selected_col] = solution_grid[selected_row][selected_col]
                                        hints_count -= 1

                elif game_state in ("lose", "win"):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if restart_button_rect.collidepoint(pos):
                            game_state = "start"
                            selected_col, selected_row = None, None
                            mistake_number_reasoner = None

            if game_state == "start":
                draw_intro(screen)

            elif game_state == "playing":
                draw_board(screen)
                draw_selected_cell(screen, selected_row, selected_col)
                if grid:
                    draw_numbers(screen, grid, original_grid, solution_grid, mistake_number_reasoner)
                    draw_game_info(screen, hints_count, game_time, mistakes_left)

            elif game_state == "lose":
                screen.fill(BLACK)
                text = font.render("Game Over", True, RED)
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                screen.blit(text, text_rect)
                if grid:
                    draw_game_info(screen, hints_count, game_time, mistakes_left)
                draw_restart_offer(screen)

            elif game_state == "win":
                screen.fill(BLACK)
                text = font.render("You won!", True, GREEN)
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                screen.blit(text, text_rect)
                if grid:
                    draw_game_info(screen, hints_count, game_time, mistakes_left)
                draw_restart_offer(screen)

            pygame.display.flip()
            clock.tick(60)

    except KeyboardInterrupt:
        print("Игра остановлена пользователем")
    except Exception as error:
        print(f"Критическая ошибка в главном цикле: {error}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sudoku Game")
    parser.add_argument(
        "--save-path",
        type=str,
        default="saves/game_save.json",
        help="Путь к файлу сохранения"
    )
    args = parser.parse_args()
    save_path = Path(args.save_path)

    pygame.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sudoku")
        font = pygame.font.SysFont("Times New Roman", 40)
    except pygame.error as error:
        print(f"Ошибка инициализации графики: {error}")
        exit(1)

    clock = pygame.time.Clock()
    main(save_path)