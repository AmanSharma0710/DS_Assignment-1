# from grequests import async
import aiohttp
import asyncio
import time
import matplotlib.pyplot as plt
import csv
import requests
import sys

url = "http://localhost:5000"
endpoint = "/home"

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json(content_type=None)
    
async def main(n_requests=10000):
    async with aiohttp.ClientSession() as session:
        res = await asyncio.gather(*[fetch(session, url+endpoint) for _ in range(n_requests)])
    result = {}
    for i in res:
        server_id = int(i['message'][19:])
        if server_id in result.keys():
            result[server_id] += 1
        else:
            result[server_id] = 1
    return result

if __name__ == "__main__":
        
        n_requests = 10000
        start_time = time.time()
        # get result as json
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(main(n_requests))
        end_time = time.time()
        print(result)

        # find mean and standard deviation
        mean = 0
        for i in result.values():
            mean += i
        mean /= len(result.values())
        std = 0
        for i in result.values():
            std += (i - mean)**2
        std /= len(result.values())
        std = std**0.5
        time_taken = end_time - start_time

        # write to csv
        with open("./logs/A2_md5.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow([mean, std, time_taken])


