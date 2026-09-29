import pandas as pd
import matplotlib.pyplot as plt
import os
import ast


def read_dataset(dataset_path):
    porto_df = pd.read_csv(dataset_path)
    for column in porto_df.columns:
        print(column, porto_df[column].dtype)
    return porto_df


def plot_missing_data(df):
    counts = df["MISSING_DATA"].value_counts(normalize=True)
    counts.index = counts.index.map(lambda x: str(x).strip().lower() == "true")
    not_missing = counts.get(False, 0)
    missing = counts.get(True, 0)
    print("Missing", missing, "Not missing:", not_missing)

    plt.bar(["Not missing", "Missing"], [not_missing, missing])
    plt.ylabel("Proportion")
    plt.ylim(0, 1)

    os.makedirs("visualizations", exist_ok=True)
    plt.savefig("visualizations/missing_data.png")
    plt.close()


def check_missing_polylines(df):
    missing_rows = df[df["MISSING_DATA"] == True]
    not_missing_rows = df[df["MISSING_DATA"] == False]

    print(f"Rows with MISSING_DATA=True: {len(missing_rows)}")
    print(f"Rows with MISSING_DATA=False: {len(not_missing_rows)}")

    missing_rows = missing_rows.copy()
    missing_rows["num_points"] = missing_rows["POLYLINE"].apply(
        lambda x: len(ast.literal_eval(x)) if pd.notna(x) else 0
    )

    print("\nPOLYLINE point counts for MISSING_DATA=True rows:")
    print(missing_rows["num_points"].value_counts())

    non_empty_but_flagged = (missing_rows["num_points"] > 0).sum()
    print(f"\nRows flagged as missing but with non-empty POLYLINE: {non_empty_but_flagged}")


def check_range(df):
    for column in df.columns:
        if df[column].dtype == "float64" or df[column].dtype == "int64":
            print(column, "Range:", df[column].min(), df[column].max())


def check_trip_ids(df):
    print("Total trips:", len(df))
    print("Unique TRIP_ID:", df["TRIP_ID"].nunique())
    print("Duplicate TRIP_ID rows:", df["TRIP_ID"].duplicated().sum())


def plot_call_types(df):
    counts = df["CALL_TYPE"].value_counts(normalize=True)
    print("Call type proportions:\n", counts)

    plt.bar(counts.index, counts.values)
    plt.ylabel("Proportion")
    plt.xlabel("CALL_TYPE")

    os.makedirs("visualizations", exist_ok=True)
    plt.savefig("visualizations/call_types.png")
    plt.close()


def plot_day_types(df):
    counts = df["DAY_TYPE"].value_counts(normalize=True)
    print("Day type proportions:\n", counts)

    plt.bar(counts.index, counts.values)
    plt.ylabel("Proportion")
    plt.xlabel("DAY_TYPE")

    os.makedirs("visualizations", exist_ok=True)
    plt.savefig("visualizations/day_types.png")
    plt.close()


def plot_polyline_lengths(df, sample_size=100000):
    sample = df["POLYLINE"].dropna().sample(min(sample_size, len(df)), random_state=0)
    lengths = sample.apply(lambda x: len(ast.literal_eval(x)))
    print("POLYLINE point count stats:\n", lengths.describe())

    plt.hist(lengths, bins=50)
    plt.xlabel("Number of GPS points")
    plt.ylabel("Trip count")

    os.makedirs("visualizations", exist_ok=True)
    plt.savefig("visualizations/polyline_lengths.png")
    plt.close()


def plot_sample_trajectories(df, n=20):
    sample = df[df["MISSING_DATA"] == False]["POLYLINE"].dropna().sample(n, random_state=0)

    for polyline in sample:
        points = ast.literal_eval(polyline)
        if len(points) < 2:
            continue
        lons, lats = zip(*points)
        plt.plot(lons, lats, linewidth=0.5)

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    os.makedirs("visualizations", exist_ok=True)
    plt.savefig("visualizations/sample_trajectories.png")
    plt.close()


def main(dataset_path="porto/porto.csv"):
    porto_df = read_dataset(dataset_path=dataset_path)
    print(porto_df.columns)
    plot_missing_data(porto_df)
    check_missing_polylines(porto_df)
    check_range(porto_df)
    check_trip_ids(porto_df)
    plot_call_types(porto_df)
    plot_day_types(porto_df)
    plot_polyline_lengths(porto_df)
    plot_sample_trajectories(porto_df)


if __name__ == "__main__":
    main()