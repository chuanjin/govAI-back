# Use the official Python image with uv pre-installed or install it
FROM python:3.12-slim-bookworm

# The official uv image can also be used as a base, or we can copy it:
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory in the container
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a container
ENV UV_LINK_MODE=copy

# Install dependencies first for better layer caching
# We need pyproject.toml and uv.lock
COPY pyproject.toml uv.lock ./

# Install the project's dependencies
# --frozen ensures we use the exact versions from uv.lock
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY . .

# Final sync to install the project itself if it's defined as a package
RUN uv sync --frozen --no-dev

# Expose the port the app runs on
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["uv", "run", "uvicorn", "govai.main:app", "--host", "0.0.0.0", "--port", "8000"]
