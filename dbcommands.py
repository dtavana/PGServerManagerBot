import aiomysql
import asyncio
import config as cfg


async def dzconnect(bot):
    async with aiomysql.create_pool(host=cfg.dzhost, port=cfg.dzport,
        user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, loop=loop) as pool:
        async with pool.get() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                bot.dzcur = cur
    bot.loop.create_task(dzconnect())


async def disconnect():
    async with aiomysql.create_pool(host=cfg.disuser, port=cfg.disport,
        user=cfg.disuser, password=cfg.dispass, db = cfg.disschema, loop=loop) as pool:
        async with pool.get() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                cur.execute('SELECT PlayerUID FROM users WHERE DiscordUser = TwiSt#2791;')
                initData = cur.fetchone()
                result = await asyncio.gather(initData)
                print(result)
    bot.loop.create_task(disconnect())
