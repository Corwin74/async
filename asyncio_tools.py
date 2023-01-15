import asyncio

coroutines = []
game_is_over = False
year = 1957


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)
