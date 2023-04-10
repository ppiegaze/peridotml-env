from flytekit import task, workflow


def fake(i: int) -> int:
    return i


fake(i=fake(i=1))


@task
def t(a: int) -> int:
    return a + 1


@workflow
def wf() -> int:
    return t(a=t(a=10))
