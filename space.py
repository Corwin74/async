import time
import curses
import asyncio
import logging
import random
from itertools import cycle
import os
from curses_tools import draw_frame, read_controls, get_frame_size


TIC_TIMEOUT = 0.1


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
    rocket_height, rocket_width = get_frame_size(frames['rocket_frame_1'])
    for frame in cycle(['rocket_frame_1', 'rocket_frame_2']):
        rows_direction, columns_direction, space_pressed =\
            read_controls(canvas)
        if columns_direction > 0:
            column = min(max_x - rocket_width, column + columns_direction)
        if columns_direction < 0:
            column = max(1, column + columns_direction)
        if rows_direction > 0:
            row = min(max_y - rocket_height, row + rows_direction)
        if rows_direction < 0:
            row = max(1, row + rows_direction)
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
    coroutines = [
        blink(
            canvas, random.randint(1, max_y - 1),
            random.randint(1, max_x - 1),
            random.randint(1, 4),
            symbol=random.choice(['*', ':', '+', '.'])
        )
        for _ in range(stars_qty)
    ]
    coroutines.append(fire(canvas, median_y - 1, median_x + 2, -1))
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
