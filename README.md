# Timetable Scanner

## Description

A full-stack application that scans a timetable uploaded as an image file and produces an ICS file containing all the information in the timetable. The back end was made in Python using Flask for the REST API, OpenCV for image processing, and TesseractOCR for OCR, and the front end was made with React. The application is currently deployed on an AWS EC2 instance using Gunicorn, Docker, and NGINX and is live at [timetablescan.com](http://timetablescan.com/). I'm hoping to extend the functionality of this application to scan calendar posters as well, but currently, the limiting factor seems to be the accuracy of the OCR. I'm also hoping to incorporate some form of ML to be able to handle different timetable formats, but first I need to build a database of timetables.

## Installation

### Server

For ease of transferability, the server side is packaged with Docker. Therefore, please ensure you have Docker installed before continuing. The Dockerfile uses pipenv and the Pipfile to install all required dependencies.

In the server directory, run the following commands to build the Docker image and run it in a container:
'''
docker build -t timetable-scanner .
docker run --rm -p 5000:5000 timetable-scanner
'''
Note that 'timetable-scanner' is the name of the image and this can be replaced with anything. The server is currently set to run on port 5000, but this can be changed by altering the port mapping in the 'docker run' command.

### Client

Please install both Node and npm before continuing. The application currently runs with node version 18.16.0 and npm version 9.8.1.

In the client directory, run the following commands to install all packages and start a development server:
'''
npm install
npm start
'''
