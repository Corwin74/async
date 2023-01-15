import asyncio

coroutines = []
year = 1957
game_is_over = False


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)
