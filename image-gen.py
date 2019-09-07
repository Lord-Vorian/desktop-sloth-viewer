"""
Blend two images across user data from github gathered from a window of 256 days
lord-vorian 9/7/2019

256 days comes from this study on habit forming:
(https://centrespringmd.com/docs/How%20Habits%20are%20Formed.pdf)
"""

import json
from subprocess import call
from PIL import Image

window_length = 256  # days
goal = 2  # daily goal for contributions. Big effect on image generated
rel_contributions = []  # rel = relevant

call([r'scrape.bat'])  # this bat uses the submodded scraper to output "contributions.json'


with open('contributions.json') as source:
    all_contributions = json.load(source)

    if len(all_contributions) < window_length:
        window_length = len(all_contributions)  # just in case contributions are fewer than 256

    rel_contributions = all_contributions[-1:0-window_length-1:-1]  # step backward from most recent
    print('.json file parsed...')

image1 = Image.open('img\image1.jpg')
width, height = image1.size
print(width/window_length)


