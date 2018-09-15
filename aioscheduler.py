import asyncio
import time
from functools import partial

import crontab


async def task():
    print(asyncio.get_event_loop().time(), time.time(), sep='\t')


def schedule_delay(coro, delay, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(
        delay,
        partial(
            schedule_delay,
            coro,
            delay,
            loop
        )
    )


def schedule_cron(coro, cron_rule, loop):
    cron = crontab.CronTab(cron_rule)
    loop.call_at(
        loop.time() + cron.next(loop.time(), default_utc=True),
        partial(
            process_cron,
            coro,
            cron,
            loop
        )
    )


def process_cron(coro, cron, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_at(
        loop.time() + cron.next(loop.time(), default_utc=True),
        partial(
            process_cron,
            coro,
            cron,
            loop
        )
    )


def main():
    loop = asyncio.get_event_loop()
    schedule_cron(task, '* * * * *', loop)
    loop.run_forever()


if __name__ == '__main__':
    main()
