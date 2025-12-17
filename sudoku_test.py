import pytest
import sudoku
import copy
import pygame
import os

def test_is_valid_move_success():
    """Тест №1: Проверка валидного хода."""
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 5

    result = sudoku.is_valid_move(board, 0, 1, 6)
    assert result is True


def test_is_valid_move_exception():
    """Тест №2: Проверка выброса ошибки при неверных координатах."""
    board = [[0] * 9 for _ in range(9)]

    with pytest.raises(ValueError) as exception:
        sudoku.is_valid_move(board, 10, 10, 1)

    assert f"Координаты (10, 10) выходят за пределы поля" in str(exception.value)

def test_solved_board_success():
    """Тест №3: Успешное решение пустой доски."""
    board = [[0] * 9 for _ in range(9)]

    result = sudoku.solved_board(board)

    assert result is not False

    zeros = sum(row.count(0) for row in result) # Проверка на заполненность доски
    assert zeros == 0


def test_solved_board_failure():
    """
    Тест №4: Нерешаемая доска возвращает False.
    Мы берем готовое решение и ломаем его, чтобы алгоритм не завис.
    """
    game_data = sudoku.generate_board(1)
    full_board = game_data[1]

    broken_board = copy.deepcopy(full_board)

    original_value = broken_board[0][0]
    broken_board[0][0] = 0
    broken_board[0][1] = original_value # Делаем подмену: запомнили цифру из позиции [0][0], удалили с доски и переставили на другую позицию

    result = sudoku.solved_board(broken_board)
    assert result is False

def test_generate_board_success():
    """Тест №5: Проверка генерации уровня."""
    difficulty = 1

    grid, solution, hints, mistakes = sudoku.generate_board(difficulty)

    assert len(grid) == 9
    assert hints == 6
    zeros_in_solution = sum(row.count(0) for row in solution) # Проверка на заполненность игровой доски
    assert zeros_in_solution == 0


def test_generate_board_exception():
    """Тест №6: Ошибка при неверной сложности."""
    with pytest.raises(sudoku.SudokuError) as exception:
        sudoku.generate_board(99)

    assert "Неверный уровень сложности" in str(exception.value)


os.environ["SDL_VIDEODRIVER"] = "dummy" # Не инициализируем открытие игрового окна для проведения тестов

def test_draw_selected_cell_success():
    """Тест №7: Функция успешно рисует рамку на переданной поверхности."""
    pygame.init()
    surface = pygame.Surface((sudoku.WIDTH, sudoku.HEIGHT))

    try:
        sudoku.draw_selected_cell(surface, 0, 0)
        assert True
    finally:
        pygame.quit()

def test_draw_selected_cell_exception():
    """Тест №8: Передача None вместо поверхности вызывает AttributeError."""
    pygame.init()
    try:
        with pytest.raises(AttributeError):
            sudoku.draw_selected_cell(None, 0, 0)
    finally:
        pygame.quit()

def test_draw_numbers_success():
    """Тест №9: Успешная отрисовка чисел на поле."""
    pygame.init()
    pygame.font.init()

    sudoku.font = pygame.font.SysFont("Arial", 20)
    surface = pygame.Surface((sudoku.WIDTH, sudoku.HEIGHT))


    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 5

    original = copy.deepcopy(board)
    solution = copy.deepcopy(board)

    try:
        sudoku.draw_numbers(surface, board, original, solution)
        assert True
    finally:
        pygame.quit()

def test_draw_numbers_exception():
    """Тест №10: Некорректные данные (строка вместо списка) вызывают TypeError/IndexError."""
    pygame.init()
    pygame.font.init()
    sudoku.font = pygame.font.SysFont("Arial", 20)
    surface = pygame.Surface((sudoku.WIDTH, sudoku.HEIGHT))

    try:
        with pytest.raises((TypeError, IndexError, AttributeError)):
            sudoku.draw_numbers(surface, "invalid_board", [], [])
    finally:
        pygame.quit()

def test_draw_board_success():
    """Тест №11: Успешная отрисовка сетки."""
    pygame.init()
    surface = pygame.Surface((sudoku.WIDTH, sudoku.HEIGHT))

    try:
        sudoku.draw_board(surface)
        assert True
    finally:
        pygame.quit()

def test_draw_board_exception():
    """Тест №12: Отрисовка на невалидном объекте."""
    pygame.init()
    try:
        with pytest.raises(AttributeError):
            sudoku.draw_board(12345)
    finally:
        pygame.quit()

def test_draw_game_info_success():
    """Тест №13: Успешная отрисовка статистики."""
    pygame.init()
    pygame.font.init()
    sudoku.font = pygame.font.SysFont("Arial", 20)
    surface = pygame.Surface((sudoku.WIDTH, sudoku.HEIGHT))

    try:
        sudoku.draw_game_info(surface, hints=3, time_ms=60000, mistakes=2)
        assert True
    finally:
        pygame.quit()

def test_draw_game_info_exception():
    """Тест №14: Ошибка при математических операциях с None (время)."""
    pygame.init()
    pygame.font.init()
    sudoku.font = pygame.font.SysFont("Arial", 20)
    surface = pygame.Surface((sudoku.WIDTH, sudoku.HEIGHT))

    try:
        with pytest.raises(TypeError):
            sudoku.draw_game_info(surface, hints=3, time_ms=None, mistakes=2) # Ошибка при None // 1000
    finally:
        pygame.quit()

def test_draw_restart_offer_success():
    """Тест №15: Успешная отрисовка кнопки рестарта."""
    pygame.init()
    pygame.font.init()
    sudoku.font = pygame.font.SysFont("Arial", 20)
    surface = pygame.Surface((sudoku.WIDTH, sudoku.HEIGHT))

    try:
        sudoku.draw_restart_offer(surface)
        assert True
    finally:
        pygame.quit()

def test_draw_restart_offer_exception():
    """Тест №16: Ошибка при передаче None вместо поверхности."""
    pygame.init()
    pygame.font.init()
    sudoku.font = pygame.font.SysFont("Arial", 20)

    try:
        with pytest.raises(AttributeError):
            sudoku.draw_restart_offer(None)

    finally:
        pygame.quit()

def test_draw_intro_success():
    """Тест №17: Успешная отрисовка меню."""
    pygame.init()
    pygame.font.init()
    sudoku.font = pygame.font.SysFont("Arial", 20)
    surface = pygame.Surface((sudoku.WIDTH, sudoku.HEIGHT))

    try:
        sudoku.draw_intro(surface)
        assert True
    finally:
        pygame.quit()

def test_draw_intro_exception():
    """Тест №18: Ошибка при передаче невалидного объекта поверхности."""
    pygame.init()
    pygame.font.init()
    sudoku.font = pygame.font.SysFont("Arial", 20)

    try:
        with pytest.raises(AttributeError):
            sudoku.draw_intro("Not a surface")
    finally:
        pygame.quit()