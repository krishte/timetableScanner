# Timetable Scanner

A full-stack application that scans a timetable uploaded as an image file and produces an ICS file containing all the information in the timetable. The back-end was made in Python using Flask for the REST API, OpenCV for image processing, and TesseractOCR for OCR, and the front-end was made with React. The application is currently deployed on an AWS EC2 instance using Docker and Kubernetes and is live at [timetablescan.com](http://timetablescan.com/). I'm hoping to extend the functionality of this application to scan calendar posters as well, but currently the limiting factor seems to be the accuracy of the OCR.
