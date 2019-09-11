"""
Blend two images across user data from github gathered from a window of 256 days

256 days comes from this study on habit forming:
(https://centrespringmd.com/docs/How%20Habits%20are%20Formed.pdf)
lord-vorian 9/7/2019
"""
# TODO Write a better docstring^^ (PEP 257)

import ctypes
from random import sample,choice
from json import load as jsonload
from os import path
from subprocess import run
from PIL import Image


class SlothChart:

    def __init__(self, user, window=256, goal=2, average_window=7):
        self.user = user
        self.goal = goal
        self.average_window = average_window
        self.window = window  # Both in days
        self.contributions = []
        self.gradients = sample.(range(250,1500),3)  # effects length of color gradient across the image.
        self.image1 = 0
        print(self.filter_mod)

        # Set up file loocations
        self.local_path = path.dirname(path.abspath(__file__))
        self.scraper = path.join(self.local_path, 'github-contributions-scraper', 'index.js')
        self.data = path.join(self.local_path, 'contributions.json')
        self.image_dir = path.join(self.local_path, 'img')
        self.save_as = path.join(self.local_path, 'result.bmp')
        self.update = path.join(self.local_path, 'Update_desk.bat')
        print('starting from {}'.format(self.local_path,))


    def filtered(self, image, x, y):
        """Use PIL's PixelAccess class to edit an individual pixel on the given image object"""
        xy = [x,y]
        px_edit = image.load()
        # Enables pixel editing with the PixelAccess class
        greyscale = int(sum(px_edit[x, y]) / 3)
        # Average the RGB values to come up with the grey scale. int() to avoid float

        R = int(greyscale / (xy[(self.gradients[0]%2)]/self.gradients[0]+1))
        G = int(greyscale / (xy[(self.gradients[1]%2)]/self.gradients[1]+1))
        B = int(greyscale / (xy[(self.gradients[2]%2)]/self.gradients[2]+1))

        px_edit[x, y] = (R,G,B)
        # This replaces the pixel. Play with this until you like the filter. TODO make dict of filters
        # Be warned: anything done in this func will have a big impact on processing speed TODO add this to docstring


    def get_contributions(self):
        run('node {} {} {}'.format( self.scraper, self.user, self.data))
        # call the scraper submod
        with open(self.data) as source:
            all_contributions = jsonload(source)

            if len(all_contributions) < self.window:
                self.window = len(all_contributions)  # Just in case contributions are fewer than 256

            self.contributions = all_contributions[-1:0-self.window-1:-1]  # Step backward from most recent
            self.contributions = self.contributions.reverse()  # To return the list to its original order
            print('.json file parsed...')
            return self.contributions

    def get_image(self):
        self.image1 = Image.open(path.join(self.image_dir, 'image1.jpg'))  # TODO make this file-type agnostic
        return self.image1

    def bar_chart_overlay(self):
        
        width, height = self.get_image()
        column_ranges = []  # A set of pixel locations in x to be used as bars in the chart
        column_width = width//self.window  # Number of pixels in each column

        # TODO generate a line instead of a bar chart (looks better)

        for column in range(self.window):  # Give each column a single value: its width
            if column <= width % self.window:
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
        self.get_contributions()
        rolling_avg = [self.contributions[0]['count']] * self.average_window
        for i in range(0, self.window):
            today_count = self.contributions[i]["count"]
            rolling_avg.append(today_count)
            rolling_avg.pop(0)
            cut_height = (sum(rolling_avg)/len(rolling_avg)) / self.goal
            # Set the height of the bar to the average percent of goal over number of days in the window
            if cut_height < 1:  # Ignore bars that need not be cut
                for line in range(column_ranges[i][0]-1, column_ranges[i][1]):  # (line = vertical line of pxls)
                    for pixel in range(0, int(height * (1-cut_height))):
                        self.filtered(self.image1, line, pixel)
        return self.image1


if __name__ == "__main__":
    BOOM =
    image1.save(path_dict['save as'], 'BMP')
    ctypes.windll.user32.SystemParametersInfoW(20, 0, path_dict['save as'], 3)  # Updates the desktop image
    # TODO make os independent
