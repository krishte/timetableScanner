import cv2
import pytesseract
from pytesseract import Output
import numpy as np
import math
import re
from datetime import timedelta
from dateparser.search import search_dates
from icalendar import Calendar, Event
'''
Calendar formats:
 - Month e.g. July 2023
 - Year calendar (months vertical)
 - Year calendar (months horizontal)
 - Timetable (days vertically, times horizontally) 
'''

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# returns dictionary with keys beign dates in dd/mm/yyyy format and values being lists of pairs where each pair is (24-hour time, description of activitylll)

img = cv2.imread('timetable5.png')

def relsize_adjust(x):
    return math.ceil((min(img.shape[0], img.shape[1])/x))

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 50, 200, apertureSize=3)
react_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (relsize_adjust(300), relsize_adjust(300)))
dilation = cv2.dilate(edges, react_kernel, iterations = 1)


# c = 0
# for i in contours:
#     area = cv2.contourArea(i)
#     cv2.drawContours(img, contours, c, (0, 255, 0), 3)
#     c+=1



#Thresholding works worse than gray for now
#ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)


#aperture size may need to be adjusted depending on image: 3,5, or 7
#Understand how Canny works

######## Currently works with gray, canny edges, dilation
######## suggested approach is downsampling, blurring, canny edges, dilation, erosion


 
# Applying dilation on the threshold image to make grid lines thicker
#react_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (relsize_adjust(300), relsize_adjust(300)))
# closing = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, (5,5))
# edges = cv2.Canny(closing, 50, 200, apertureSize=3)
#dilation = cv2.dilate(edges, rect_kernel, iterations = 1)


# Finding contours
#contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

#Averaging pixels seems to help it detect more lines - blurring
# kernel = np.ones((5,5),np.float32)/25
# edges = cv2.filter2D(gray,-1,kernel)
# edges = cv2.Canny(edges,50,200,apertureSize = 3)
# kernel = np.ones((5,5),np.uint8)
# edges = cv2.dilate(edges,kernel,iterations = 1)
# kernel = np.ones((5,5),np.uint8)
# edges = cv2.erode(edges,kernel,iterations = 1)


# For month.png: minlineLength=300, maxLineGap=10, and kernel=(2,2)
# Need to understand paramters more carefully
#Increasing threshold leads to more lines???
#lines = cv2.HoughLinesP(opening, rho=1, theta=np.pi/1440, threshold=200, minLineLength=200, maxLineGap=15)
lines = cv2.HoughLinesP(dilation, rho=1, theta=np.pi/360, threshold=relsize_adjust(3), minLineLength=relsize_adjust(3), maxLineGap=relsize_adjust(100))
        
lines_list = []
 
for line in lines:
    x1,y1,x2,y2=line[0]
    #cv2.line(img,(x1,y1),(x2,y2),(0,255,0),1)
    lines_list.append([[x1,y1],[x2,y2]])

# Contours outline the entire object so not so useful right now    
# =============================================================================
# for cnt in contours:
#     x, y, w, h = cv2.boundingRect(cnt)
#     # Drawing a rectangle on copied image
#     rect = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
# =============================================================================

#separate lines into horizontal and vertical
horizontal_lines = [[[a,b], [c,d]] for [[a,b], [c,d]] in lines_list if abs(b-d)<=relsize_adjust(100)]
vertical_lines = [[[a,b], [c,d]] for [[a,b], [c,d]] in lines_list if abs(a-c)<=relsize_adjust(100)]

#sort by second parameter in each tuple and ensure val[0][0] < val[1][0]
horizontal_lines = sorted(horizontal_lines, key=lambda x: x[0][1])
for i in range(len(horizontal_lines)):
    if (horizontal_lines[i][0][0] > horizontal_lines[i][1][0]):
        horizontal_lines[i] = [[horizontal_lines[i][1][0], horizontal_lines[i][0][1]],
                               [horizontal_lines[i][0][0], horizontal_lines[i][1][1]]]
        
#sort by first parameter in each tuple and ensure val[0][1] < val[1][1]
vertical_lines.sort()
for i in range(len(vertical_lines)):
    if (vertical_lines[i][0][1] > vertical_lines[i][1][1]):
        vertical_lines[i] = [[vertical_lines[i][0][0], vertical_lines[i][1][1]],
                             [vertical_lines[i][1][0], vertical_lines[i][0][1]]]
        
#When two lines are close enough to be considered the same line
linedif_tolerance = relsize_adjust(100)

#Group lines that are close together into one line

assert(len(horizontal_lines) > 1)
condensed_horizontal_lines = horizontal_lines[0:1]
for i in range(1,len(horizontal_lines)):
    if (abs(horizontal_lines[i][0][1]-horizontal_lines[i-1][0][1]) >= linedif_tolerance and
        abs(horizontal_lines[i][1][1]-horizontal_lines[i-1][1][1]) >= linedif_tolerance):
        condensed_horizontal_lines.append(horizontal_lines[i])
    else:
        condensed_horizontal_lines[-1][0][0] = min(condensed_horizontal_lines[-1][0][0], horizontal_lines[i][0][0])
        condensed_horizontal_lines[-1][1][0] = max(condensed_horizontal_lines[-1][1][0], horizontal_lines[i][1][0])
        

