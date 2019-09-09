"""
Blend two images across user data from github gathered from a window of 256 days

256 days comes from this study on habit forming:
(https://centrespringmd.com/docs/How%20Habits%20are%20Formed.pdf)
lord-vorian 9/7/2019
"""
# TODO Write a better docstring^^ (PEP 257)

import ctypes
from random import random
from json import load as jsonload
from os import path
from subprocess import run
from PIL import Image

window_length = 66  # Days
goal = 2  # Daily goal for contributions. Big effect on image generated
average_window = 7  # Days
user = 'lord-vorian'


path_dict = {"here": path.dirname(path.abspath(__file__))}
print('starting from {}'.format(path_dict["here"]))
path_dict.update([
    ("scraper", path.join(path_dict['here'], 'github-contributions-scraper', 'index.js')),
    ("data", path.join(path_dict['here'], 'contributions.json')),
    ("image dir", path.join(path_dict['here'], 'img')),
    ("save as", path.join(path_dict['here'], 'result.bmp')),
    ("update", path.join(path_dict['here'], 'Update_desk.bat')),
])

run('node {} {} {}'.format( path_dict['scraper'], user, path_dict['data']))
# call the scraper submod


fmod = random()
def filtered(image, x, y):
    """Use PIL's PixelAccess class to edit an individual pixel on the given image object"""
    px_edit = image.load()
    # Enables pixel editing with the PixelAccess class
    greyscale = int(sum(px_edit[x, y]) / 3)
    # Average the RGB values to come up with the grey scale. int() to avoid float
    px_edit[x, y] = (int(greyscale*fmod*.8),int(greyscale/8),int(greyscale*fmod*.5))
    # This replaces the pixel. Play with this until you like the filter. TODO make dict of filters
    # Be warned: anything done in this func will have a big impact on processing speed


rel_contributions = []  # rel = relevant
with open(path_dict['data']) as source:
    all_contributions = jsonload(source)

    if len(all_contributions) < window_length:
        window_length = len(all_contributions)  # Just in case contributions are fewer than 256

    rel_contributions = all_contributions[-1:0-window_length-1:-1]  # Step backward from most recent
    rel_contributions.reverse()  # To return the list to its original order
    print('.json file parsed...')

image1 = Image.open(path.join(path_dict['image dir'], 'image1.jpg'))  # TODO make this file-type agnostic
width, height = image1.size

column_ranges = []  # A set of pixel locations in x to be used as bars in the chart
column_width = width//window_length  # Number of pixels in each column

# TODO generate a line instead of a bar chart (looks better)

for column in range(window_length):  # Give each column a single value: its width
    if column <= width % window_length:
        column_ranges.append([column_width+1])  # Distribute remainder of pixels across remainder(th) columns
    else:                                       # ex: 1920 % 256 = 128. So add +1 to the first 128 columns
        column_ranges.append([column_width])

pixel_position = -1  # Store pixel position across image. -1 so we arrive at 0 on first iteration
for column in range(len(column_ranges)):
    # Turn this list of pixel widths into a list of pixel ranges

    column_ranges[column].append(column_ranges[column][0] + pixel_position)
    # Add the width of this column to the position on the image to get the end of the range

    column_ranges[column][0] = pixel_position + 1
    # We no longer need the width, so we replace it with the current position + 1 pixel

    pixel_position = column_ranges[column][1]
    # Update current position so it matched


# Now we edit image1 one pixel at a time . . . .

rolling_avg = [rel_contributions[0]['count']] * average_window
for i in range(0, window_length):
    today_count = rel_contributions[i]["count"]
    rolling_avg.append(today_count)
    rolling_avg.pop(0)
    cut_height = (sum(rolling_avg)/len(rolling_avg)) / goal
    # Set the height of the bar to the average percent of goal over number of days in the window
    if cut_height < 1:  # Ignore bars that need not be cut
        for line in range(column_ranges[i][0]-1, column_ranges[i][1]):  # (line = vertical line of pxls)
            for pixel in range(0, int(height * (1-cut_height))):
                filtered(image1, line, pixel)


image1.save(path_dict['save as'], 'BMP')
ctypes.windll.user32.SystemParametersInfoW(20, 0, path_dict['save as'], 3)  # Updates the desktop image
# TODO make os independent
