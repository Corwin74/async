import curses
from itertools import cycle
import asyncio_tools
from obstacles_tools import obstacles
from curses_tools import get_frame_size, draw_frame, read_controls
from game_over import show_end_title
from physics import update_speed
from game_scenario import PHRASES


async def fire(canvas, start_row, start_column,
               rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio_tools.sleep(1)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio_tools.sleep(1)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows, columns

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio_tools.sleep(1)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed
        for obstacle in list(obstacles.values()):
            if obstacle.has_collision(row, column):
                obstacle.set_has_a_hit()
                obstacle.set_collision_coordinates(row, column)
                return


async def animate_spaceship(canvas, row, column, frames):

    row_speed = column_speed = 0
    max_y, max_x = canvas.getmaxyx()

    rocket_height, rocket_width = get_frame_size(frames['rocket_frame_1'])
    for frame in cycle(['rocket_frame_1', 'rocket_frame_2']):
        rows_direction, columns_direction, space_pressed =\
            read_controls(canvas)
        if space_pressed and asyncio_tools.year >= 2020:
            asyncio_tools.coroutines.append(fire(canvas, row, column + 2, -1))
        if columns_direction > 0:
            row_speed, column_speed = \
                update_speed(row_speed, column_speed, 0, 1)
        if columns_direction < 0:
            row_speed, column_speed = \
                update_speed(row_speed, column_speed, 0, -1)
        if rows_direction > 0:
            row_speed, column_speed = \
                update_speed(row_speed, column_speed, 1, 0)
        if rows_direction < 0:
            row_speed, column_speed = \
                update_speed(row_speed, column_speed, -1, 0)
        if rows_direction == 0 and columns_direction == 0:
            row_speed, column_speed = \
                update_speed(row_speed, column_speed, 0, 0)

        row, column = row + row_speed, column + column_speed
        column = min(max_x - rocket_width, column)
        column = max(1, column)
        row = min(max_y - rocket_height, row)
        row = max(1, row)

        for obstacle in list(obstacles.values()):
            if obstacle.has_collision(row, column):
                obstacle.set_has_a_hit()
                obstacle.set_collision_coordinates(row, column)
                asyncio_tools.coroutines.append(show_end_title(canvas))
                asyncio_tools.game_is_over = True
                return
        draw_frame(canvas, row, column, frames[frame])
        await asyncio_tools.sleep(1)
        draw_frame(canvas, row, column, frames[frame], negative=True)


async def blink(
                canvas,
                row,
                column,
                start_state,
                symbol='*'
                ):
    state = start_state
    while True:
        if state == 1:
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio_tools.sleep(20)
            state = 2
        if state == 2:
            canvas.addstr(row, column, symbol)
            await asyncio_tools.sleep(3)
            state = 3
        if state == 3:
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio_tools.sleep(5)
            state = 4
        if state == 4:
            canvas.addstr(row, column, symbol)
            await asyncio_tools.sleep(3)
            state = 1


async def print_game_messages(canvas):

    while True:
        canvas.clear()
        if PHRASES.get(asyncio_tools.year):
            canvas.addstr(1, 1, str(asyncio_tools.year) + ' ---> ' +
                          PHRASES.get(asyncio_tools.year))
        else:
            canvas.addstr(1, 1, str(asyncio_tools.year))
        canvas.refresh()
        await asyncio_tools.sleep(1)


async def update_year_counter():
    while True:
        for _ in range(15):
            await asyncio_tools.sleep(1)
        if not asyncio_tools.game_is_over:
            asyncio_tools.year += 1
