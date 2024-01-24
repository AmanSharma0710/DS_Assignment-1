# from grequests import async
import aiohttp
import asyncio
import time
import matplotlib.pyplot as plt
import csv
import requests

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

    # get the number of servers active
    response = requests.get(f"{url}/rep")
    print(response.json())
    n_servers = response.json()['message']['N']

    # make the number of servers 1
    if n_servers > 1:
        response = requests.delete(f"{url}/rm", json={"n": n_servers-1, "hostnames": []})
    elif n_servers < 1:
        response = requests.post(f"{url}/add", json={"n": 1-n_servers, "hostnames": []})

    print(response.json())

    means = []
    stds = []
    for i in range(5):
        print(f"Run {i+1}")
        response = requests.post(f"{url}/add", json={"n": 1, "hostnames": []})
        print(response.json())
        time.sleep(5)

        response = requests.get(f"{url}/rep")
        print(response.json())

        
        n_requests = 10
        start_time = time.time()
        # get result as json
        result = asyncio.run(main(n_requests))
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

        means.append(mean)
        stds.append(std)

    print(result)
    # plot the means in a bar graph and standard deviation as error bars
    plt.bar(range(5), means, yerr=stds, color='grey')
    plt.xlabel("Server ID")
    plt.ylabel("Number of requests")
    plt.title("Hashring performance")
    plt.savefig("./plots/A2.png")



