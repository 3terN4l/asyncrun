#!/usr/bin/env python3.7
#-*-coding:utf-8-*-

import asyncio
import time
from asyncrun import AsyncRun

async def test(i):
    print(f"started at {time.strftime('%X')} for {i} s")
    await asyncio.sleep(i)
    print(f"finished at {time.strftime('%X')} for {i} s")
    

csrc = (x for x in range(10))
print(f"started at {time.strftime('%X')}")
ar = AsyncRun(csrc, test, ctimeout=5, print_exception=False)
ar.run()
print(f"finished at {time.strftime('%X')}")
