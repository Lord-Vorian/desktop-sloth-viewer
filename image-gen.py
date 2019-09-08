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
goal = 2  # daily goal for contributions. Big effect on image generated
average_window = 7  # days
rel_contributions = []  # rel = relevant

call([r'scrape.bat'])  # this .bat uses the submodded scraper to output "contributions.json'
# TODO make a version of this .bat to be called on Linux

with open('contributions.json') as source:
    all_contributions = json.load(source)

    if len(all_contributions) < window_length:
        window_length = len(all_contributions)  # just in case contributions are fewer than 256

    rel_contributions = all_contributions[-1:0-window_length-1:-1]  # step backward from most recent
    rel_contributions.reverse()  # to return the list to its original order
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
rolling_avg = [rel_contributions[0]['count']] * average_window

for i in range(0, window_length):
    today_count = rel_contributions[i]["count"]
    rolling_avg.append(today_count)
    rolling_avg.pop(0)
    cut_height = (sum(rolling_avg)/len(rolling_avg))/ goal
    # set the height of the bar to the average percent of goal over number of days in the window
    if cut_height < 1:  # ignore bars that need not be cut
        for line in range(column_ranges[i][0]-1,column_ranges[i][1]):
            for pixel in range(0, int(height * (1-cut_height))):
                greyscale = int(sum(px_edit[line, pixel]) / 3)  #TODO make this junk readable
                px_edit[line, pixel] = (int(greyscale/3),30,int(greyscale/3))

image1.show()
image1.save('temp.png','PNG')




