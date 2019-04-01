#!/usr/bin/env python3.7
#-*-coding:utf-8-*-

import asyncio
import time
from asyncrun import AsyncRun

async def test(i):
    reader, writer = await asyncio.open_connection(*i)
    writer.write('hello\r\n'.encode())
    echo = await reader.read()
    print(f"{i}\t{echo}")
    writer.close()
    await writer.wait_closed()
    

csrc = ((f"{x}", 80) for x in ['www.baidu.com', 'www.so.com', 'www.163.com', 'www.qq.com'])
print(f"started at {time.strftime('%X')}")
ar = AsyncRun(csrc, test, ctimeout=5, print_exception=False)
ar.run()
print(f"finished at {time.strftime('%X')}")
