import os
import tempfile
import time
import zipfile
from urllib.request import urlretrieve

import numpy as np
import pandas as pd
import polars as pl
from flytekit import Resources, WorkflowFailurePolicy, task, workflow
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile


@task(cache=True, cache_version="v2", requests=Resources(cpu="2", mem="4Gi"))
def download_movielens_20m_ratings() -> FlyteDirectory:
    """Download the movie lens 20m example"""
    print("[1] downloading movielens 20m")
    name = "ml-20m.zip"
    src = os.path.join("https://files.grouplens.org/datasets/movielens/", name)
    dst = os.path.join(tempfile.mkdtemp(), name)
    urlretrieve(src, dst)

    print("[2] extracting file from ml-20m.zip")
    tmp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(dst, "r") as zip_ref:
        (path,) = zipfile.Path(zip_ref).iterdir()

        zip_ref.extractall(tmp_dir)

    return FlyteFile(path=os.path.join(tmp_dir, path.name, "ratings.csv"))


@task(
    cache=True,
    cache_version="v7",
    requests=Resources(cpu="4", mem="16Gi"),
    limits=Resources(cpu="4", mem="16Gi"),
)
def create_fake_dataset() -> FlyteFile:
    options = list(range(10))
    cat = np.random.choice(options, size=100000000)
    x = np.random.normal(size=100000000)

    tmp = tempfile.mktemp()
    df = pd.DataFrame({"movieId": cat, "rating": x})
    df.to_csv(tmp, index=False)

    return FlyteFile(path=str(tmp))


@task(requests=Resources(cpu="2", mem="1.1Gi"), limits=Resources(cpu="2", mem="1.1Gi"))
def get_average_ratings_polars(f: FlyteFile, streaming: bool) -> FlyteFile:
    path = f.download()
    df = pl.scan_csv(path)

    # avg_rating = (
    #     df.groupby("movieId").agg(pl.avg("rating")).collect(streaming=streaming)
    # )
    tmp = tempfile.mktemp()
    if streaming:
        df.sink_parquet(tmp)
    else:
        df.collect().write_parquet(tmp)
    return FlyteFile(path=str(tmp))
    # return StructuredDataset(dataframe=avg_rating)


@task(requests=Resources(cpu="2", mem="1.1Gi"), limits=Resources(cpu="2", mem="1.1Gi"))
def get_average_ratings_pandas(f: FlyteFile) -> FlyteFile:
    path = f.download()
    df = pd.read_csv(path)
    # avg_rating = df.groupby("movieId")[["rating"]].mean()
    tmp = tempfile.mktemp()
    df.to_parquet(tmp, index=False)

    # return StructuredDataset(dataframe=avg_rating)
    return FlyteFile(path=str(tmp))


@workflow(failure_policy=WorkflowFailurePolicy.FAIL_AFTER_EXECUTABLE_NODES_COMPLETE)
def wf():
    ratings = create_fake_dataset()
    get_average_ratings_polars(f=ratings, streaming=True).with_overrides(
        name="get_average_ratings_polars_streaming"
    )
    get_average_ratings_polars(f=ratings, streaming=False)
    get_average_ratings_pandas(f=ratings)

    break_memory()


@task(requests=Resources(cpu="2", mem="1Gi"))
def break_memory():
    array = []
    while True:
        array.extend([1.0] * 10000)
        time.sleep(0.01)
