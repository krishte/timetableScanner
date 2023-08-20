# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 13:48:18 2023

@author: tejas
"""

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
import matplotlib.pyplot as plt


img = cv2.imread("timetable6.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)[470:495, 0:995]
blur = cv2.GaussianBlur(gray, (3,3), 0)
d = pytesseract.image_to_data(blur, output_type=Output.DICT, config='--psm 6')
print(d['text'])
flatten = gray.flatten()
freq = [0 for i in range(256)]
for val in flatten:
    freq[val] += 1

thresh1 = cv2.threshold(blur, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1]
plt.plot(freq)
plt.show()
cv2.imwrite("img.png", blur)