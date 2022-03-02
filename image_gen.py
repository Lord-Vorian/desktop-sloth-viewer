"""
Blend two images across user data from github gathered from a window of 256 days

256 days comes from this study on habit forming:
(https://centrespringmd.com/docs/How%20Habits%20are%20Formed.pdf)
lord-vorian 9/7/2019
"""
# TODO Write a better docstring^^ (PEP 257)

import ctypes
from random import sample, choice
from os import path, getlogin, listdir
from os import name as os_name
from PIL import Image
import requests
from bs4 import BeautifulSoup


class SlothChart:

    def __init__(self, user, window=256, goal=2, average_window=7):
        self.user = user
        self.osUser = getlogin()
        self.goal = goal
        self.average_window = average_window  # for calculating a rolling average
        self.window = window  # Both in days
        self.contributions = []
        self.minimum_resolution = 720
        self.gradients = sample(range(250, 1500), 3)  # effects length of color gradient across the image.
        self.image1 = None
        self.image1_edit = None
        print('gradients:', self.gradients)
        # Set up file locations
        self.local_path = path.dirname(path.abspath(__file__))
        self.scraper = path.join(self.local_path, 'github-contributions-scraper', 'index.js')
        self.image_dir = path.join(self.local_path, 'pics', 'favorites')
        self.save_as = path.join(self.local_path,'pics', 'result.bmp')
        self.update = path.join(self.local_path, 'Update_desk.bat')
        print('starting from {}'.format(self.local_path,))

    def filtered(self, editor, x, y):
        """Use PIL's PixelAccess class to edit an individual pixel on the given image object"""
        xy = [x,y]
        greyscale = int(sum(editor[x, y]) / 3)
        # Average the RGB values to come up with the grey scale. int() to avoid float

        R = int(greyscale / (xy[(self.gradients[0] % 2)] / self.gradients[0]+1))  # +1 to avoid division by zero
        G = int(greyscale / (xy[(self.gradients[1] % 2)] / self.gradients[1]+1))
        B = int(greyscale / (xy[(self.gradients[2] % 2)] / self.gradients[2]+1))

        editor[x, y] = (R, G, B)
        # This replaces the pixel. Play with this until you like the filter. TODO make dict of filters
        # Be warned: anything done in this func will have a big impact on processing speed TODO add this to docstring

    def get_contributions(self):
        response = requests.get(f'https://github.com/users/{self.user}/contributions')
        page = BeautifulSoup(response.text, 'html.parser')
        all_contributions = []
        for i in page.find_all(attrs={'data-date': True}):
            all_contributions.append((i['data-date'], int(i['data-count'])))
        if len(all_contributions) < self.window:
            self.window = len(all_contributions)  # Just in case contributions are fewer than 256
        self.contributions.extend(all_contributions[-1:0-self.window-1:-1])  # Step backward from most recent
        self.contributions.reverse()  # To return the list to its original order
        return self.contributions

    def get_image(self):
        if os_name == 'nt':
            # in windows, new lock-screen backgrounds are auto-downloaded.
            # this should fetch all of the ones in landscape orientation and put them in the project folder
            # TODO find a way to access this windows location without hard-coding the address
            windows_lockscreen_dir = f"C:\\Users\\{self.osUser}\\AppData\\Local\\Packages\\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\\LocalState\\Assets"
            for file in listdir(windows_lockscreen_dir):
                file = Image.open(path.join(windows_lockscreen_dir,file))
                if file.size[0] > file.size[1] and file.size[1] >= self.minimum_resolution:
                    file.save(path.join(self.image_dir, f'{len(listdir(self.image_dir))}.jpeg'), 'JPEG')

        self.image1 = Image.open(path.join(self.image_dir, choice(listdir(self.image_dir))))
        # Pick a random image from favorites and open it
        return self.image1

    def bar_chart_overlay(self):
        self.get_image()
        width, height = self.image1.size
        column_ranges = []  # A set of pixel locations in x to be used as bars in the chart
        column_width = width//self.window  # Number of pixels in each column

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
        self.contributions = self.get_contributions()
        self.image1_edit = self.image1.load()  # Enables pixel editing with the PixelAccess class
        rolling_avg = [self.contributions[0]['count']] * self.average_window
        for i in range(0, self.window):
            today_count = self.contributions[i]['count']
            rolling_avg.append(today_count)
            rolling_avg.pop(0)
            cut_height = (sum(rolling_avg)/len(rolling_avg)) / self.goal
            # ^^Set the height of the bar to the average percent of goal over number of days in the window
            if cut_height < 1:  # Ignore bars that need not be cut
                for line in range(column_ranges[i][0]-1, column_ranges[i][1]):  # (line = vertical line of pxls)
                    for pixel in range(0, int(height * (1-cut_height))):
                        self.filtered(self.image1_edit, line, pixel)
        self.image1.save(self.save_as, 'BMP')
        ctypes.windll.user32.SystemParametersInfoW(20, 0, self.save_as, 3)  # Updates the desktop image
        # TODO make os independent ^^
        return self.image1

    def line_chart_overlay(self):
        self.image1_edit = self.get_image().load()
        width, height = self.image1.size
        self.get_contributions()

        step_width = width // self.window
        rolling_avg = [self.contributions[0][1]] * self.average_window
        xy_list = [[0,int(height * (sum(rolling_avg) / len(rolling_avg)) / self.goal)]]
        pixel_position = 0
        for day in range(self.window):
            today_count = self.contributions[day][1]
            rolling_avg.append(today_count)
            rolling_avg.pop(0)
            if day < width % self.window:
                xy_list.append([pixel_position + step_width + 1])
            else:
                xy_list.append([pixel_position + step_width])
            pixel_position = xy_list[-1][0]
            xy_list[-1].append(int(height * (sum(rolling_avg) / len(rolling_avg)) / self.goal))

        for x in range(width):
            cut_height = 'err'
            for pair in range(len(xy_list)):
                if x == xy_list[pair][0]:
                    cut_height = xy_list[pair][1]

                elif x > xy_list[pair][0]:
                    x1,y1 = xy_list[pair]
                    x2,y2 = xy_list[pair+1]
                    slope = (y2-y1)/(x2-x1)
                    offset = -(slope*x1 - y1)
                    cut_height = int(x*slope + offset)

            if cut_height < height:
                for y in range(height-cut_height):
                    self.filtered(self.image1_edit, x, y)

        self.image1.save(self.save_as, 'BMP')
        ctypes.windll.user32.SystemParametersInfoW(20, 0, self.save_as, 3)









if __name__ == "__main__":
    background_chart = SlothChart('Lord-Vorian', 256, 4, 30)
    background_chart.line_chart_overlay()

