import curses
from curses_tools import draw_frame, get_frame_size
from asyncio_tools import sleep


GAME_OVER_FRAME = """  #####                          #######                      
 #     #   ##   #    # ######    #     # #    # ###### #####  
 #        #  #  ##  ## #         #     # #    # #      #    # 
 #  #### #    # # ## # #####     #     # #    # #####  #    # 
 #     # ###### #    # #         #     # #    # #      #####  
 #     # #    # #    # #         #     #  #  #  #      #   #  
  #####  #    # #    # ######    #######   ##   ###### #    # 
                                                              
"""


async def show_end_title(canvas):
    max_y, max_x = canvas.getmaxyx()
    title_height, title_width = get_frame_size(GAME_OVER_FRAME)
    row = (max_y - title_height) / 2
    column = (max_x - title_width) / 2
    while True:
        for i in range(20):
            draw_frame(canvas, row, column, GAME_OVER_FRAME, style=curses.A_DIM)
            await sleep(1)
        for i in range(3):
            draw_frame(canvas, row, column, GAME_OVER_FRAME)
            await sleep(1)
        for i in range(5):
            draw_frame(canvas, row, column, GAME_OVER_FRAME, style=curses.A_BOLD)
            await sleep(1)
        for i in range(3):
            draw_frame(canvas, row, column, GAME_OVER_FRAME)
            await sleep(1)