#Need to check if the vertical lines have some overlap before combining them. Otherwise, treat them separately somehow
assert(len(vertical_lines) > 1)
condensed_vertical_lines = vertical_lines[0:1]
for i in range(1,len(vertical_lines)):
    if (abs(vertical_lines[i][0][0]-vertical_lines[i-1][0][0]) >= linedif_tolerance and
        abs(vertical_lines[i][1][0]-vertical_lines[i-1][1][0]) >= linedif_tolerance):
        condensed_vertical_lines.append(vertical_lines[i])
    else:
        condensed_vertical_lines[-1][0][1] = min(condensed_vertical_lines[-1][0][1], vertical_lines[i][0][1])
        condensed_vertical_lines[-1][1][1] = max(condensed_vertical_lines[-1][1][1], vertical_lines[i][1][1])
        

#Need to add additional code for vertical lines that don't extend over 1/2 the image size e.g. timetable2.jpg

#Display condensed lines on image
for line in condensed_vertical_lines:
    [[x1,y1],[x2,y2]] = line
    cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
for line in condensed_horizontal_lines:
    [[x1,y1],[x2,y2]] = line
    cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
    
#Represent each line with a single value to recreate grid
horizontal_pos = [int((a[0][1]+a[1][1])/2) for a in condensed_horizontal_lines]
vertical_pos = [int((a[0][0]+a[1][0])/2) for a in condensed_vertical_lines]

boxes = []
titletext = ""
# The text above the timetable
if (horizontal_pos[0] >= 10):
    titled = pytesseract.image_to_data(gray[0:horizontal_pos[0]], output_type=Output.DICT)
    titletext = " ".join([val for val in titled['text'] if val.strip() != ''])
    title_boxes = len(titled['text'])
    
    for k in range(title_boxes):
        if int(titled['conf'][k]) >= 0:
            (x, y, w, h) = (titled['left'][k], titled['top'][k], titled['width'][k], titled['height'][k])
            img = cv2.rectangle(img, (x,y), (x+w, y+h), (0,255, 0), 1)

for i in range(len(horizontal_pos)-1):
    boxes.append([])
    for j in range(len(vertical_pos)-1):
        print(i,j)
        #Use either thresh1 or gray (yet to be decided)
        d = pytesseract.image_to_data(gray[horizontal_pos[i]:horizontal_pos[i+1], vertical_pos[j]:vertical_pos[j+1]], output_type=Output.DICT)
        n_boxes = len(d['text'])
        #print(d['text'])
        
        #To draw tightest possible rectangles around text
        (minx, miny, maxx, maxy) = (10000,10000,0,0)
        for k in range(n_boxes):
            if int(d['conf'][k]) >= 0 and d['text'][k].strip() != "":
                (x, y, w, h) = (d['left'][k], d['top'][k], d['width'][k], d['height'][k])
                minx = min(x, minx)
                miny = min(y, miny)
                maxx = max(x+w, maxx)
                maxy = max(y+h, maxy)
                
                #Used to a draw box around each word
                #img = cv2.rectangle(img, (x+vertical_pos[j], y+horizontal_pos[i]), (x+vertical_pos[j]+ w, y+horizontal_pos[i] +h), (0, 255, 0), 1)
        #2d array of text and coordinates for each box in grid
        boxes[-1].append((" ".join([d['text'][k] for k in range(n_boxes) if d['text'][k].strip() != '' and d['conf'][k] >= 0]), (vertical_pos[j]+minx, horizontal_pos[i]+miny, vertical_pos[j]+maxx, horizontal_pos[i]+maxy)))
        
        
#Assume all days occur in a single row and all times occur in a single column and both are the first respectively
#Dates for timetable are in the titletext

#Dictionary of (column number, (day, coordinates))
col_to_day = {}
for row in boxes:
    counter = 0
    for text in row:
        if len(text[0]) >= 3 and text[0].lower() != "day":
            for day in days:
                if day.lower().startswith(text[0].lower()):
                    col_to_day[counter] = (day, text[1])
                    break
        counter += 1
    if (len(col_to_day) > 0):
        break

#Dictionary of (row number, (times, coordinates))
row_to_time = {}    
for j in range(len(boxes[0])):
    for i in range(len(boxes)):
        times = re.findall(r'\b\d+[:.]\d\d', boxes[i][j][0])
        if (times != []):
            if (len(times) > 2):
                raise Exception(str(len(times)) + " times discovered in row " + str(i) + " column " + str(j))
            times = [time.replace(".", ":") for time in times]
            row_to_time[i] = (times, boxes[i][j][1])
    if (len(row_to_time) > 0):
        break
    
#If only one time in each row, take next time to make it two, but last row only has one
#Need to deal with last row
time_rows = list(row_to_time.keys())
for i in range(len(row_to_time)-1):
    if len(row_to_time[time_rows[i]][0]) == 1:
        row_to_time[time_rows[i]][0].append(row_to_time[time_rows[i+1]][0][0])
    
        
#Extracting date from titletext
titledates = search_dates(titletext)
startdate = ""
enddate = ""
if (titledates != None and len(titledates) == 2):
    startdate = titledates[0][1]
    enddate = titledates[1][1]
    enddate += timedelta(days=1)
    
for day in col_to_day.values():
    (x1,y1,x2,y2)= day[1]
    img = cv2.rectangle(img, (x1,y1), (x2,y2), (255, 0, 0), 3)
    
for time in row_to_time.values():
    (x1,y1,x2,y2)= time[1]
    img = cv2.rectangle(img, (x1,y1), (x2,y2), (0, 0, 255), 3)
    
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
    

cv2.imwrite('img.png', dilation)
cv2.waitKey(0)


