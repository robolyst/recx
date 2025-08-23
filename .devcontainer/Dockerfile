FROM python:3.12.4-bullseye

RUN apt update

# build-essential: cvxopt, cvxpy
# python-dev: cvxopt
# libopenblas-dev: cvxopt, cvxpy
# libblas-dev: cvxopt, cvxpy
# liblapack-dev: cvxopt, cvxpy
# libsuitesparse-dev: cvxopt
# cmake: cvxpy
# glpk-utils: cvxpy
# libglpk-dev: cvxpy
# glpk-doc: cvxpy
# python3-swiglpk: cvxpy
# RUN apt install -y build-essential python3-dev libopenblas-dev libblas-dev liblapack-dev libsuitesparse-dev cmake glpk-utils libglpk-dev glpk-doc python3-swiglpk

# Setup the package manager
RUN pip3 install --upgrade pip
RUN pip3 install uv


# Install python packages
ADD pyproject.toml /app/pyproject.toml
ADD uv.lock /app/uv.lock
RUN uv pip install -r /app/pyproject.toml --system

# Install python dev packages
RUN (cd /app && uv pip install -r /app/pyproject.toml --system --group dev)

# Prevent creating a virtual environment every time you run a uv command:
ENV UV_PROJECT_ENVIRONMENT=/usr/local/

# Setup jupyter notebooks to run from within
# vs code
ADD .devcontainer/jupyter_notebook_config.py /root/.jupyter/jupyter_notebook_config.py

# Install oh my zsh
RUN apt install -y git zsh wget
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true
ENV SHELL /usr/bin/zsh


# Git needs some sort of editor so that you can do things
# like `git commit --amend` or `git rebase -i`
RUN apt install -y vim
