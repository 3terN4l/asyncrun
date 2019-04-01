#!/usr/bin/env python3.7
#-*-coding:utf-8-*-

"""
Asynchronous Nerworking I/O using asyncio and Queue module

from asyncrun import AsyncRun
import asyncio
import time

async def test(i):
    print(f"started at {time.strftime('%X')} for {i} s")
    # other code
    await asyncio.sleep(i)
    print(f"finished at {time.strftime('%X')} for {i} s")
    

csrc = (x for x in range(4))
print(f"started at {time.strftime('%X')}")
ar = AsyncRun(csrc, test, ctimeout=5, print_exception=True)
ar.run()
print(f"finished at {time.strftime('%X')}")
"""

import asyncio

class AsyncRun:

    def __init__(self, csrc, cfunc,  qsize=1024, csize=256, ctimeout=None, print_exception=False, *args, **kargs):
        self.csrc = csrc
        self.cfunc = cfunc
        self.qsize = qsize
        self.csize = csize
        self.queue = asyncio.Queue()
        self.ctimeout = ctimeout
        self.end_csrc = 0
        self.print_exception = print_exception

    async def produce(self):
        # if queue is not full, put()
        while not self.queue.full():
            try:
                ip = next(self.csrc)
                await self.queue.put(ip)
                # print(f"PUT\t{ip}")
            except StopIteration:
                # csrc end
                self.end_csrc = 1
                # None marks csrc has ended
                await self.queue.put(None)
                break
        else:
            # queue is full. run consumer()
            await self.consumer()

    async def consumer(self):

        while not self.queue.empty():
            ig = await self.queue.get()
            # print(f"GET\t{ig}")
            if ig:
                try:
                    if self.ctimeout:
                        await asyncio.wait_for(self.cfunc(ig), timeout=self.ctimeout)
                    else:
                        await self.cfunc(ig)
                # don't exit current coroutine with exception
                # but not raise exception
                except asyncio.TimeoutError:
                    if self.print_exception:
                        print(f"[Error]-{self.cfunc.__name__}({ig}): asyncio.TimeoutError")
                except ConnectionRefusedError:
                    if self.print_exception:
                        print(f"[Error]-{self.cfunc.__name__}({ig}): ConnectionRefusedError")
                # Possible reasons of connectionAbortedError:
                # referer:https://stackoverflow.com/questions/51562067/connectionabortederror-winerror-10053-an-established-connection-was-aborted-b
                # Timeout or other network-level error.
                # Network connection died
                # Firewall closed the connection because it was open too long
                # Connection was closed before process has been finished
                # AntiVirus blocks the connection
                except ConnectionAbortedError:
                    if self.print_exception:
                        print(f"[Error]-{self.cfunc.__name__}({ig}): ConnectionAbortedError")
                except Exception as e:
                    if self.print_exception:
                        print(f"[Error]-{self.cfunc.__name__}({ig}): {e}")
            else:
                break
        else:
            # keep Coroutine up if csrc is not over yet
            # if end_csrc is not 0 and queue.empty() , run produce()
            if not self.end_csrc:
                await self.produce()
            else:
                pass

    async def _coordinate_control(self):
        tprod = [asyncio.create_task(self.produce())]
        tcons = [asyncio.create_task(self.consumer()) for i in range(self.csize)]
        tasks = tprod + tcons
        await asyncio.gather(*tasks, return_exceptions=False)

    def run(self):
        asyncio.run(self._coordinate_control())

