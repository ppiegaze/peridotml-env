import os
import tempfile
import zipfile
from urllib.request import urlretrieve

import pandas as pd
import polars as pl
from flytekit import Resources, StructuredDataset, task, workflow
from flytekit.types.directory import FlyteDirectory


@task(cache=True, cache_version="v1", requests=Resources(cpu="2", mem="4Gi"))
def download_movielens_20m() -> FlyteDirectory:
    """Download the movie lens 20m example"""
    tmp_dir = tempfile.mkdtemp(prefix="movie-lens")
    print(f"[1] downloading movielens 20m to {tmp_dir}")
    url = "https://files.grouplens.org/datasets/movielens/ml-20m.zip"
    dst = os.path.join(tmp_dir, "ml-20m.zip")
    urlretrieve(url, dst)
    print("[2] extracting file from ml-20m.zip")
    with zipfile.ZipFile(dst, "r") as zip_ref:
        zip_ref.extractall(tmp_dir)

    return FlyteDirectory(path=str(tmp_dir))


@task
def get_average_ratings_polars(
    fd: FlyteDirectory, streaming: bool
) -> StructuredDataset:
    path = os.path.join(str(fd.download()), "ml-20m", "ratings.csv")
    df = pl.scan_csv(path)

    avg_rating = (
        df.groupby("movieId").agg(pl.avg("rating")).collect(streaming=streaming)
    )

    return StructuredDataset(dataframe=avg_rating)


@task
def get_average_ratings_pandas(fd: FlyteDirectory) -> StructuredDataset:
    path = os.path.join(str(fd.download()), "ml-20m", "ratings.csv")
    df = pd.read_csv(path)

    avg_rating = df.groupby("movieId")[["rating"]].mean()

    return StructuredDataset(dataframe=avg_rating)


@workflow
def wf():
    movielens = download_movielens_20m()
    get_average_ratings_polars(fd=movielens, streaming=True)
    get_average_ratings_polars(fd=movielens, streaming=False)
    get_average_ratings_pandas(fd=movielens)
