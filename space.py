import time
import curses
import asyncio
import logging
import random
from curses_tools import draw_frame, read_controls


TIC_TIMEOUT = 0.1


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
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


async def animate_spaceship(canvas, row, column):
    draw_frame(canvas, row, column, rocket_frame_1)
    await sleep(1)
    draw_frame(canvas, row, column, rocket_frame_1, negative=True)
    draw_frame(canvas, row, column, rocket_frame_2)
    await sleep(1)
    draw_frame(canvas, row, column, rocket_frame_2, negative=True)


async def sleep(tics=1):
    for _ in range(int(tics)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    state = random.randint(1, 4)
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


def game_engine(canvas, stars_qty=200):
    
    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)
    max_y, max_x = canvas.getmaxyx()
    median_y = int(max_y / 2)
    median_x = int(max_x / 2)
    x = median_x
    y = median_y
    coroutines = [blink(
                        canvas, random.randint(1, max_y - 2),
                        random.randint(1, max_x - 2),
                        symbol=random.choice(['*', ':', '+', '.'])
                        ) for _ in range(stars_qty)]
    coroutines.append(fire(canvas, median_y, median_x, -1))
    coroutines.append(animate_spaceship(canvas, median_y + 1, median_x - 2))
    while True:
        try:
            for coroutine in coroutines.copy():
                coroutine.send(None)
            canvas.refresh()
            rows_direction, columns_direction, space_pressed = read_controls(canvas)
            x += columns_direction
            y += rows_direction
            time.sleep(TIC_TIMEOUT)
        except StopIteration:
            coroutines.remove(coroutine)
            coroutines.append(animate_spaceship(canvas, y, x))


if __name__ == '__main__':
    logger = logging.getLogger(__file__)
    logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
    )
    with open('frames/rocket_frame_1.txt', 'r') as f:
        rocket_frame_1 = f.read()
    with open('frames/rocket_frame_2.txt', 'r') as f:
        rocket_frame_2 = f.read()
    curses.update_lines_cols()
    curses.wrapper(game_engine)

