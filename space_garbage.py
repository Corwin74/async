import uuid
import random
from obstacles_tools import obstacles, Obstacle
from curses_tools import draw_frame, get_frame_size
from asyncio_tools import coroutines, sleep
from explosion import explode


async def fill_orbit_with_garbage(canvas, frames):

    garbage_keys = list(frames.keys())
    garbage_keys.remove('rocket_frame_1')
    garbage_keys.remove('rocket_frame_2')
    _, max_x = canvas.getmaxyx()
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


async def fly_garbage(canvas, column, garbage_frame, garbage_uid, speed=0.5):
    """Animate garbage, flying from top to bottom. \
        Сolumn position will stay same, as specified on start."""

    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        if obstacles[garbage_uid].get_has_a_hit():
            collision_row, collision_column = \
                obstacles[garbage_uid].get_collision_coordinates()
            coroutines.append(explode(canvas, collision_row, collision_column))
            del obstacles[garbage_uid]
            return
        draw_frame(canvas, row, column, garbage_frame)
        await sleep(1)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacles[garbage_uid].set_row(row)
    del obstacles[garbage_uid]
