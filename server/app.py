import cv2
import pytesseract
from pytesseract import Output
import numpy as np
import re
from datetime import timedelta, datetime
from icalendar import Calendar, Event
import Levenshtein
from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS
import io

app = Flask(__name__)
CORS(app)

'''
Calendar formats:
 - Month e.g. July 2023
 - Year calendar (months vertical)
 - Year calendar (months horizontal)
 - Timetable (days vertically, times horizontally)
'''
# Maximum separation of lines to be considered the same line
CONST_LINE_SEPARATION = 20
# Size of kernel used to remove text
CONST_KERNEL_SIZE = 10
# Min slope for a line to be considered vertical
CONST_MIN_SLOPE = 40
# Max slope for a line to be considered horizontal
CONST_MAX_SLOPE = 1/CONST_MIN_SLOPE
# threshold for lines to be considered overlapping i.e. they can not overlap by at most this amount and still be considered overlapping
CONST_OVERLAP_THRESHOLD = 25
# Maximum difference between y-coords of text to be considered on the same line
CONST_VERTICAL_TEXT_DIF = 10
# The second times that will be produced if only one times is detected in a box with no previous time
CONST_PRESET_TIME_DIF = 60
# (a1+10, a1-10) must be contained in (b1, b2) for strict_contains to evaluate to true when detecting boxes
CONST_STRICT_CONTAIN = 10
# The max a box will be cropped by before applying thresholding
CONST_MAX_CROP = 10
# Minimum allowed box width. Image is resized according to this
CONST_MIN_BOX_WIDTH = 100
# List of days
CONST_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday",
              "Friday", "Saturday", "Sunday", "Weekends", "Weekdays"]
# List of supported img types
CONST_SUP_IMG_TYPES = ["png", "jpg", "jpeg", "jpe", "jp2"]

#images = ["timetable.png", "timetable2.jpg", "timetable3.png", "timetable4.jpg", "timetable5.png", "timetable6.jpg", "timetable7.jpg", "timetable8.jpg", "timetable9.png", "timetable10.png", "timetable11.jpg"]


def get_lines_from_gray_img(gray):
    react_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    kernel_horizontal = np.ones((1, CONST_KERNEL_SIZE), np.uint8)
    kernel_vertical = np.ones((CONST_KERNEL_SIZE, 1), np.uint8)

    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 3, 2)

    edges = cv2.Canny(thresh, 50, 200, apertureSize=3)
    edges2 = cv2.Canny(gray, 50, 200, apertureSize=3)

    opening_horizontal = cv2.erode(edges, kernel_horizontal, iterations=1)
    dilation_horizontal = cv2.dilate(
        opening_horizontal, react_kernel, iterations=1)

    # Second method catches some lines that are missed due to blurring
    opening_horizontal2 = cv2.erode(edges2, kernel_horizontal, iterations=1)
    dilation_horizontal2 = cv2.dilate(
        opening_horizontal2, react_kernel, iterations=1)

    opening_vertical = cv2.erode(edges, kernel_vertical, iterations=1)
    dilation_vertical = cv2.dilate(
        opening_vertical, react_kernel, iterations=1)

    opening_vertical2 = cv2.erode(edges2, kernel_vertical, iterations=1)
    dilation_vertical2 = cv2.dilate(
        opening_vertical2, react_kernel, iterations=1)

    # This is the raw output of HoughLines which may contains all types of lines in either list
    hor_lines1 = cv2.HoughLinesP(
        dilation_horizontal, rho=1, theta=np.pi/1440, threshold=50, minLineLength=50, maxLineGap=15)
    hor_lines2 = cv2.HoughLinesP(
        dilation_horizontal2, rho=1, theta=np.pi/1440, threshold=50, minLineLength=50, maxLineGap=15)

    ver_lines1 = cv2.HoughLinesP(
        dilation_vertical, rho=1, theta=np.pi/1440, threshold=50, minLineLength=50, maxLineGap=15)
    ver_lines2 = cv2.HoughLinesP(
        dilation_vertical2, rho=1, theta=np.pi/1440, threshold=50, minLineLength=50, maxLineGap=15)

    return (hor_lines1, hor_lines2, ver_lines1, ver_lines2)


