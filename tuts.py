import time
import curses
import asyncio
import logging
import random


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
    max_row, max_column = rows - 2, columns - 2

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def sleep(canvas, tics=1):
    for _ in range(int(tics)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    state = random.randint(1, 4)
    while True:
        if state == 1:
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await sleep(canvas, 20)
            state = 2
        if state == 2:
            canvas.addstr(row, column, symbol)
            await sleep(canvas, 3)
            state = 3
        if state == 3:
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await sleep(canvas, 5)
            state = 4
        if state == 4:
            canvas.addstr(row, column, symbol)
            await sleep(canvas, 3)
            state = 1


def draw(canvas, stars_qty=200):

    canvas.border()
    curses.curs_set(False)
    max_y, max_x = canvas.getmaxyx()
    coroutines = [blink(
                        canvas, random.randint(1, max_y-2),
                        random.randint(1, max_x-2),
                        symbol=random.choice(['*', ':', '+', '.'])
                        ) for _ in range(stars_qty)]
    coroutines.append(fire(canvas, max_y/2, max_x/2, -1))
    while True:
        try:
            for coroutine in coroutines.copy():
                coroutine.send(None)
            canvas.refresh()
            time.sleep(TIC_TIMEOUT)
        except StopIteration:
            coroutines.remove(coroutine)


if __name__ == '__main__':
    logger = logging.getLogger(__file__)
    logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
    )
    curses.update_lines_cols()
    curses.wrapper(draw)
