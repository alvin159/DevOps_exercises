FROM python:3.10-slim

WORKDIR /app/tests

# Copy requirements and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy test files and source code
COPY . .

# Default command to run the tests
CMD ["pytest", "test_api.py"]
