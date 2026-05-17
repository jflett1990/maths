FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
COPY configs ./configs
RUN pip install --no-cache-dir -e .
CMD ["python", "scripts/run_paper.py", "--config", "configs/base.yaml"]
