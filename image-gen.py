"""
Blend two images across user data from github gathered from a window of 256 days
lord-vorian 9/7/2019

256 days comes from this study on habit forming:
(https://centrespringmd.com/docs/How%20Habits%20are%20Formed.pdf)
"""

import json
from os import path
from subprocess import call
from PIL import Image

window_length = 256  # days
goal = 5  # daily goal for contributions. Big effect on image generated
rel_contributions = []  # rel = relevant

#call([r'scrape.bat'])  # this .bat uses the submodded scraper to output "contributions.json'
# TODO make a version of this .bat to be called on Linux

with open('contributions.json') as source:
    all_contributions = json.load(source)

    if len(all_contributions) < window_length:
        window_length = len(all_contributions)  # just in case contributions are fewer than 256

    rel_contributions = all_contributions[-1:0-window_length-1:-1]  # step backward from most recent
    print('.json file parsed...')

image1 = Image.open('img\image1.jpg')  # TODO make this file-type agnostic
width, height = image1.size

column_ranges = []  # a set of pixel locations in x to be used as bars in the chart
column_width = width//window_length  # number of pixels in each column
                                     # TODO generate a line instead of a bar chart (looks better)

for column in range(0, window_length):  # give each column a single value: its width
    if column <= width % window_length:
        column_ranges.append([column_width+1])  # distribute remainder of pixels across remainder(th) columns
    else:                                       # ex: 1920 % 256 = 128. So add +1 to the first 128 columns
        column_ranges.append([column_width])

pixel_position = -1  # store pixel position across image. -1 so we arrive at 0 on first iteration
for column in range(0,len(column_ranges)):
    # turn this list of pixel widths into a list of pixel ranges

    column_ranges[column].append(column_ranges[column][0] + pixel_position)
    # add the width of this column to the position on the image to get the end of the range

    column_ranges[column][0] = pixel_position + 1
    # we no longer need the width, so we replace it with the current position + 1 pixel

    pixel_position = column_ranges[column][1]
    # update current position so it matched

# Now we edit image1 one pixel at a time . . . .

px_edit = image1.load()  # enables pixel editing with the PixelAccess class

for i in range(0, window_length):
    cut_height = rel_contributions[i]["count"]/goal
    # find percentage of goal achieved TODO make this a rolling 7-day average to smooth results.
    if cut_height < 1:  # ignore bars that need not be cut
        for line in range(column_ranges[i][0],column_ranges[i][1]):
            for pixel in range(0, int(height * (1-cut_height))):
                #assert (line in range(0,width) and pixel in range(0,height)), "bar {}\n"
                px_edit[line,pixel] = (0,0,0)

image1.show()




