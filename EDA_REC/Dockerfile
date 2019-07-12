#Use an official Python runtime as a parent image
FROM eda_rec_basepython:1.0

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8052

# Define environment variable

# Run app.py when the container launches
#CMD [ "/bin/sh -c","/usr/local/bin/gunicorn", "-D","--config=guncontainer.py","init:app"]
ENTRYPOINT [ "/bin/sh","-c","/usr/local/bin/gunicorn --config=guncontainer.py init:app"]