def group_lines(raw_horizontal_lines, raw_vertical_lines, horizontal_lines, vertical_lines):
    """Group horizontal and vertical lines by y and x coordinate respectively."""
    for line in raw_horizontal_lines:
        x1, y1, x2, y2 = line[0]
        if (x2 != x1 and abs((y2-y1)/(x2-x1)) <= CONST_MAX_SLOPE):
            # cv2.line(img,(x1,y1),(x2,y2),(0,255,0),1)
            horizontal_lines.append(
                [[min(x1, x2), min(y1, y2)], [max(x1, x2), max(y1, y2)]])

    for line in raw_vertical_lines:
        x1, y1, x2, y2 = line[0]
        if (x2 == x1 or abs((y2-y1)/(x2-x1)) >= CONST_MIN_SLOPE):
            # cv2.line(img,(x1,y1),(x2,y2),(0,255,0),1)
            vertical_lines.append(
                [[min(x1, x2), min(y1, y2)], [max(x1, x2), max(y1, y2)]])

    # finds the list in lines_list that contains the lines with x or y coordinate coord or returns -1 if no such list exists

    def line_search(lines_list, coord):
        for i in range(len(lines_list)):
            if abs(lines_list[i][0]-coord) <= CONST_LINE_SEPARATION:
                return i
        return -1

    # determines if the two intervals (a1,a2) and (b1,b2) overlap with some leeway
    def overlap(a1, a2, b1, b2):
        return ((a1 >= b1-CONST_OVERLAP_THRESHOLD and a1 <= b2+CONST_OVERLAP_THRESHOLD) or
                (a2 >= b1-CONST_OVERLAP_THRESHOLD and a2 <= b2+CONST_OVERLAP_THRESHOLD))

    horizontal_lines.sort()
    vertical_lines = sorted(vertical_lines, key=lambda x: x[0][1])

    # Could keep track of (y1,y2) at start of each list but only works if lines are really flat?
    # A list of lists where each nested list contains a y coordinate followed by all lines at that y coordinate (for grouped_horizontal_lines)
    grouped_horizontal_lines, grouped_vertical_lines = [], []
    for line in horizontal_lines:
        [[x1, y1], [x2, y2]] = line
        ind = line_search(grouped_horizontal_lines, y1)
        if (ind == -1):
            grouped_horizontal_lines.append([y1, line])
        else:
            minx = x1
            maxx = x2
            newlines = []
            for overlap_line in grouped_horizontal_lines[ind][1:]:
                if (overlap(x1, x2, overlap_line[0][0], overlap_line[1][0])):
                    minx = min(minx, overlap_line[0][0])
                    maxx = max(maxx, overlap_line[1][0])
                else:
                    newlines.append(overlap_line)
            newlines.append([[minx, y1], [maxx, y2]])
            grouped_horizontal_lines[ind][1:] = newlines

    for line in vertical_lines:
        [[x1, y1], [x2, y2]] = line
        ind = line_search(grouped_vertical_lines, x1)
        if (ind == -1):
            grouped_vertical_lines.append([x1, line])
        else:
            miny = y1
            maxy = y2
            newlines = []
            for overlap_line in grouped_vertical_lines[ind][1:]:
                if (overlap(y1, y2, overlap_line[0][1], overlap_line[1][1])):
                    miny = min(miny, overlap_line[0][1])
                    maxy = max(maxy, overlap_line[1][1])
                else:
                    newlines.append(overlap_line)
            newlines.append([[x1, miny], [x2, maxy]])
            grouped_vertical_lines[ind][1:] = newlines

    grouped_horizontal_lines.sort()
    grouped_vertical_lines.sort()

    return (grouped_horizontal_lines, grouped_vertical_lines)


def find_days(gray, grouped_horizontal_lines, grouped_vertical_lines):
    daysrow = -1
    day_to_coord = {}
    for i in range(len(grouped_horizontal_lines)-1):
        start_hori_line = grouped_horizontal_lines[i][0]
        end_hori_line = grouped_horizontal_lines[i+1][0]
        intersecting_vertical_lines = [grouped_vertical_lines[0][0]]
        for group in grouped_vertical_lines[1:]:
            for line in group[1:]:
                if (start_hori_line >= line[0][1]-CONST_OVERLAP_THRESHOLD and
                        end_hori_line <= line[1][1]+CONST_OVERLAP_THRESHOLD):
                    intersecting_vertical_lines.append(group[0])
                    break
        for j in range(len(intersecting_vertical_lines)-1):
            thresh2 = cv2.threshold(gray[grouped_horizontal_lines[i][0]:grouped_horizontal_lines[i+1][0],
                                         intersecting_vertical_lines[j]:intersecting_vertical_lines[j+1]], 0, 255,
                                    cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1]
            blur2 = cv2.GaussianBlur(thresh2, (3, 3), 0)
            # psm 7, 11,12 work as well but detect the line in between days as a | character
            d = pytesseract.image_to_data(
                blur2, output_type=Output.DICT,  config='--psm 7')
    #        cv2.imshow(str(i), blur1[grouped_horizontal_lines[i][0]:grouped_horizontal_lines[i+1][0], grouped_vertical_lines[0][0]:grouped_vertical_lines[-1][0]])
            n_boxes = len(d['text'])
            print(d['text'])
            #print("days", d['text'])
            #print("days", d['conf'])
            for k in range(n_boxes):
                if int(d['conf'][k]) >= 0 and d['text'][k].strip() != "":
                    (x, y, w, h) = (d['left'][k], d['top']
                                    [k], d['width'][k], d['height'][k])
                    text = "".join(
                        [e for e in d['text'][k].strip() if e.isalnum()])
                    if len(text) >= 3 and text.lower() != "day":
                        for day in CONST_DAYS:
                            if day.lower().startswith(text.lower()) or Levenshtein.distance(text.lower(), day.lower()) <= 1:
                                print("dayfound", day)
                                day_to_coord[day] = (x+intersecting_vertical_lines[j], y+grouped_horizontal_lines[i]
                                                     [0], x+w+intersecting_vertical_lines[j], y+h+grouped_horizontal_lines[i][0])
                                #img = cv2.rectangle(img, (day_to_coord[day][0], day_to_coord[day][1]), (day_to_coord[day][2], day_to_coord[day][3]), (255, 0, 0), 2)
                                daysrow = i
                                break
        if (daysrow != -1):
            break

    return (daysrow, day_to_coord)


