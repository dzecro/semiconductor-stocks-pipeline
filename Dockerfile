# Official Python base image
# Minimal version — smaller file size, faster build
FROM python:3.11-slim

# Set the working directory inside the container
# All subsequent commands run from this path
WORKDIR /app

# Copy requirements first before copying the rest of the code
# Docker builds in layers — copying requirements separately means
# Docker can cache this layer and skip re-installing libraries
# on every rebuild as long as requirements.txt hasn't changed
COPY requirements.txt .

# ── FIX: Added --timeout and --retries flags ──────────────
# --timeout=300   wait up to 5 minutes per package download
#                 instead of the default 15 seconds
# --retries=5    retry failed downloads up to 5 times
#                before giving up
RUN pip install --no-cache-dir --timeout=300 --retries=5 -r requirements.txt

# Copy the rest of project files into the container
COPY . .

# Create the data directory inside the container
RUN mkdir -p data

# The command Docker runs when the container starts:
# 1. First runs load.py — executes the full ETL pipeline
# 2. Then launches the Streamlit dashboard on port 8501
CMD python load.py && streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0