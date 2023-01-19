import uuid
import random
import settings
from obstacles_tools import obstacles, Obstacle
from curses_tools import draw_frame, get_frame_size
import asyncio_tools
from explosion import explode
from game_scenario import get_garbage_delay_tics


async def fill_orbit_with_garbage(canvas, frames):

    garbage_keys = list(frames.keys())
    garbage_keys.remove('rocket_frame_1')
    garbage_keys.remove('rocket_frame_2')
    _, max_x = canvas.getmaxyx()
    while True:
        tics = get_garbage_delay_tics(settings.year)
        if not settings.game_is_over and tics:
            garbage = random.choice(garbage_keys)
            garbage_height, garbage_width = get_frame_size(frames[garbage])
            garbage_column = random.randint(
                settings.BORDER_WIDTH,
                max_x - garbage_width - settings.BORDER_WIDTH
            )
            garbage_uid = uuid.uuid4()
            asyncio_tools.coroutines.append(
                fly_garbage(
                    canvas,
                    garbage_column,
                    frames[garbage],
                    garbage_uid
                )
            )
            obstacles[garbage_uid] = Obstacle(
                settings.BORDER_WIDTH,
                garbage_column,
                garbage_height,
                garbage_width,
                uid=garbage_uid)
            await asyncio_tools.sleep(
                get_garbage_delay_tics(settings.year)
            )
        else:
            await asyncio_tools.sleep(1)


async def fly_garbage(canvas, column, garbage_frame, garbage_uid, speed=0.5):
    """Animate garbage, flying from top to bottom. \
        Сolumn position will stay same, as specified on start."""

    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - settings.BORDER_WIDTH)

    row = 0

    while row < rows_number:
        if obstacles[garbage_uid].get_has_a_hit():
            collision_row, collision_column = \
                obstacles[garbage_uid].get_collision_coordinates()
            asyncio_tools.coroutines.append(
                explode(canvas, collision_row, collision_column)
            )
            del obstacles[garbage_uid]
            return
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio_tools.sleep(1)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacles[garbage_uid].set_row(row)
    del obstacles[garbage_uid]