def find_times(gray, grouped_horizontal_lines, grouped_vertical_lines, daysrow):
    timescol = -1
    times_col_boxes = []
    for i in range(0, len(grouped_vertical_lines)-1):
        times_col_boxes = []
        start_vert_line = grouped_vertical_lines[i][0]
        end_vert_line = grouped_vertical_lines[i+1][0]
        intersecting_horizontal_lines = [
            grouped_horizontal_lines[daysrow+1][0]]
        for group in grouped_horizontal_lines[daysrow+2:]:
            if (group[0] > CONST_LINE_SEPARATION + grouped_vertical_lines[i][-1][1][1]):
                break
            for line in group[1:]:
                if (start_vert_line >= line[0][0]-CONST_OVERLAP_THRESHOLD
                        and end_vert_line <= line[1][0]+CONST_OVERLAP_THRESHOLD):
                    intersecting_horizontal_lines.append(group[0])
                    break
        print(intersecting_horizontal_lines)
        for line in grouped_vertical_lines[i+1][1:]:
            if (line[0][1] >= grouped_horizontal_lines[daysrow+1][0]):
                intersecting_horizontal_lines.append(line[0][1])
            if (line[1][1] >= grouped_horizontal_lines[daysrow+1][0]):
                intersecting_horizontal_lines.append(line[1][1])
        intersecting_horizontal_lines.sort()
        new_intersecting_horizontal_lines = intersecting_horizontal_lines[0:1]
        for val in intersecting_horizontal_lines[1:]:
            if (abs(val-new_intersecting_horizontal_lines[-1]) > CONST_LINE_SEPARATION):
                new_intersecting_horizontal_lines.append(val)
        intersecting_horizontal_lines = new_intersecting_horizontal_lines
        print(grouped_horizontal_lines[daysrow+1][0], intersecting_horizontal_lines)
        for j in range(len(intersecting_horizontal_lines)-1):
            horizontal_midpoint = (intersecting_horizontal_lines[j]+intersecting_horizontal_lines[j+1])/2
            vert_line_index = -1
            for k in range(i+1, len(grouped_vertical_lines)):
                for line in grouped_vertical_lines[k][1:]:
                    if (horizontal_midpoint >= line[0][1] and horizontal_midpoint <= line[1][1]):
                        vert_line_index = k
                        break
                if (vert_line_index != -1):
                    break
            print(j, vert_line_index)
            if (vert_line_index==-1):
                vert_line_index = i+1          

            thresh2 = cv2.threshold(gray[intersecting_horizontal_lines[j]:intersecting_horizontal_lines[j+1], grouped_vertical_lines[i]
                                    [0]:grouped_vertical_lines[vert_line_index][0]], 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1]
            blur2 = cv2.GaussianBlur(thresh2, (3, 3), 0)

            #cv2.imshow(str(j), gray[intersecting_horizontal_lines[j]:intersecting_horizontal_lines[j+1], grouped_vertical_lines[i][0]:(grouped_vertical_lines[i+1][0] if vert_line_found else grouped_vertical_lines[-1][0])])
            d = pytesseract.image_to_data(
                blur2, output_type=Output.DICT, config='--psm 6')
            n_boxes = len(d['text'])
            for k in range(n_boxes):
                if (int(d['conf'][k]) >= 0 and d['text'][k].strip() != ""):
                    (_, y, _, h) = (d['left'][k], d['top']
                                    [k], d['width'][k], d['height'][k])
                    text = d['text'][k].strip()
                    times_col_boxes.append(
                        [text, [y+intersecting_horizontal_lines[j], y+h+intersecting_horizontal_lines[j]]])
                    if (re.findall(r'\d{2,}', text) != []):
                        timescol = i
                    #img = cv2.rectangle(img, (x+grouped_vertical_lines[i][0],y+intersecting_horizontal_lines[j]), (x+w+grouped_vertical_lines[i][0],y+h+intersecting_horizontal_lines[j]), (0, 0, 255), 2)
        if timescol != -1:
            break
    print(times_col_boxes)
    return (timescol, times_col_boxes)


