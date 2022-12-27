import time
import curses
import asyncio
import logging
import random


TIC_TIMEOUT = 0.1


async def sleep(canvas, tics=1):
    for _ in range(int(tics)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(canvas, 20)

        canvas.addstr(row, column, symbol)
        await sleep(canvas, 3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(canvas, 5)

        canvas.addstr(row, column, symbol)
        await sleep(canvas, 3)


def draw(canvas, stars_qty=300):

    canvas.border()
    curses.curs_set(False)
    max_y, max_x = canvas.getmaxyx()
    coroutines = [blink(canvas, random.randint(1, max_y-2),
                        random.randint(1, max_x-2), symbol=random.choice(['*', ':', '+', '.'])) for _ in range(stars_qty)]
    while True:
        try:
            for coroutine in coroutines:
                coroutine.send(None)
            canvas.refresh()
            time.sleep(TIC_TIMEOUT)
        except StopIteration:
            print('Жопа!')


if __name__ == '__main__':
    logger = logging.getLogger(__file__)
    logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
    )
    curses.update_lines_cols()
    curses.wrapper(draw)
