import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    df = pd.read_csv("./logs/A2_md5.csv")
    plt.bar(range(2, 7, 1), df['means'], yerr=df['stds'], color='grey')
    plt.xlabel("Number of replicas")
    plt.xticks(np.arange(2, 7, step=1))
    plt.ylabel("Number of requests")
    plt.title("Hashring performance")
    plt.savefig("./plots/A2_md5.png")