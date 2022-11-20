import asyncio

from settings import GAME_TICK_RATE


class Territory:
    def __init__(self, pos_x: int, pos_y: int):
        self.pos_x = pos_x
        self.pos_y = pos_y


class Player:
    def __init__(
            self,
            territories: list[Territory],
            money: int = 1000,
            workers: int = 100,
            army: int = 20,
            tech_level: int = 1
    ):
        self.territories = territories
        self.money = money
        self.workers = workers
        self.army = army
        self.tech_level = tech_level


async def game_update(player: Player) -> None:
    await asyncio.sleep(GAME_TICK_RATE)

    player.money += player.workers // 4
    player.money -= player.army // 4

