import cv2
import pytesseract
from pytesseract import Output
import numpy as np
import math
import re
from datetime import timedelta
from dateparser.search import search_dates
from icalendar import Calendar, Event
from imutils.object_detection import non_max_suppression
'''
Calendar formats:
 - Month e.g. July 2023
 - Year calendar (months vertical)
 - Year calendar (months horizontal)
 - Timetable (days vertically, times horizontally) 
'''

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
images = ["timetable.png", "timetable3.png", "timetable5.png", "timetable2.jpg", "timetable4.jpg", "timetable6.jpg"]

# returns dictionary with keys beign dates in dd/mm/yyyy format and values being lists of pairs where each pair is (24-hour time, description of activitylll)



def timetableScanner(img):
    def relsize_adjust(x):
        return math.ceil((min(img.shape[0], img.shape[1])/x))
    
    
    # =============================================================================
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray, (3,3), 0)
    # thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
    # 
    # #horizontal lines
    # kernel_horizontal = np.ones((1, 10),np.uint8)
    # opening_horizontal = cv2.erode(thresh, kernel_horizontal, iterations = 1)
    # 
    # #vertical lines
    # kernel_vertical = np.ones((20,1), np.uint8)
    # opening_vertical = cv2.erode(thresh, kernel_vertical, iterations=1)
    # edges = cv2.Canny(gray, 50, 200, apertureSize=3)
    # =============================================================================
    
    react_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    kernel_horizontal = np.ones((1, 10),np.uint8)
    kernel_vertical = np.ones((10, 1),np.uint8)
    
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 3, 2)
    
    edges = cv2.Canny(thresh, 50, 200, apertureSize=3)
    edges2 = cv2.Canny(gray, 50, 200, apertureSize=3)
    
    opening_horizontal = cv2.erode(edges, kernel_horizontal, iterations = 1)
    dilation_horizontal = cv2.dilate(opening_horizontal, react_kernel, iterations = 1)
    
    #Second method catches some lines that are missed due to blurring
    opening_horizontal2 = cv2.erode(edges2, kernel_horizontal, iterations = 1)
    dilation_horizontal2 = cv2.dilate(opening_horizontal2, react_kernel, iterations = 1)
    
    opening_vertical = cv2.erode(edges, kernel_vertical, iterations = 1)
    dilation_vertical = cv2.dilate(opening_vertical, react_kernel, iterations = 1)
    
    opening_vertical2 = cv2.erode(edges2, kernel_vertical, iterations = 1)
    dilation_vertical2 = cv2.dilate(opening_vertical2, react_kernel, iterations = 1)
    
    
    
    #This is the raw output of HoughLines which may contains all types of lines in either list
    
    raw_horizontal_lines = np.concatenate((cv2.HoughLinesP(dilation_horizontal, rho=1, theta=np.pi/1440, threshold=50, minLineLength=50, maxLineGap=15), cv2.HoughLinesP(dilation_horizontal2, rho=1, theta=np.pi/1440, threshold=50, minLineLength=50, maxLineGap=15)))
    raw_vertical_lines = np.concatenate((cv2.HoughLinesP(dilation_vertical, rho=1, theta=np.pi/1440, threshold=50, minLineLength=50, maxLineGap=15), cv2.HoughLinesP(dilation_vertical2, rho=1, theta=np.pi/1440, threshold=50, minLineLength=50, maxLineGap=15)))
            
    
    #Ensure each lists contains only the corresponding lines in the correct format with (x1,y1) <= (x2,y2)
    
    horizontal_lines, vertical_lines = [], []
     
    for line in raw_horizontal_lines:
        x1,y1,x2,y2=line[0]
        #cv2.line(img,(x1,y1),(x2,y2),(0,255,0),1)
        if (abs((y2-y1)/(x2-x1))<=0.025):
            #cv2.line(img,(x1,y1),(x2,y2),(0,255,0),1)
            horizontal_lines.append([[min(x1,x2),min(y1,y2)],[max(x1,x2),max(y1,y2)]])
        
    for line in raw_vertical_lines:
        x1,y1,x2,y2=line[0]
        if (x2==x1 or abs((y2-y1)/(x2-x1))>=40):
            #cv2.line(img,(x1,y1),(x2,y2),(0,255,0),1)
            vertical_lines.append([[min(x1,x2),min(y1,y2)],[max(x1,x2),max(y1,y2)]])
            
    #finds the list in lines_list that contains the lines with x or y coordinate coord or returns -1 if no such list exists
    def line_search(lines_list, coord):
        for i in range(len(lines_list)):
            if abs(lines_list[i][0]-coord) <= 20:
                return i
        return -1
    
    #determines if the two intervals (a1,a2) and (b1,b2) overlap with some leeway
    def overlap(a1, a2, b1, b2):
        return ((a1 >= b1-25 and a1 <= b2+25) or (a2 >= b1-25 and a2 <= b2+25))
    
    horizontal_lines.sort()
    vertical_lines = sorted(vertical_lines, key=lambda x: x[0][1])
            
    #Could keep track of (y1,y2) at start of each list but only works if lines are really flat?
    #A list of lists where each nested list contains a y coordinate followed by all lines at that y coordinate (for grouped_horizontal_lines)
    #Below line contains both lists initialized with lines for borders of image
    #grouped_horizontal_lines, grouped_vertical_lines = [[0, [[0,0], [img.shape[1],0]]], [img.shape[0], [[0,img.shape[0]], [img.shape[1], img.shape[0]]]]], [[0, [[0,0], [0,img.shape[0]]]], [img.shape[1], [[img.shape[1],0], [img.shape[1], img.shape[0]]]]]
    grouped_horizontal_lines, grouped_vertical_lines = [], []
    for line in horizontal_lines:
        [[x1,y1], [x2,y2]] = line
        ind = line_search(grouped_horizontal_lines, y1)
        if (ind==-1):
            grouped_horizontal_lines.append([y1, line])
        else:
            minx = x1
            maxx = x2
            newlines = []
            for overlap_line in grouped_horizontal_lines[ind][1:]:
                if (overlap(x1,x2, overlap_line[0][0], overlap_line[1][0])):
                    minx = min(minx, overlap_line[0][0])
                    maxx = max(maxx, overlap_line[1][0])
                else:
                    newlines.append(overlap_line)
            newlines.append([[minx, y1], [maxx, y2]])
            grouped_horizontal_lines[ind][1:] = newlines
            
    for line in vertical_lines:
        [[x1,y1], [x2,y2]] = line
        ind = line_search(grouped_vertical_lines, x1)
        if (ind==-1):
            grouped_vertical_lines.append([x1, line])
        else:
            miny = y1
            maxy = y2
            newlines = []
            for overlap_line in grouped_vertical_lines[ind][1:]:
                if (overlap(y1,y2, overlap_line[0][1], overlap_line[1][1])):
                    miny = min(miny, overlap_line[0][1])
                    maxy = max(maxy, overlap_line[1][1])
                else:
                    newlines.append(overlap_line)
            newlines.append([[x1, miny], [x2, maxy]])
            grouped_vertical_lines[ind][1:] = newlines
            
    grouped_horizontal_lines.sort()
    grouped_vertical_lines.sort()
            
    for y_lines in (grouped_vertical_lines+grouped_horizontal_lines):
        for line in y_lines[1:]:
            [[x1,y1], [x2,y2]] = line
            cv2.line(img,(x1,y1),(x2,y2),(0,255,0),3)
            
    #image preprocessing for pytesseract    
    thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1]
    #blur2 = cv2.GaussianBlur(thresh1, (3,3), 0)
    
            
    daysrow = -1
    day_to_coord = {}
    for i in range(len(grouped_horizontal_lines)-1):
        d = pytesseract.image_to_data(thresh1[grouped_horizontal_lines[i][0]:grouped_horizontal_lines[i+1][0], grouped_vertical_lines[0][0]:grouped_vertical_lines[-1][0]], output_type=Output.DICT)
        n_boxes = len(d['text'])
    
        for k in range(n_boxes):
            if int(d['conf'][k]) >= 0 and d['text'][k].strip() != "":
                (x, y, w, h) = (d['left'][k], d['top'][k], d['width'][k], d['height'][k])
                text = d['text'][k].strip()
                if len(text) >= 3 and text.lower() != "day":
                    for day in days:
                        if day.lower().startswith(text.lower()):
                            day_to_coord[day] = (x+grouped_vertical_lines[0][0],y+grouped_horizontal_lines[i][0],x+w+grouped_vertical_lines[0][0],y+h+grouped_horizontal_lines[i][0])
                            img = cv2.rectangle(img, (day_to_coord[day][0], day_to_coord[day][1]), (day_to_coord[day][2], day_to_coord[day][3]), (255, 0, 0), 2)
                            daysrow = i
                            break
        if (daysrow != -1):
            break
    
    assert(daysrow != -1)
    
    #timescol = -1
    #for i in range(len(grouped_vertical_lines)-1):
        
    
