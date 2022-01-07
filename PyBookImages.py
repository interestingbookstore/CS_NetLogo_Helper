import PIL.Image
from PIL import Image, ImageDraw, ImageFont


# Made by interestingbookstore
# Github: https://github.com/interestingbookstore/randomstuff
# -----------------------------------------------------------------------
# Comp Sci NetLogo Helper branch
# ---------------------------------------------------------


def r(start, stop):
    if start > stop:
        for i in range(stop, start + 1):
            yield i
    else:
        for i in range(start, stop + 1):
            yield i


class PyBookImage:
    def __init__(self, *params):
        self.img = None
        self.d = None
        self.resx, self.resy = None, None
        self.width, self.height = None, None
        self.size = None

        parameter_sizes = 1, 2, 3
        if len(params) not in parameter_sizes:
            Exception('Parameters can either be "{path to image}" or (width, height, background=(0, 0, 0, 0))')
        if len(params) == 1 or (len(params) == 2 and isinstance(params[0], str)):
            extensions = ['', '.png', '.jpg']
            while True:
                try:
                    if len(extensions) == 0:
                        raise IndexError
                    self.im = Image.open(params[0] + extensions[0]).convert('RGBA')
                    self.update_dimensions_and_stuff()
                    if len(params) == 2:
                        self.resize(params[1])
                    break
                except FileNotFoundError:
                    extensions.pop(0)
                except IndexError:
                    self.im = Image.open(params[0])
        else:
            if len(params) == 2:
                params = params[0], params[1], (0, 0, 0, 0)
            width, height, background = params
            self.im = Image.new('RGBA', (width, height), background)
            self.update_dimensions_and_stuff()

    def update_dimensions_and_stuff(self):
        self.img = self.im.load()
        self.d = ImageDraw.Draw(self.im)
        self.resx, self.resy = self.im.size
        self.width, self.height = self.resx, self.resy
        self.size = self.width, self.height

    def __getitem__(self, item):
        return self.img[item[0], self.normalize_y(item[1])]

    def __setitem__(self, key, value):
        x, y = key[0], self.normalize_y(key[1])
        if (0 <= x < self.width) and (0 <= y < self.height):
            if len(value) == 3:
                nc = value
                nt = 1
            else:
                nc = value[:3]
                nt = value[3] / 255
            oc, ot = self.img[x, y][:3], self.img[x, y][3]
            nc2 = nc[0] * nt + oc[0] * (255 - nt), nc[1] * nt + oc[1] * (255 - nt), nc[2] * nt + oc[2] * (255 - nt), (ot + nt) * 255
            nc2 = tuple(255 if round(i) > 255 else round(i) for i in nc2)
            self.img[x, y] = nc2

    def show(self):
        self.im.show()

    def to_bytes(self):
        return self.im.tobytes('raw', 'RGBA')

    def resize(self, width, height=None, interpolation='bicubic'):
        interpolation_dict = {'nearest': PIL.Image.NEAREST, 'bilinear': PIL.Image.BILINEAR, 'bicubic': PIL.Image.BICUBIC, 'lanczos': PIL.Image.NEAREST}
        if interpolation not in interpolation_dict:
            raise Exception(f'Interpolation can be "nearest", "bilinear", "bicubic", or "lanczos". But {interpolation} given.')
        if height is None:
            if type(width) == int:
                height = round(width / self.width * self.height)
            else:
                width, height = width
        self.im = self.im.resize((width, height), interpolation_dict[interpolation])
        self.update_dimensions_and_stuff()

    def scale(self, scale):
        self.resize(round(self.width * scale))

    def opacity_aware_fill(self, color):
        for x in range(self.width):
            for y in range(self.height):
                self[x, y] = color[0], color[1], color[2], self[x, y][3]

    def remove_transparency(self):
        self.im = self.im.convert('RGB').convert('RGBA')
        self.update_dimensions_and_stuff()

    def make_bw(self):
        self.im = self.im.convert('LA').convert('RGBA')
        self.update_dimensions_and_stuff()

    def normalize_y(self, *y):
        if len(y) == 2:
            return y[0], self.resy - y[1] - 1
        if len(y) == 1:
            return self.resy - y[0] - 1
        raise Exception(f'Either "y" or "x, y" value expected, but {y} given')

    def fix_color(self, color):
        if len(color) == 3:
            return color[0], color[1], color[2], 255
        if len(color) == 4:
            return color
        raise Exception(f'RGB or RGBA color expected, but {len(color)} channel long color given: {color}')

    def fill(self, color):
        self.im.paste(color, (0, 0, self.resx, self.resy))

    def add_point(self, x, y, color, image=None, set=False):
        # DEPRECATED: USE __setitem__
        if image is None:
            image = self.img

        y = self.normalize_y(y)
        if 0 <= x < self.resx and 0 <= y < self.resy:
            if set:
                image[x, y] = color
            else:
                if len(color) == 4:
                    nt = color[3]
                    color = color[:3]
                else:
                    nt = 255
                old = image[x, y]
                ot = old[3]
                old = old[:3]
                st = nt + ot
                new = [0, 0, 0, 0]
                for index, i in enumerate(color):
                    new[index] = round(old[index] * (ot - nt) / 255 + color[index] * nt)
                new[3] = st
                for index, i in enumerate(new):
                    if i > 255:
                        new[index] = 255

                image[x, y] = tuple(new)

        if image != self.img:
            return image

    def draw_line(self, start, end, thickness, color):
        if len(color) == 3:
            color = color[0], color[1], color[2], 255

        top_left = list(start)
        if end[0] < start[0]:
            top_left[0] = end[0]
        if end[1] < start[1]:
            top_left[1] = end[1]

        sx, sy = start
        ex, ey = end

        if sx > ex:
            sx2 = ex - thickness
            ex2 = sx + thickness
        else:
            sx2 = sx - thickness
            ex2 = ex + thickness
        if sy > ey:
            sy2 = ey - thickness
            ey2 = sy + thickness
        else:
            sy2 = sy - thickness
            ey2 = ey + thickness

        line_im = Image.new('RGBA', (self.resx, self.resy))
        line_img = line_im.load()
        self.draw_circle(start, thickness, color, line_img)
        self.draw_circle(end, thickness, color, line_img)

        for x in r(sx2, ex2):
            for y in r(sy2, ey2):
                line_length = ((sx - ex) ** 2 + (sy - ey) ** 2) ** 0.5
                distance = ((x - sx) ** 2 + (y - sy) ** 2) ** 0.5
                distance2 = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5
                if distance < distance2:
                    distance_long = distance2
                    cx, cy = sx, sy
                else:
                    distance_long = distance
                    cx, cy = ex, ey
                if cx - thickness <= x <= cx + thickness and cy - thickness <= y <= cy + thickness:
                    if distance_long > line_length:
                        continue

                if end[0] == start[0]:
                    intersection_x = start[0]
                    intersection_y = y
                elif end[1] == start[1]:
                    intersection_x = x
                    intersection_y = start[1]
                else:
                    slope_1 = (end[1] - start[1]) / (end[0] - start[0])
                    slope_2 = -1 / slope_1
                    offset_1 = start[1] - slope_1 * start[0]
                    offset_2 = y - slope_2 * x
                    intersection_x = (offset_2 - offset_1) / (slope_1 - slope_2)
                    intersection_y = slope_2 * intersection_x + offset_2
                distance = ((x - intersection_x) ** 2 + (y - intersection_y) ** 2) ** 0.5
                if distance <= thickness:
                    line_img = self.add_point(x, y, color, line_img, True)
                else:
                    distance -= thickness
                    if distance < 1:
                        line_img = self.add_point(x, y, (color[0], color[1], color[2], round(color[3] * (1 - distance))), line_img, True)
        self.im.alpha_composite(line_im, (0, 0))

    def draw_quadrant(self, x, y, radius, color, quadrant='tl', keep_middle=True):
        color = self.fix_color(color)
        if quadrant == 'tl':
            sx, sy, ex, ey = x - radius, y, x, y + radius
        elif quadrant == 'tr':
            sx, sy, ex, ey = x, y, x + radius, y + radius
        elif quadrant == 'bl':
            sx, sy, ex, ey = x - radius, y - radius, x, y
        elif quadrant == 'br':
            sx, sy, ex, ey = x, y - radius, x + radius, y
        else:
            raise Exception(f'Quadrant can be "tl", "tr", "bl", or "br", but "{quadrant}" given.')

        if not keep_middle:
            if sx == x:
                if ex > sx: sx += 1
                else: sx -= 1
            if ex == x:
                if sx > ex: ex += 1
                else: ex -= 1
            if sy == y:
                if ey > sy: sy += 1
                else: sy -= 1
            if ey == y:
                if sy > ey: ey += 1
                else: ey -= 1

        for x2 in r(sx, ex):
            for y2 in r(sy, ey):
                d = ((x2 - x) ** 2 + (y2 - y) ** 2) ** 0.5
                if d <= radius:
                    self[x2, y2] = color
                else:
                    d -= radius
                    if d < 1:
                        self[x2, y2] = color[0], color[1], color[2], round(color[3] * (1 - d))

    def draw_rectangle(self, x, y, width, height, color, corner_radius=0):
        if corner_radius == 0:
            self.d.rectangle((self.normalize_y(x, y), self.normalize_y(x + width, y + height)), color)
        else:
            self.draw_rectangle(x + corner_radius, y + height - corner_radius, width - corner_radius * 2, corner_radius, color)
            self.draw_rectangle(x, y + corner_radius, width, height - corner_radius * 2, color)
            self.draw_rectangle(x + corner_radius, y, width - corner_radius * 2, corner_radius, color)
            self.draw_quadrant(x + corner_radius, y + height - corner_radius, corner_radius, color, 'tl', False)
            self.draw_quadrant(x + width - corner_radius, y + height - corner_radius, corner_radius, color, 'tr', False)
            self.draw_quadrant(x + corner_radius, y + corner_radius, corner_radius, color, 'bl', False)
            self.draw_quadrant(x + width - corner_radius, y + corner_radius, corner_radius, color, 'br', False)

    def draw_lines(self, points, thickness, color, close=False):
        if close:
            points.append(points[0])

        line_im = Image.new('RGBA', (self.resx, self.resy))
        line_img = line_im.load()

        lines = [(i, points[index - 1]) for index, i in enumerate(points)]

        for i in lines:
            start, end = i
            if len(color) == 3:
                color = color[0], color[1], color[2], 255

            top_left = list(start)
            if end[0] < start[0]:
                top_left[0] = end[0]
            if end[1] < start[1]:
                top_left[1] = end[1]

            sx, sy = start
            ex, ey = end

            if sx > ex:
                sx2 = ex - thickness
                ex2 = sx + thickness
            else:
                sx2 = sx - thickness
                ex2 = ex + thickness
            if sy > ey:
                sy2 = ey - thickness
                ey2 = sy + thickness
            else:
                sy2 = sy - thickness
                ey2 = ey + thickness

            self.draw_circle(start, thickness, color, line_img)
            self.draw_circle(end, thickness, color, line_img)

            for x in r(sx2, ex2):
                for y in r(sy2, ey2):
                    line_length = ((sx - ex) ** 2 + (sy - ey) ** 2) ** 0.5
                    distance = ((x - sx) ** 2 + (y - sy) ** 2) ** 0.5
                    distance2 = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5
                    if distance < distance2:
                        distance_long = distance2
                        cx, cy = sx, sy
                    else:
                        distance_long = distance
                        cx, cy = ex, ey
                    if cx - thickness <= x <= cx + thickness and cy - thickness <= y <= cy + thickness:
                        if distance_long > line_length:
                            continue

                    if end[0] == start[0]:
                        intersection_x = start[0]
                        intersection_y = y
                    elif end[1] == start[1]:
                        intersection_x = x
                        intersection_y = start[1]
                    else:
                        slope_1 = (end[1] - start[1]) / (end[0] - start[0])
                        slope_2 = -1 / slope_1
                        offset_1 = start[1] - slope_1 * start[0]
                        offset_2 = y - slope_2 * x
                        intersection_x = (offset_2 - offset_1) / (slope_1 - slope_2)
                        intersection_y = slope_2 * intersection_x + offset_2
                    distance = ((x - intersection_x) ** 2 + (y - intersection_y) ** 2) ** 0.5
                    if distance <= thickness:
                        line_img = self.add_point(x, y, color, line_img, True)
                    else:
                        distance -= thickness
                        if distance < 1:
                            line_img = self.add_point(x, y, (color[0], color[1], color[2], round(color[3] * (1 - distance))), line_img, False)
        self.im.alpha_composite(line_im, (0, 0))
        # for point, point2 in lines:
        #     point = point[0], self.normalize_y(point[1])
        #     im_negative = line_im.crop((point[0] - thickness, point[1] - thickness, point[0] + thickness, point[1] + thickness))
        #     source = im_negative.split()
        #     a = source[3].point(lambda i: 255 - i)
        #     im_negative = Image.merge('RGBA', (source[0], source[1], source[2], a))
        #
        #     im_negative.save('aaahi.png')

    def draw_square(self, origin, radius, fill):
        for x in r(origin[0] - radius, origin[0] + radius):
            for y in r(origin[1] - radius, origin[1] + radius):
                self.add_point(x, y, fill)

    def draw_circle(self, origin, radius, fill, image=None):
        if len(fill) == 3:
            fill = fill[0], fill[1], fill[2], 255
        origin = origin[0], origin[1]

        for x in r(origin[0] - radius, origin[0] + radius):
            for y in r(origin[1] - radius, origin[1] + radius):
                distance = ((x - origin[0]) ** 2 + (y - origin[1]) ** 2) ** 0.5

                if distance <= radius:
                    self.add_point(x, y, fill, image)
                else:
                    distance -= radius
                    if distance < 1:
                        self.add_point(x, y, (fill[0], fill[1], fill[2], round(fill[3] * (1 - distance))), image)

    def draw_text(self, text, x, y, size, font, color, anchor='m'):
        if anchor == 'tl':
            anchor = 'lt'
        elif anchor == 't':
            anchor = 'mt'
        elif anchor == 'tr':
            anchor = 'rt'
        elif anchor == 'l':
            anchor = 'lm'
        elif anchor == 'm':
            anchor = 'mm'
        elif anchor == 'r':
            anchor = 'rm'
        elif anchor == 'bl':
            anchor = 'ls'
        elif anchor == 'b':
            anchor = 'ms'
        elif anchor == 'br':
            anchor = 'rs'

        font = ImageFont.truetype(font, size)
        self.d.text(self.normalize_y((x, y)), text, color, font, anchor)

    def save(self, path):
        if '.' not in path:  # It's lazy, and not perfect, I'll get back to it.
            path += '.png'
        self.im.save(path)

    def save_show(self):
        self.im.save('AAAAA.png')