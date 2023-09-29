# Timetable Scanner

## Description

A full-stack application that scans a timetable uploaded as an image file and produces an ICS file containing all the information in the timetable. The back end was made in Python using Flask for the REST API, OpenCV for image processing, and TesseractOCR for OCR, and the front end was made with React. The application is currently deployed on an AWS EC2 instance using Gunicorn, Docker, and NGINX and is live at [timetablescan.com](http://timetablescan.com/). I'm hoping to extend the functionality of this application to scan calendar posters as well, but currently, the limiting factor seems to be the accuracy of the OCR. I'm also hoping to incorporate some form of ML to be able to handle different timetable formats, but first I need to build a database of timetables.

## Installation

### Server

For ease of transferability, the server side is packaged with Docker. Therefore, please ensure you have Docker installed before continuing. The Dockerfile uses pipenv and the Pipfile to install all required dependencies.

In the server directory, run the following commands to build the Docker image and run it in a container:

```
docker build -t timetable-scanner .
docker run --rm -p 5000:5000 timetable-scanner
```

Note that 'timetable-scanner' is the name of the image and this can be replaced with anything. The server is currently set to run on port 5000, but this can be changed by altering the port mapping in the 'docker run' command.

### Client

Please install both Node and npm before continuing. The application currently runs with Node version 18.16.0 and npm version 9.8.1.

In the client directory, run the following commands to install all packages and start a development server:

```
npm install
npm start
```

Depending on the location of the server, you may need to change the links for all the POST requests made in App.js and TimetableEdit.js.

## Overview
### Server
The following is a high-level overview of how the Python server code works:
- Receives the uploaded image from the front end and applies image-processing techniques including Gaussian blurring, adaptive thresholding, Canny edge-detection, erosion, and dilation to increase the definition of vertical and horizontal lines in the image
- Runs a Probabilistic Hough Line Transform to identify lines in the resulting processed image
- Sorts the lines found by the Transform into either horizontal lines or vertical lines
- Uses the horizontal lines to search the image row-by-row starting at the top for a row containing the days of the week
- Uses the vertical lines to search the image column-by-column starting at the left for a column containing times and changes all the times found into standard 24-hour format
- Finds each smallest box formed by horizontal and vertical lines and searches the box for text
- Uses the text found together with the day columns which the box overlaps with and the time rows which the box also overlaps with to create an event.
- Finally, uses the icalendar module to put all the events into an ICS file and returns this

### Client
The following is a high-level overview of how the React client code works:
- The home page contains fields to upload an image and select start/end dates for the uploaded timetable. It also contains examples of timetables on which the program works.
- After uploading the timetable image to the server and receiving a response, the client displays the first edit stage which allows the user to see the times found by the program and edit them if necessary
  - This step helps to improve the accuracy of finding the times for each event and proved necessary when Tesseract seemed to struggle with certain fonts
- After editing the times, all the events found by the application are overlayed onto the original timetable image, and the user can hover over each event to see the event details found and set by the program.
- The user can edit these details and then select which events to include in the ICS file before downloading it.

| Home Page | Edit Times | Select Events |
| ------------- | ------------- | ------------- |
|![Client-1](https://github.com/krishte/timetableScanner/assets/46422100/573c6f30-ca91-424f-a713-5019a06bf09e)|![Client-2](https://github.com/krishte/timetableScanner/assets/46422100/4db72594-0435-4b95-912d-a2961fc299ff)|![Client-3](https://github.com/krishte/timetableScanner/assets/46422100/c9c556e2-fcfb-4347-87f8-5b36d2bc7e8e)|
