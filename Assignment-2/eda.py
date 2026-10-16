import json

import pandas as pd


def main():
    with open("porto/porto.csv", "r", encoding="utf-8") as file:
        df = pd.read_csv(file)


if __name__ == "__main__":
    main()