def process_times(times_col_boxes, grouped_horizontal_lines, grouped_vertical_lines, timescol, find_closest_line, not_gibberish):
    # group time boxes with same horizontal coordinate
    times_col_grouped_boxes = [times_col_boxes[0]]
    for (text, (y1, y2)) in times_col_boxes[1:]:
        if (abs(y2-times_col_grouped_boxes[-1][1][1]) <= CONST_VERTICAL_TEXT_DIF):
            times_col_grouped_boxes[-1][0] += " " + text
            times_col_grouped_boxes[-1][1][0] = min(
                y1, times_col_grouped_boxes[-1][1][0])
            times_col_grouped_boxes[-1][1][1] = max(
                y2, times_col_grouped_boxes[-1][1][1])
        else:
            times_col_grouped_boxes.append([text, [y1, y2]])

    # Filter out gibberish after grouping by x-coord
    times_col_grouped_boxes = [
        x for x in times_col_grouped_boxes if not_gibberish(x[0])]

    # print(times_col_grouped_boxes)
    # Find the average size of a text box
    assert(len(times_col_grouped_boxes) != 0)
    vert_sep_threshold = 0.0  # y_diffs[0]
    for val in times_col_grouped_boxes:
        vert_sep_threshold += val[1][1] - val[1][0] + 5
    vert_sep_threshold /= len(times_col_grouped_boxes)

    def is_contained_in_horizontal_line(point, index):
        for [[x1, y1], [x2, y2]] in grouped_horizontal_lines[index][1:]:
            if point >= x1 and point <= x2:
                return True
        return False

    # Group text boxes whose y values differ by at most the size of the average text box i.e. they have less than a line spacing between them
    times = [times_col_grouped_boxes[0]]
    for (text, (y1, y2)) in times_col_grouped_boxes[1:]:
        closest_line_index = find_closest_line(
            (y1+times[-1][1][1])/2, grouped_horizontal_lines)
        closest_line = grouped_horizontal_lines[closest_line_index][0]
        if (abs(y1-times[-1][1][1]) <= vert_sep_threshold and
            (not (closest_line >= times[-1][1][1]-10 and closest_line <= y1+10 and
                  is_contained_in_horizontal_line((grouped_vertical_lines[timescol][0] +
                                                   grouped_vertical_lines[timescol+1][0])/2, closest_line_index)))):
            times[-1][0] += " " + text
            times[-1][1][1] = y2
        else:
            times.append([text, [y1, y2]])
    print(times)
    return times


def parse_times(times):

    # Process all the values in times into standard format
    for i in range(len(times)):
        num_times = re.findall(
            r'\b\d+[:.,;]?\d+\s?\w*\s?[-]\s?\d+[:.,;]?\d+', times[i][0])
        num_single_time = re.findall(r'\b\d+[:.,;]?\d+', times[i][0])
        print(i, num_times, num_single_time)
        if len(num_times) == 1 or len(num_single_time) == 2:
            two_times = []
            if (len(num_times) == 1):
                two_times = num_times[0].split('-')
            else:
                two_times.append(num_single_time[0])
                two_times.append(num_single_time[1])
            for j in range(2):
                num_time = ""
                for c in two_times[j]:
                    if (not c.isalpha() and c != ' '):
                        num_time += c
                hours, minutes = "", ""
                if (len([c for c in num_time if not c.isdigit()]) == 0):
                    hours = num_time
                    minutes = "00"
                else:
                    [hours, minutes] = num_time.split(
                        [c for c in num_time if not c.isdigit()][0])

                two_times[j] = hours + ":" + minutes
            times[i][0] = (two_times[0], two_times[1])
        elif len(num_times) == 0 and len(num_single_time) == 1:
            one_time = num_single_time[0]

            num_time = ""
            for c in one_time:
                if (not c.isalpha() and c != ' '):
                    num_time += c
            hours, minutes = "", ""
            if (len([c for c in num_time if not c.isdigit()]) == 0):
                hours = num_time
                minutes = "00"
            else:
                [hours, minutes] = num_time.split(
                    [c for c in num_time if not c.isdigit()][0])

            one_time = hours + ":" + minutes
            times[i][0] = (one_time, "Empty")
        else:
            times[i][0] = ("Empty", "Empty")
            # This case should never be reached in the end
            #raise Exception("No time in box " + str(i))
        
        
    # Deal with the one time cases

    def time_dif_mins(timepair):
        [h1, m1] = [int(x) for x in timepair[0].split(':')]
        [h2, m2] = [int(x) for x in timepair[1].split(':')]
        return (h2-h1)*60+m2-m1

    last_time_dif = CONST_PRESET_TIME_DIF
    for i in range(len(times)-1):
        if (times[i][0][1] == "Empty" and times[i+1][0][0] != "Empty" and times[i][0][0] != "Empty"):
            times[i][0] = (times[i][0][0], times[i+1][0][0])
            last_time_dif = time_dif_mins(times[i][0])

    def addMins(mins, time):
        [h1, m1] = [int(x) for x in time.split(':')]
        m1 += mins
        h1 += m1//60
        m1 %= 60
        m1 = str(m1)
        if (len(m1) == 1):
            return str(h1)+":0" + m1
        else:
            return str(h1)+":"+m1

    if times[-1][0][1] == "Empty" and times[-1][0][0] != "Empty":
        times[-1][0] = (times[-1][0][0],
                        addMins(last_time_dif, times[-1][0][0]))
        
    print(times)
    #returns whether time1 is smaller than time2
    def is_time_smaller(time1, time2):
        [h1,m1] = time1.split(':')
        [h2,m2] = time2.split(':')
        if (h1==h2):
            return int(m1) < int(m2)
        return int(h1) < int(h2)
        
    #flag times that start before the previous time ends or where the second time occurs before the first
    error_times = []
    for i in range(len(times)):
        if (times[i][0][0] == "Empty" or times[i][0][1] == "Empty"):
            error_times.append(True)
        elif (i > 0 and is_time_smaller(times[i][0][0], times[i-1][0][1])) or is_time_smaller(times[i][0][1], times[i][0][0]):
            error_times.append(True)
        else:
            error_times.append(False)
        
    return times, error_times


