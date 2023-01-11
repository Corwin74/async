import time
import curses
import asyncio
import logging
import random
import uuid
from itertools import cycle
import os
from curses_tools import draw_frame, read_controls, get_frame_size
from obstacles import show_obstacles, Obstacle
from physics import update_speed


TIC_TIMEOUT = 0.1
coroutines = []
obstacles = {}


async def fly_garbage(canvas, column, garbage_frame, garbage_uid, speed=0.5):
    """Animate garbage, flying from top to bottom. \
        Сolumn position will stay same, as specified on start."""
    global obstacles

    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacles[garbage_uid].set_row(row)
    del obstacles[garbage_uid]


async def fill_orbit_with_garbage(canvas, frames):
    global coroutines

    garbage_keys = list(frames.keys())
    garbage_keys.remove('rocket_frame_1')
    garbage_keys.remove('rocket_frame_2')
    max_y, max_x = canvas.getmaxyx()
    while True:
        garbage = random.choice(garbage_keys)
        garbage_height, garbage_width = get_frame_size(frames[garbage])
        garbage_column = random.randint(1, max_x - garbage_width - 1)
        garbage_uid = uuid.uuid4()
        coroutines.append(
            fly_garbage(canvas, garbage_column, frames[garbage], garbage_uid)
        )
        obstacles[garbage_uid] = Obstacle(
            1,
            garbage_column,
            garbage_height,
            garbage_width,
            uid=garbage_uid)
        await sleep(10)


async def fire(canvas, start_row, start_column,
               rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows, columns

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, row, column, frames, max_x, max_y):
    global coroutines

    row_speed = column_speed = 0

    rocket_height, rocket_width = get_frame_size(frames['rocket_frame_1'])
    for frame in cycle(['rocket_frame_1', 'rocket_frame_2']):
        rows_direction, columns_direction, space_pressed =\
            read_controls(canvas)
        if space_pressed:
            coroutines.append(fire(canvas, row, column + 2, -1))
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

        draw_frame(canvas, row, column, frames[frame])
        await sleep(1)
        draw_frame(canvas, row, column, frames[frame], negative=True)


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


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
            await sleep(20)
            state = 2
        if state == 2:
            canvas.addstr(row, column, symbol)
            await sleep(3)
            state = 3
        if state == 3:
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await sleep(5)
            state = 4
        if state == 4:
            canvas.addstr(row, column, symbol)
            await sleep(3)
            state = 1


def start_game_engine(canvas, frames, logger, stars_qty=200):
    global coroutines
    global obstacles

    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)
    max_y, max_x = canvas.getmaxyx()
    # Function return a tuple (y, x) of the height and width of the window.
    # Not a maximum of coordinates. So adjust it.
    max_x -= 1
    max_y -= 1
    median_y = int(max_y / 2)
    median_x = int(max_x / 2)
    column = median_x
    row = median_y
    for _ in range(stars_qty):
        coroutines.append(
            blink(
                canvas, random.randint(1, max_y - 1),
                random.randint(1, max_x - 1),
                random.randint(1, 4),
                symbol=random.choice(['*', ':', '+', '.'])
            )
        )
    coroutines.append(fire(canvas, median_y - 1, median_x + 2, -1))
    coroutines.append(fill_orbit_with_garbage(canvas, frames))
    coroutines.append(show_obstacles(canvas, obstacles))
    coroutines.append(
        animate_spaceship(canvas, row, column, frames, max_x, max_y)
    )
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                logger.debug(f'StopIteration: {coroutine}')
                coroutines.remove(coroutine)
        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def load_frames_data(path):
    files = os.listdir(path=path)
    frames = {}
    for file in files:
        with open(f'{path}{file}', "r", encoding='utf-8') as f:
            frames[file.split('.')[0]] = f.read()
    return frames


def main():
    logger = logging.getLogger(__file__)
    logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO,
            filename='space.log',
    )
    frames = load_frames_data('frames/')
    curses.update_lines_cols()
    curses.wrapper(start_game_engine, frames, logger)


if __name__ == '__main__':
    main()
