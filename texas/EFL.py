"""
Note: This script requires that pytesseract, Tesseract, and all Tesseract
binaries are installed

@author Jenya Kahn-Lang
"""
import numpy as np
import pandas as pd
import os
import re
import pytesseract
import cv2  # Note: use pip install opencv-python
import pdf2image

try:
    from PIL import Image
except ImportError:
    import Image
from pytesseract import Output


# USER-DEFINED FUNCTIONS ------------------------------------------------------

# Convert a PDF file to an image file
def pdf_to_img(pdf_file):
    return pdf2image.convert_from_path(pdf_file)


# Use OCR to read an image; store the results in dictionary format
def ocr_core(file):
    text = pytesseract.image_to_data(file, output_type=Output.DICT)
    return text


# Convert the first page of a PDF file to a data dictionary using OCR
# ***there must be a less silly way to do this
def extract_pdf_data_1stpg(pdf_file):
    images = pdf_to_img(pdf_file)
    return ocr_core(images[0])


# Find the (index of the) bounding boxes within an image dictionary that
# contain certain text
def find_boxes_w_text(text, precision, d):
    matches_list = []
    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['conf'][i]) > precision:  # OCR precision requirement
            if re.match(text, d['text'][i]):

                matches_list.append(d['text'][i])
    print(matches_list)
    return matches_list


# MAIN CODE -------------------------------------------------------------------

# Set directory **CHANGE THIS TO LOCAL PATH (will make relative eventually)
base_directory = 'X:\\Python\\urap-scrape\\texas\\PDFs'

# Help python locate pytesseract  **MAY NEED TO CHANGE THIS
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

# For now, just grab a sample PDF for demonstration purposes
filenames = os.listdir(base_directory)
# f = filenames[10]
f = "12294.pdf"
pdf_file = os.path.join(base_directory, f)

# print_pages(image_file)
d = extract_pdf_data_1stpg(pdf_file)
print(d.keys())

# Show bounding boxes
images = pdf_to_img(pdf_file)
# Extract image
for i in images:
    img = i
    break  # only extracting the first page for now
# Convert image to Open cv format
img_cv = np.array(img.convert('RGB'))
# Convert RGB to BGR 
img_cv = img_cv[:, :, ::-1].copy()
# Get bounding boxes
n_boxes = len(d['text'])
for i in range(n_boxes):
    if int(d['conf'][i]) > 60:
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        img_cv = cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 255, 0), 2)
# Display image and boxes
cv2.imshow('img', img_cv)
cv2.waitKey(0)

# Find the (index of the) bounding boxes within an image dictionary that 
# contain various text
#
find_boxes_w_text('Energy', 0, d)
find_boxes_w_text('Charge', 0, d)
find_boxes_w_text('(Base|Fixed|Monthly|AMS)', 0, d)
find_boxes_w_text('([0-9])', 0, d)
find_boxes_w_text('\$', 0, d)
find_boxes_w_text('kWh', 0, d)
find_boxes_w_text('greater', 0, d)
find_boxes_w_text('less', 0, d)
find_boxes_w_text('than', 0, d)
find_boxes_w_text('more', 0, d)
find_boxes_w_text('below', 0, d)
find_boxes_w_text('least', 0, d)
find_boxes_w_text('use|usage', 0, d)
find_boxes_w_text('minimum', 0, d)
find_boxes_w_text('fee', 0, d)
find_boxes_w_text('credit', 0, d)
find_boxes_w_text('bill', 0, d)
find_boxes_w_text('delivery', 0, d)
find_boxes_w_text('distribution', 0, d)
find_boxes_w_text('transmission', 0, d)
# find_boxes_w_text('(Oncor|AEP|Centerpoint|TNMP|Mexico|', 0, d)
find_boxes_w_text('Example', 0, d)

"""
Thoughts:
- Use machine learning to extract text. Could try:
    - Making the features simply the text-bounding box pairs?
        - Although it's effectively the same, some of the ML methods may 
          perform better if I we midpt and height/width
    - Specifying word matches (and the associated bounding boxes) as features directly
        - Could even make the features the horizontal and vertical distances to a box
            - with those key words
        - We may want to make some of the text matching case insensitive
        - If the OCR seems to be doing a poor job, we can use the distance to 
          each of these words as features instead of only exact matches 
          
"""