def find_day_cols(day_to_coord, grouped_vertical_lines, timescol, find_closest_line):
    day_to_col = {}
    found_days = list(day_to_coord.keys())
    day_coords = list(day_to_coord.values())
    lastcol = timescol + 1
    for i in range(len(day_coords)-1):
        newcol = find_closest_line(
            (day_coords[i][0]+day_coords[i][2]+day_coords[i+1][0]+day_coords[i+1][2])/4, grouped_vertical_lines)
        day_to_col[found_days[i]] = (lastcol, newcol)
        lastcol = newcol
    day_to_col[found_days[-1]] = (lastcol, len(grouped_vertical_lines)-1)
    return day_to_col


def find_time_rows(times, grouped_horizontal_lines, daysrow, find_closest_line):
    time_to_row = {}
    lastrow = daysrow+1
    for i in range(len(times)-1):
        newrow = find_closest_line(
            (times[i][1][0]+times[i][1][1]+times[i+1][1][0]+times[i+1][1][1])/4, grouped_horizontal_lines)
        time_to_row[times[i][0]] = (lastrow, newrow)
        lastrow = newrow
    last_hor_line = find_closest_line(
        times[-1][1][1]+10, grouped_horizontal_lines)
    if (last_hor_line == lastrow):
        time_to_row[times[-1][0]] = (lastrow, lastrow+1)
    elif (grouped_horizontal_lines[last_hor_line][0] <= times[-1][1][1]):
        time_to_row[times[-1][0]] = (lastrow, last_hor_line+1)
    else:
        time_to_row[times[-1][0]] = (lastrow, last_hor_line)

    return time_to_row


