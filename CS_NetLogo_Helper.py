from urllib.request import urlopen
import ssl
import re
import os
from threading import Thread
from datetime import datetime
from PyBookEngine import *
from pyperclip import copy
from time import time

# Made by interestingbookstore
# Github: https://github.com/interestingbookstore/randomstuff
# -----------------------------------------------------------------------
# Version 1.0.0-alpha
# ---------------------------------------------------------

background_brightness = 37
button_roundedness = 30
button_color = 40, 120, 190
button_width, button_height = 430, 90
button_gap = 30
amount_of_buttons = 3
button_container_padding = 42
button_container_outer_padding = 45
container_vertical_extra_padding = 0
button_container_color_offset = 15
button_container_radius_offset = -20
info_text_vertical_offset = 0
double_info_text_horizontal_offset = 170
text_clipboard_gap = 5
clipboard_size = 0.6
clipboard_brightness = 190
text_gap = 20
text_brightness = 190
extra_yres = 300

container_size = button_container_padding * 2 + button_width, button_container_padding * 2 + button_height * 3 + button_gap * 2
xres, yres = container_size[0] + button_container_outer_padding * 2, container_size[1] + (button_container_outer_padding + container_vertical_extra_padding) * 2 + extra_yres

latest_assignment_number = None
latest_nlogo_file = None
template = None
scale = None

with open('options.txt') as f:
    t = f.readlines()
    for line in t:
        option, value = line.split('=')
        value = value.lstrip().rstrip('\n').replace('\\n', '\n')
        option = option.strip('\n ')
        print(f'Option: {option}, Value: {value}')
        if option == 'heading':
            heading = value
        elif option == 'netlogo_save_folder':
            netlogo_save_folder = value.rstrip('/')
        elif option == 'elapsed_time_copy_to_clipboard_format':
            elapsed_time_copy_to_clipboard_format = value
        elif option == 'elapsed_time_display_format':
            elapsed_time_display_format = value
        elif option == 'scale':
            scale = float(value)


def get_latest_homework():
    global latest_assignment_number, latest_nlogo_file, template
    ssl._create_default_https_context = ssl._create_unverified_context

    url = 'https://www.davidmholmes.net/Stuy/1intro/hw.html'
    page = urlopen(url)

    text = page.read().decode('utf-8')
    latest_assignment_number = re.search('<h1 id="\d{1,3}">', text).group(0)[8:-2]
    latest_download_url = 'https://www.davidmholmes.net/Stuy/1intro/' + re.search('href=".+.nlogo', text).group(0)[6:]
    name = re.search('href=\".{1,100}.nlogo\".*\n.*download=\"(.+)\"', text).group(1)
    page2 = urlopen(latest_download_url)
    text2 = page2.read().decode('utf=8')
    latest_nlogo_file = name, text2
    with open('template.nlogo') as f:
        template = f.read()


x = Thread(target=get_latest_homework)
x.start()

g = Game((xres * 0.5 * scale, yres * 0.5 * scale), 'CS NetLogo Helper', resolution=(xres, yres))
s = g.scene()
s.set_background((background_brightness, background_brightness, background_brightness))
container_button_offset = button_container_outer_padding + button_container_padding
b1 = Button(container_button_offset, container_button_offset + button_height + button_gap + container_vertical_extra_padding, button_width, button_height, 'Generate and copy heading', 'Roboto-Bold.ttf', 30, (220, 220, 220), button_color, button_roundedness)
b2 = Button(container_button_offset, container_button_offset + container_vertical_extra_padding, button_width, button_height, 'Generate file for homework', 'Roboto-Bold.ttf', 30, (220, 220, 220), button_color, button_roundedness)
b3 = Button(container_button_offset, container_button_offset + (button_height + button_gap) * 2 + container_vertical_extra_padding, button_width, button_height, 'Download and add heading', 'Roboto-Bold.ttf', 30, (220, 220, 220), button_color, button_roundedness)
button_container_im = PyBookImage(container_size[0], container_size[1])
button_container_im.draw_rectangle(0, 0, container_size[0], container_size[1], (background_brightness + button_container_color_offset, background_brightness + button_container_color_offset, background_brightness + button_container_color_offset), button_roundedness + button_container_padding + button_container_radius_offset)
button_container = Sprite(button_container_im, button_container_outer_padding, button_container_outer_padding + container_vertical_extra_padding)
text_y = (yres - extra_yres - button_container_outer_padding) + (yres - (yres - extra_yres - button_container_outer_padding)) // 2 + info_text_vertical_offset
info_text_upper = Text('', 'Roboto-Medium.ttf', 30, (text_brightness, text_brightness, text_brightness), xres // 2 + double_info_text_horizontal_offset, text_y + text_gap, 'left')
info_text_lower = Text('', 'Roboto-Medium.ttf', 30, (text_brightness, text_brightness, text_brightness), xres // 2 + double_info_text_horizontal_offset, text_y - text_gap, 'left')
info_text_center = Text('', 'Roboto-Medium.ttf', 30, (text_brightness, text_brightness, text_brightness), xres // 2, text_y, 'center')
s.add(button_container, b1, b2, b3, info_text_upper, info_text_lower, info_text_center)
clipboard_im = PyBookImage('clipboard_icon')
clipboard_im.opacity_aware_fill((clipboard_brightness, clipboard_brightness, clipboard_brightness))
clip_w = clipboard_im.width
copy_button = Sprite(clipboard_im, xres // 2 + clip_w // 2 + double_info_text_horizontal_offset + text_clipboard_gap, text_y, clipboard_size, origin='m')
counting_start = False


@s.update_loop
def idk():
    global counting_start
    if latest_assignment_number is not None:
        if counting_start:
            info_text_center.text = ''
            if copy_button not in s:
                s.add(copy_button)
            info_text_lower.text = elapsed_time_display_format.replace('{time}', str(round((time() - counting_start) / 3600, 1)))

            if distance(g.mouse_position, copy_button) <= 50:
                g.force_mouse_cursor_to_hand()
                if g.just_pressed('left'):
                    copy(elapsed_time_copy_to_clipboard_format.replace('{time}', str(round((time() - counting_start) / 3600, 1))))

        if b1.pressed:
            info_text_lower.text = ''
            info_text_upper.text = ''
            counting_start = False
            if copy_button in s:
                s.remove(copy_button)

        if b1.pressed:
            copy(generate_heading())
            info_text_center.text = 'Heading copied!'
        if b2.pressed:
            fn = f'{netlogo_save_folder}/{latest_assignment_number}.nlogo'
            with open(fn, 'w') as f:
                f.write(f'{generate_heading()}{template}')
            os.startfile(fn)
            counting_start = time()
            info_text_upper.text = f'Time started: {datetime.now().strftime("%A %#I:%M %p") if g.os == "windows" else datetime.now().strftime("%A %-I:%M %p")}'
        if b3.pressed:
            fn = f'{netlogo_save_folder}/{latest_nlogo_file[0]}'
            with open(fn, 'w') as f:
                f.write(f'{generate_heading()}{latest_nlogo_file[1]}')
                os.startfile(fn)
            counting_start = time()
            info_text_upper.text = f'Time started: {datetime.now().strftime("%A %#I:%M %p") if g.os == "windows" else datetime.now().strftime("%A %-I:%M %p")}'


def generate_heading():
    return heading.replace('{latest_assignment_number}', latest_assignment_number)


g.run_game()
