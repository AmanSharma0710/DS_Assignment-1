# from grequests import async
import aiohttp
import asyncio
import time
import matplotlib.pyplot as plt
import csv
import numpy as np

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
    result = asyncio.run(main(n_requests))
    end_time = time.time()

    print(result)
    print(f"Time taken: {end_time - start_time} seconds")
    print(f"Throughput: {n_requests/(end_time - start_time)} requests/second")

    # plot the result
    plt.bar([1, 2, 3], result.values(), color='grey')
    plt.xticks(np.arange(1, 4, step=1))
    plt.xlabel("Server ID")
    plt.ylabel("Number of requests")
    plt.title("Hashring performance")
    plt.savefig("./plots/A1_custom.png")