def find_boxes(grouped_horizontal_lines, grouped_vertical_lines, daysrow, timescol):
    # whether (a1, a2) is contained in (b1, b2) with some leeway
    def contains(a1, a2, b1, b2):
        return (a1 >= b1-CONST_OVERLAP_THRESHOLD and a2 <= b2+CONST_OVERLAP_THRESHOLD)

    def strict_contains(a1, a2, b1, b2):
        return (a1 >= b1 and a2 <= b2)
    boxes = []
    for i in range(daysrow+1, len(grouped_horizontal_lines)):
        for j in range(i+1, len(grouped_horizontal_lines)):
            for k in range(timescol+1, len(grouped_vertical_lines)):
                for l in range(k+1, len(grouped_vertical_lines)):
                    contained = False
                    for [[x1, y1], [x2, y2]] in grouped_horizontal_lines[i][1:]:
                        if contains(grouped_vertical_lines[k][0], grouped_vertical_lines[l][0], x1, x2):
                            contained = True
                    if not contained:
                        continue
                    contained = False
                    for [[x1, y1], [x2, y2]] in grouped_horizontal_lines[j][1:]:
                        if contains(grouped_vertical_lines[k][0], grouped_vertical_lines[l][0], x1, x2):
                            contained = True
                    if not contained:
                        continue
                    contained = False
                    for [[x1, y1], [x2, y2]] in grouped_vertical_lines[k][1:]:
                        if contains(grouped_horizontal_lines[i][0], grouped_horizontal_lines[j][0], y1, y2):
                            contained = True
                    if not contained:
                        continue
                    contained = False
                    for [[x1, y1], [x2, y2]] in grouped_vertical_lines[l][1:]:
                        if contains(grouped_horizontal_lines[i][0], grouped_horizontal_lines[j][0], y1, y2):
                            contained = True
                    if not contained:
                        continue
                    for a in range(i+1, j):
                        for [[x1, y1], [x2, y2]] in grouped_horizontal_lines[a][1:]:
                            if strict_contains(grouped_vertical_lines[k][0]+CONST_STRICT_CONTAIN, grouped_vertical_lines[k][0]+CONST_STRICT_CONTAIN, x1, x2) or strict_contains(grouped_vertical_lines[l][0]-CONST_STRICT_CONTAIN, grouped_vertical_lines[l][0]-CONST_STRICT_CONTAIN, x1, x2):
                                contained = False
                    if not contained:
                        continue
                    for a in range(k+1, l):
                        for [[x1, y1], [x2, y2]] in grouped_vertical_lines[a][1:]:
                            if strict_contains(grouped_horizontal_lines[i][0]+CONST_STRICT_CONTAIN, grouped_horizontal_lines[i][0]+CONST_STRICT_CONTAIN, y1, y2) or strict_contains(grouped_horizontal_lines[j][0]-CONST_STRICT_CONTAIN, grouped_horizontal_lines[j][0]-CONST_STRICT_CONTAIN, y1, y2):
                                contained = False
                    if not contained:
                        continue
                    #img = cv2.rectangle(img, (grouped_vertical_lines[k][0],grouped_horizontal_lines[i][0]), (grouped_vertical_lines[l][0],grouped_horizontal_lines[j][0]), (0,255,0), 5)
                    #img = cv2.circle(img, (int((grouped_vertical_lines[k][0]+ grouped_vertical_lines[l][0])/2),int((grouped_horizontal_lines[i][0]+grouped_horizontal_lines[j][0])/2)), radius=5, color=(0, 0, 255), thickness=-1)
                    boxes.append((k, i, l, j))
    return boxes


