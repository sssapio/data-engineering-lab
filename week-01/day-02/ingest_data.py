#!/usr/bin/env python

import argparse

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm


def main():
    parser = argparse.ArgumentParser(
        description="Ingest NYC Yellow Taxi data into PostgreSQL"
    )

    parser.add_argument("--pg-user", required=True)
    parser.add_argument("--pg-pass", required=True)
    parser.add_argument("--pg-host", required=True)
    parser.add_argument("--pg-port", required=True)
    parser.add_argument("--pg-db", required=True)
    parser.add_argument("--target-table", required=True)

    args = parser.parse_args()

    pg_user = args.pg_user
    pg_pass = args.pg_pass
    pg_host = args.pg_host
    pg_port = args.pg_port
    pg_db = args.pg_db
    target_table = args.target_table

    url = (
        "https://github.com/DataTalksClub/"
        "nyc-tlc-data/releases/download/yellow/"
        "yellow_tripdata_2021-01.csv.gz"
    )

    dtype = {
        "VendorID": "Int64",
        "passenger_count": "Int64",
        "trip_distance": "float64",
        "RatecodeID": "Int64",
        "store_and_fwd_flag": "string",
        "PULocationID": "Int64",
        "DOLocationID": "Int64",
        "payment_type": "Int64",
        "fare_amount": "float64",
        "extra": "float64",
        "mta_tax": "float64",
        "tip_amount": "float64",
        "tolls_amount": "float64",
        "improvement_surcharge": "float64",
        "total_amount": "float64",
        "congestion_surcharge": "float64",
    }

    parse_dates = [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
    ]

    engine = create_engine(
        f"postgresql+psycopg://"
        f"{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    )

    print(f"Connecting to PostgreSQL at {pg_host}:{pg_port}")
    print(f"Target table: {target_table}")

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=100000,
    )

    first = True

    for df_chunk in tqdm(df_iter):

        if first:
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists="replace",
                index=False,
            )

            print("Table created")
            first = False

        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append",
            index=False,
        )

        print(f"Inserted {len(df_chunk)} rows")


if __name__ == "__main__":
    main()