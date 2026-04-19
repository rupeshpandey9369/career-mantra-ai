# Use the official Python image
FROM python:3.10-slim

# Create a non-root user for Hugging Face Spaces
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirement files first
COPY --chown=user requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents
COPY --chown=user . $HOME/app

# Expose the port Hugging Face uses
EXPOSE 7860

# Command to run on start using eventlet for Flask-SocketIO compatibility
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:7860", "app:application"]
