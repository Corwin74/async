import time
import curses
import logging
import random
import os

import asyncio_tools
from space_garbage import fill_orbit_with_garbage
from stars_and_ship import animate_spaceship, blink, print_game_messages,\
    update_year_counter
from obstacles_tools import show_obstacles

TIC_TIMEOUT = 0.1


def start_game_engine(canvas, frames, stars_qty=200):

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
    derwin = canvas.derwin(2, 50, max_y-2, max_x - 50)

    for _ in range(stars_qty):
        asyncio_tools.coroutines.append(
            blink(
                canvas, random.randint(1, max_y - 1),
                random.randint(1, max_x - 1),
                random.randint(1, 4),
                symbol=random.choice(['*', ':', '+', '.'])
            )
        )
    asyncio_tools.coroutines.append(fill_orbit_with_garbage(canvas, frames))
    asyncio_tools.coroutines.append(show_obstacles(canvas))
    asyncio_tools.coroutines.append(
        animate_spaceship(canvas, row, column, frames)
    )
    asyncio_tools.coroutines.append(update_year_counter())
    asyncio_tools.coroutines.append(print_game_messages(derwin))

    while True:
        for coroutine in asyncio_tools.coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                asyncio_tools.coroutines.remove(coroutine)
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
    logger.info('Game start')
    curses.wrapper(start_game_engine, frames)


if __name__ == '__main__':
    main()