#Text detection using EAST: finds bounding boxes on all words but not accurate enough
# =============================================================================
#     colored_blur = cv2.GaussianBlur(img, (3,3), 0)
#     imgresized32 = cv2.resize(colored_blur, (int(img.shape[1]/32)*32, int(img.shape[0]/32)*32))  
#     net = cv2.dnn.readNet("frozen_east_text_detection.pb")
#     blob = cv2.dnn.blobFromImage(imgresized32, 1.0, (int(img.shape[1]/32)*32, int(img.shape[0]/32)*32), (123.68, 116.78, 103.94), True, False)
# 
#     outputLayers = []
#     outputLayers.append("feature_fusion/Conv_7/Sigmoid")
#     outputLayers.append("feature_fusion/concat_3")
#     
#     net.setInput(blob)
#     (scores, geometry) = net.forward(outputLayers)
#     (numRows, numCols) = scores.shape[2:4]
#     rects = []
#     confidences = []
#     # loop over the number of rows
#     for y in range(0, numRows):
#         # extract the scores (probabilities), followed by the geometrical
#         # data used to derive potential bounding box coordinates that
#         # surround text
#         scoresData = scores[0, 0, y]
#         xData0 = geometry[0, 0, y]
#         xData1 = geometry[0, 1, y]
#         xData2 = geometry[0, 2, y]
#         xData3 = geometry[0, 3, y]
#         anglesData = geometry[0, 4, y]
#     
#         for x in range(0, numCols):
#     		# if our score does not have sufficient probability, ignore it
#             # Set minimum confidence as required
#             if scoresData[x] < 0.5:
#                 continue
#     		# compute the offset factor as our resulting feature maps will
#             #  x smaller than the input image
#             (offsetX, offsetY) = (x * 4.0, y * 4.0)
#             # extract the rotation angle for the prediction and then
#             # compute the sin and cosine
#             angle = anglesData[x]
#             cos = np.cos(angle)
#             sin = np.sin(angle)
#             # use the geometry volume to derive the width and height of
#             # the bounding box
#             h = xData0[x] + xData2[x]
#             w = xData1[x] + xData3[x]
#             # compute both the starting and ending (x, y)-coordinates for
#             # the text prediction bounding box
#             endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
#             endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
#             startX = int(endX - w)
#             startY = int(endY - h)
#             # add the bounding box coordinates and probability score to
#             # our respective lists
#             rects.append((startX, startY, endX, endY))
#             confidences.append(scoresData[x])
#                         
#     boxes = non_max_suppression(np.array(rects), probs=confidences)
#     # loop over the bounding boxes
#     for (startX, startY, endX, endY) in boxes:
#     	# scale the bounding box coordinates based on the respective
#     	# ratios
#     	startX = int(startX)
#     	startY = int(startY)
#     	endX = int(endX)
#     	endY = int(endY)
#     	# draw the bounding box on the image
#     	cv2.rectangle(imgresized32, (startX, startY), (endX, endY), (0, 255, 0), 2)
# =============================================================================
    

    return (img, gray, blur, thresh)


