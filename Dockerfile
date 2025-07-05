FROM python:3.10-slim-bookworm

# Set the working directory inside the container
WORKDIR /app


# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container

COPY ./app ./app
# Set the Python path to include the current directory
ENV PYTHONPATH=/app

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]