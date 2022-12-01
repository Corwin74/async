import time
import curses
import asyncio


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    while True:
        canvas.border()
        curses.curs_set(False)
        coroutine = blink(canvas, 5, 20)
        coroutine.send(None)
        canvas.refresh()
        time.sleep(2)
        coroutine.send(None)
        canvas.refresh()
        time.sleep(0.3)
        coroutine.send(None)
        canvas.refresh()
        time.sleep(0.5)
        coroutine.send(None)
        canvas.refresh()
        time.sleep(0.3)
        canvas.refresh()
        time.sleep(1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
