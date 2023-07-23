# Use an official Python runtime as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container and install the Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install the German language model for spaCy
RUN python -m spacy download de_core_news_md

# Copy the rest of the application files into the container
COPY . /app/

# Expose the port that Streamlit runs on (default is 8501)
EXPOSE 8501

# Set the command to run the Streamlit app when the container starts
CMD ["streamlit", "run", "app.py"]
