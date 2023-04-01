## M1 Setup Guide
We need a special setup to run our code directly on M1 hardware. Luckily,
using an M1 chip requires minimal work arounds. Note: docker and GHA are useful for
seeing how code will run in production. It will not cause a problem now, but could if
we change our stack a lot.

1. Install miniconda [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html). Alternatively, try using micromamba.
2. Create a new python 3.9 environment because the m1 tensorflow library, `tensorflow-macos` requires it.
3. `pip install m1-requirements.txt`



https://github.com/romkatv/powerlevel10k#getting-started


ssh-keygen -t ed25519 -C "esad@peridotml.io"