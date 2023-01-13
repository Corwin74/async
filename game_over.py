import curses
from curses_tools import draw_frame, get_frame_size
from asyncio_tools import sleep


GAME_OVER_FRAME = """
  ______      ___      .___  ___.  _______      ______   ____    ____  _______ .______      
 /  _____|    /   \     |   \/   | |   ____|    /  __  \  \   \  /   / |   ____||   _  \     
|  |  __     /  ^  \    |  \  /  | |  |__      |  |  |  |  \   \/   /  |  |__   |  |_)  |    
|  | |_ |   /  /_\  \   |  |\/|  | |   __|     |  |  |  |   \      /   |   __|  |      /     
|  |__| |  /  _____  \  |  |  |  | |  |____    |  `--'  |    \    /    |  |____ |  |\  \----.
 \______| /__/     \__\ |__|  |__| |_______|    \______/      \__/     |_______|| _| `._____|"""


async def show_end_title(canvas):
    max_y, max_x = canvas.getmaxyx()
    title_height, title_width = get_frame_size(GAME_OVER_FRAME)
    row = (max_y - title_height) / 2
    column = (max_x - title_width) / 2
    while True:
        draw_frame(canvas, row, column, GAME_OVER_FRAME, style=curses.A_DIM)
        await sleep(20)
        draw_frame(canvas, row, column, GAME_OVER_FRAME)
        await sleep(3)
        draw_frame(canvas, row, column, GAME_OVER_FRAME, style=curses.A_BOLD)
        await sleep(5)
        draw_frame(canvas, row, column, GAME_OVER_FRAME)
        await sleep(3)
