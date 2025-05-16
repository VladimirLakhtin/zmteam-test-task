FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN apt-get update && pip install uv

ENV PATH="/root/.cargo/bin:${PATH}"

# Copy project definition file
COPY ./pyproject.toml /app/

# Install dependencies using uv
RUN uv pip install --system --no-cache --requirement /app/pyproject.toml

# Copy the rest of the application code into the container at /app
COPY ./app /app/app
COPY ./.env /app/.env

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV MODULE_NAME="app.main"
ENV VARIABLE_NAME="app"