#Need to add additional code for vertical lines that don't extend over 1/2 the image size e.g. timetable2.jpg

#Display condensed lines on image
# =============================================================================
# for line in condensed_vertical_lines:
#     [[x1,y1],[x2,y2]] = line
#     cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
# for line in condensed_horizontal_lines:
#     [[x1,y1],[x2,y2]] = line
#     cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
# =============================================================================


#Assumes startdate and enddate have times of 00:00 and exist
# =============================================================================
# cal = Calendar()
# for row in row_to_time.keys():
#     for col in col_to_day.keys():
#         if (boxes[row][col][0] == ""):
#             continue
#         eventstartdate = startdate + timedelta(days=((days.index(col_to_day[col][0]) - startdate.weekday() + 7)%7))
#         eventenddate = eventstartdate
#         eventstartdate += timedelta(hours=int(row_to_time[row][0][0].split(':')[0]), minutes=int(row_to_time[row][0][0].split(':')[1]))
#         eventenddate += timedelta(hours=int(row_to_time[row][0][1].split(':')[0]), minutes=int(row_to_time[row][0][1].split(':')[1]))
#         count = 0
#         event = Event()
#         #Need to search boxes[row][col][0] for "weeks" in some cases
#         #if "week" in boxes[row][col][0].lower() or "weeks" in boxes[row][col][0].lower():
#             
#         event.add('summary', boxes[row][col][0])
#         event.add('dtstart', eventstartdate)
#         event.add('dtend', eventenddate)
#         while eventenddate < enddate:
#             count += 1
#             eventstartdate += timedelta(days=7)
#             eventenddate += timedelta(days=7)
#         event.add('rrule', {'freq': 'weekly', 'count':count})
#         cal.add_component(event)
# 
# f = open('example.ics', 'wb')
# f.write(cal.to_ical())
# f.close()
# 
# =============================================================================

for imgname in images:
    img = cv2.imread(imgname)
    imgnew = timetableScanner(img)[0]
    imS = cv2.resize(imgnew, (int(800/img.shape[0]*img.shape[1]), 800))  
    cv2.imshow(imgname, imS)

cv2.waitKey(0)


