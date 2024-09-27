FROM fedora:latest
WORKDIR /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

COPY . /app

RUN uv venv
RUN uv pip install .