def get_events(boxes, day_to_col, grouped_horizontal_lines, grouped_vertical_lines, gray, not_gibberish):
    events = []

    counter = 0
    web_boxes = []
    for (k, i, l, j) in boxes:

        daylist = []
        timelist = (i, j)

        for day, (start, end) in day_to_col.items():
            if min(l, end)-max(k, start) >= 1:
                if (day == "Weekends"):
                    daylist.extend(["Saturday", "Sunday"])
                elif day == "Weekdays":
                    daylist.extend(
                        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
                else:
                    daylist.append(day)

        x1, y1, x2, y2 = grouped_vertical_lines[k][0], grouped_horizontal_lines[
            i][0], grouped_vertical_lines[l][0], grouped_horizontal_lines[j][0]
        y_crop = min(int((y2-y1)*0.1), CONST_MAX_CROP)
        x_crop = min(int((x2-x1)*0.1), CONST_MAX_CROP)
        thresh2 = cv2.threshold(gray[(y1+y_crop):(y2-y_crop), (x1+x_crop):(
            x2-x_crop)], 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1]
        #blur2 = cv2.GaussianBlur(thresh2, (3, 3), 0)
        d = pytesseract.image_to_data(
            thresh2, output_type=Output.DICT, config='--psm 6')
        n_boxes = len(d['text'])
        text = " ".join([d['text'][k] for k in range(n_boxes)
                        if d['text'][k].strip() != '' and d['conf'][k] >= 0])
        weektext = []
        week_nos = []
        if ("week" in text.lower()):
            weektext = re.findall(
                r'\b\d+(?:\s*-\s*\d+)?\s*(?:(?:,|\w+|,\s*\w+)\s*\d+(?:\s*-\s*\d+)?\s*)*', text[text.lower().index("week"):])

        if (len(weektext) != 0):

            weeklist = weektext[0].split(",")
            for simple_val in weeklist:
                processed_val = []
                temp = ""
                for word in simple_val.split():
                    if (not any(c.isdigit() or c == '-' for c in word)):
                        processed_val.append(temp)
                        temp = ""
                    else:
                        temp += word
                processed_val.append(temp)
                for val in processed_val:
                    if (val == ""):
                        continue
                    if "-" in val:
                        [val1, val2] = val.split("-")
                        val1, val2 = int(val1.strip()), int(val2.strip())
                        for i in range(val1, val2+1):
                            week_nos.append(i)
                    else:
                        week_nos.append(int(val.strip()))
            week_nos = list(set(week_nos))
            week_nos.sort()
        if (timelist != [] and daylist != [] and not_gibberish(text)):
            counter += 1
            web_boxes.append([int(x1), int(y1), int(x2), int(y2)])
            #cv2.imwrite("input_cropped/" + str(counter) + ".png", img[y1:y2, x1:x2])
            events.append(
                (text, daylist, timelist, week_nos))
    return (events, web_boxes)


@app.route('/processTimetable', methods=['POST'])
def process_timetable():

    file = request.files['timetableFile']
    if (file.filename.split('.')[-1] not in CONST_SUP_IMG_TYPES):
        return jsonify(success=False, error="The uploaded file is not a supported image type.")

    file_bytes = np.fromfile(file, np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    hor_lines1, hor_lines2, ver_lines1, ver_lines2 = get_lines_from_gray_img(
        gray)

    if ((hor_lines1 is None or hor_lines2 is None) or (ver_lines1 is None or ver_lines2 is None)):
        return jsonify(success=False, error="This image does not appear to be a timetable")

    raw_horizontal_lines = np.concatenate((hor_lines1, hor_lines2))
    raw_vertical_lines = np.concatenate((ver_lines1, ver_lines2))

    horizontal_lines, vertical_lines = [[[0, 0], [img.shape[1], 0]], [[0, img.shape[0]], [img.shape[1], img.shape[0]]]], [
        [[0, 0], [0, img.shape[0]]],  [[img.shape[1], 0], [img.shape[1], img.shape[0]]]]

    grouped_horizontal_lines, grouped_vertical_lines = group_lines(
        raw_horizontal_lines, raw_vertical_lines, horizontal_lines, vertical_lines)

    for y_lines in (grouped_horizontal_lines+grouped_vertical_lines):
        for line in y_lines[1:]:
            [[x1, y1], [x2, y2]] = line
            cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)

    daysrow, day_to_coord = find_days(
        gray, grouped_horizontal_lines, grouped_vertical_lines)

    # No days found
    if (daysrow == -1):
        return jsonify(success=False, error="Could not find any days in the image")

    timescol, times_col_boxes = find_times(
        gray, grouped_horizontal_lines, grouped_vertical_lines, daysrow)

    if (timescol == -1):
        return jsonify(success=False, error="Could not find any times in the image")

    def not_gibberish(text):
        return len(text) >= 3

    # Find the dividing lines for days and times
    def find_closest_line(coord, lines_list):
        index = 0
        minval = abs(lines_list[0][0]-coord)
        for i, lines in enumerate(lines_list):
            if (abs(lines[0]-coord) < minval):
                minval = abs(lines[0]-coord)
                index = i
        return index

    times = process_times(times_col_boxes, grouped_horizontal_lines,
                          grouped_vertical_lines, timescol, find_closest_line, not_gibberish)
    times, error_times = parse_times(times)
    print(error_times)

    day_to_col = find_day_cols(
        day_to_coord, grouped_vertical_lines, timescol, find_closest_line)
    time_to_row = find_time_rows(
        times, grouped_horizontal_lines, daysrow, find_closest_line)

    print(time_to_row)

    print(day_to_col)

    boxes = find_boxes(grouped_horizontal_lines,
                       grouped_vertical_lines, daysrow, timescol)

    events, web_boxes = get_events(
        boxes, day_to_col, grouped_horizontal_lines, grouped_vertical_lines, gray, not_gibberish)
    
    print(boxes)
    print(grouped_horizontal_lines)
    print(grouped_vertical_lines)

    for day in CONST_DAYS:
        for event in events:
            if event[1][0] == day:
                print(event)

    min_box_width = min([x2-x1 for [x1, y1, x2, y2] in web_boxes])
    cropped_width = int(
        max(1920, img.shape[1]*CONST_MIN_BOX_WIDTH/min_box_width))

    scalefactor = cropped_width/img.shape[1]
    web_boxes = [[int(scalefactor*a), int(scalefactor*b), int(scalefactor*c),
                  int(scalefactor*d)] for [a, b, c, d] in web_boxes]
    time_boxes = []
    for (time1, time2), (i, j) in time_to_row.items():
        time_boxes.append([time1+"-"+time2, int(scalefactor*grouped_vertical_lines[timescol]
                          [0]), i, int(scalefactor*grouped_vertical_lines[timescol+1][0]), j])
    horizontal_lines = [int(scalefactor*x[0])
                        for x in grouped_horizontal_lines]
    response = jsonify(success=True, horizontalLines=horizontal_lines, timeBoxes=time_boxes,
                       croppedWidth=cropped_width, cropped_pos=web_boxes, events=events, errorTimes=error_times)

    #cv2.imwrite("test.png", img)
    return response

@app.route('/resizeImage', methods=['POST'])
def resize_image():
    file = request.files['timetableFile']
    cropped_width = int(request.form['croppedWidth'])
    print(cropped_width)
    file_bytes = np.fromfile(file, np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    imS = cv2.resize(img, (cropped_width, int(
        cropped_width/img.shape[1]*img.shape[0])))
    _, image_encoded = cv2.imencode('.jpg', imS)
    image_bytes = image_encoded.tobytes()

    # Create a Flask response with the image bytes
    response = Response(image_bytes, content_type='image/jpeg')
    return response

@app.route('/recalculateTimes', methods=['POST'])
def recalculate_times():
    
    results = request.get_json()
    events, time_rows = results[0], results[1]
    time_rows = [(x[0], (x[2], x[4])) for x in time_rows]

    def compute_half(timepair):
        [h1, m1] = [int(x) for x in timepair[0].split(':')]
        [h2, m2] = [int(x) for x in timepair[1].split(':')]
        half = int(((h2-h1)*60+m2-m1)/2)
        h_str = str(int((m1+half)/60 + h1) % 24)
        m_str = str((m1+half) % 60)
        if (len(m_str) == 1):
            m_str = "0" + m_str
        return h_str + ":" + m_str

    new_events = []
    for event in events:
        timelist = []
        i = event[2][0]
        j = event[2][1]
        for (timeJoined, (start, end)) in time_rows:
            time = timeJoined.split('-')
            if (i <= start and end <= j):
                timelist.append(time)
            elif (i > start and i < end):
                timelist.append((compute_half(time), time[1]))
            elif (j > start and j < end):
                timelist.append((time[0], compute_half(time)))
        if (timelist != []):
            new_events.append(event)
            new_events[-1][2] = (timelist[0][0], timelist[-1][1])

    for day in CONST_DAYS:
        for event in new_events:
            if event[1][0] == day:
                print(event)

    return jsonify(success=True,
                   summaries=[event[0] for event in new_events],
                   days=[event[1] for event in new_events],
                   times=[event[2][0]+"-"+event[2][1] for event in new_events],
                   weeks=[event[3] for event in new_events])


@app.route('/createCalendarFile', methods=['POST'])
def create_calendar_file():
    # Assumes startdate and enddate have times of 00:00 and exist
    events = request.get_json()
    startdate, enddate = [int(x) for x in events[4].split(
        '-')], [int(x) for x in events[5].split('-')]
    startdate, enddate = datetime(startdate[0], startdate[1], startdate[2]), datetime(
        enddate[0], enddate[1], enddate[2])
    enddate += timedelta(days=1)
    events = [(events[0][i], events[1][i], events[2][i].split(
        '-'), events[3][i]) for i in range(len(events[0]))]
    print(startdate, enddate)
    cal = Calendar()

    def time_dif_mins(timepair):
        [h1, m1] = [int(x) for x in timepair[0].split(':')]
        [h2, m2] = [int(x) for x in timepair[1].split(':')]
        return (h2-h1)*60+m2-m1

    for found_event in events:

        eventstartdate = startdate + \
            timedelta(
                days=((CONST_DAYS.index(found_event[1][0]) - startdate.weekday() + 7) % 7))
        eventenddate = eventstartdate
        if (found_event[2][0] == "Empty" or found_event[2][0] == "Empty"):
            raise Exception("An event ends at an empty time: " + found_event)
        eventstartdate += timedelta(
            minutes=time_dif_mins(("0:00", found_event[2][0])))
        eventenddate += timedelta(minutes=time_dif_mins(("0:00",
                                  found_event[2][1])))
        week_nos = found_event[3]
        if (week_nos != []):
            for week_no in week_nos:
                event = Event()
                event.add('summary', found_event[0])
                newstartdate = eventstartdate
                newenddate = eventenddate
                for i in range(week_no-1):
                    newstartdate += timedelta(days=7)
                    newenddate += timedelta(days=7)
                if newenddate > enddate:
                    continue
                event.add('dtstart', newstartdate)
                event.add('dtend', newenddate)
                cal.add_component(event)
        else:
            event = Event()
            # Need to search boxes[row][col][0] for "weeks" in some cases
            # if "week" in boxes[row][col][0].lower() or "weekrrrrrs" in boxes[row][col][0].lower():

            event.add('summary', found_event[0])
            event.add('dtstart', eventstartdate)
            event.add('dtend', eventenddate)
            while eventenddate < enddate:
                eventstartdate += timedelta(days=7)
                eventenddate += timedelta(days=7)
            event.add('rrule', {'freq': 'weekly', 'until': enddate, 'byday': [
                      s[:2].lower() for s in found_event[1]], 'byweek': [1, 2, 3]})
            cal.add_component(event)
    ics_stream = io.BytesIO(cal.to_ical())
    return send_file(
        ics_stream,
        as_attachment=True,
        download_name='sample.ics',
        mimetype='text/calendar'
    )

# if __name__=="__main__":
#        app.run(host='0.0.0.0', port=5000, debug=True)

# Text detection using EAST: finds bounding boxes on all words but not accurate enough
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
