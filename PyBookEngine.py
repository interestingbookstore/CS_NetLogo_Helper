import pygame
import pygame.freetype
from PIL import Image, ImageFilter, ImageDraw
from platform import system
import copy
from PyBookImages import *

# Made by interestingbookstore
# Github: https://github.com/interestingbookstore/randomstuff
# -----------------------------------------------------------------------
# Comp Sci NetLogo Helper branch
# ---------------------------------------------------------


# -----  Drop Shadow Pre-Render  (It adds like 0.02 seconds, which is hardly anything for this context if you ask me)  --------------------------------------------------------------------------------------
drop_shadow_high_res = Image.new('RGBA', (800, 800))
draw = ImageDraw.Draw(drop_shadow_high_res)
draw.rectangle((200, 200, 600, 600), (0, 0, 0))
drop_shadow_high_res = drop_shadow_high_res.filter(ImageFilter.GaussianBlur(100))
drop_shadow_high_res = drop_shadow_high_res.crop((600, 0, 800, 200))


# ---------------------------------------------------------------------------------------------

def image_stuff(image, scale=1):
    if type(image) == pygame.Surface:
        return image

    if isinstance(image, PyBookImage):
        image.scale(scale)
        return pygame.image.fromstring(image.to_bytes(), image.size, 'RGBA')

    if type(image) == str:
        image = Image.open(image).convert()

    center_info = False

    if scale != 1:
        if type(scale) == tuple:
            image = image.resize(fit_image(image.size, scale))
            if image.size[0] == scale[0]:
                center_info = 0, (scale[1] - image.size[1]) // 2
            else:
                center_info = (scale[0] - image.size[0]) // 2, 0
        else:
            image = image.resize((round(image.size[0] * scale), round(image.size[1] * scale)))

    if not center_info:
        return pygame.image.fromstring(image.convert('RGBA').tobytes('raw', 'RGBA'), image.size, 'RGBA').convert_alpha()
    return pygame.image.fromstring(image.convert('RGBA').tobytes('raw', 'RGBA'), image.size, 'RGBA').convert_alpha(), center_info


def image_to_bytes_stuff(image):
    if isinstance(image, pygame.Surface):
        return pygame.image.tostring(image, 'RGBA', True)
    if isinstance(image, PyBookImage):
        return image.to_bytes()
    # if isinstance(image, Image):  # ???
    return image.convert('RGBA').tobytes('raw', 'RGBA')


def separate_sprite_sheet(image, h_images, v_images=None):
    if type(image) == str:
        im = Image.open(image)
    elif isinstance(image, Image.Image):
        im = image
    else:
        raise TypeError(f'Sprite sheet image expected to be either path or Pillow image, got "{type(image)}"')
    if v_images is None:
        if not (h_images ** 0.5).is_integer():
            raise Exception(f'{h_images} is not a perfect square, and as such, cannot be used to unpack the sprite sheet')
        h_images, v_images = int(h_images ** 0.5), int(h_images ** 0.5)

    xf = im.size[0] / h_images
    yf = im.size[1] / v_images
    if (not xf.is_integer()) and (not yf.is_integer()):
        raise Exception(f"Sprite sheet image given has a resolution of {im.size[0]} by {im.size[1]}, which isn't horizontally\ndividable by {h_images}, nor vertically dividable by {v_images}")
    if not xf.is_integer():
        raise Exception(f"Sprite sheet image given has a resolution of {im.size[0]} by {im.size[1]}, which isn't horizontally dividable by {h_images}")
    if not yf.is_integer():
        raise Exception(f"Sprite sheet image given has a resolution of {im.size[0]} by {im.size[1]}, which isn't vertically dividable by {v_images}")

    images = []
    for y in range(h_images):
        for x in range(v_images):
            images.append(im.crop((x * xf, y * yf, x * xf + xf, y * yf + yf)))
    return tuple(images)


def fit_image(image_res, maximum, scale_up=True, scale=False):
    x_fac = maximum[0] / image_res[0]
    y_fac = maximum[1] / image_res[1]

    if scale:
        return min(x_fac, y_fac)

    if not scale_up and x_fac >= 1 and y_fac >= 1:
        return image_res[0], image_res[1]

    if x_fac < y_fac:
        return maximum[0], round(image_res[1] * x_fac)
    return round(image_res[0] * y_fac), maximum[1]


def calculate_drop_shadow(size, blur):
    c = Image.new('RGBA', (blur, blur))

    # -----------------------------------------------------------------------------------------------------------------
    # c2 = c.load()
    # m = blur
    # m2 = (blur ** 2 + blur ** 2) ** 0.5
    # factor = 255 / m
    # for i in range(blur):
    #     for j in range(blur):
    #         j = blur - j - 1
    #         distance = m - (i ** 2 + j ** 2) ** 0.5
    #         if distance != 0:
    #             distance = m2 / distance * m2
    #         distance *= distance
    #         c2[i, blur - j - 1] = (0, 0, 0, round(distance * factor))
    # -----------------------------------------------------------------------------------------------------------------
    # c.putpixel((0, blur - 1), (0, 0, 0))
    # c = c.filter(ImageFilter.GaussianBlur(blur // 2))
    # -----------------------------------------------------------------------------------------------------------------
    c = drop_shadow_high_res.resize((blur, blur))
    # -----------------------------------------------------------------------------------------------------------------
    # c.save('0000AAATESTIMAGE3.png')

    sc = c.crop((0, 0, 1, blur))
    s1 = sc.resize((size[0], blur), 1)
    s2 = sc.resize((size[1], blur), 1)
    # s2.save('0000AAATESTIMAGE1.png')

    f = Image.new('RGBA', (size[0] + blur * 2, size[1] + blur * 2))
    f.paste(s1, (blur, 0))
    f.paste(s2.rotate(-90, expand=True), (size[0] + blur, blur))
    f.paste(s1.rotate(180), (blur, size[1] + blur))
    f.paste(s2.rotate(90, expand=True), (0, blur))

    f.paste(c, (size[0] + blur, 0))
    f.paste(c.rotate(90), (0, 0))
    f.paste(c.rotate(270), (size[0] + blur, size[1] + blur))
    f.paste(c.rotate(180), (0, size[1] + blur))
    # f.show()
    # f.save('0000AAATESTIMAGE2.png')

    return f


# calculate_drop_shadow((200, 200), 50)
# raise Exception

class TwoDimensionalList:
    def __init__(self, single_list, width):
        self.stuff = single_list
        self.width = width
        self.height = len(single_list) // self.width
        self.fancy_list = []
        fancy_buffer = []
        for i in self.stuff:
            fancy_buffer.append(i)
            if len(fancy_buffer) == self.width:
                self.fancy_list.append(fancy_buffer.copy())
                fancy_buffer.clear()
        if fancy_buffer:
            self.fancy_list.append(fancy_buffer)
        self.coords = []
        for index, _ in enumerate(self.stuff):
            self.coords.append((index % self.width, index // self.width))

    def check(self, index):
        if type(index) == list or type(index) == tuple:
            return index[0] + index[1] * self.width, index
        return index, (index % self.width, index // self.width)

    def __contains__(self, item):
        if self.check(item)[0] < len(self.stuff):
            return True
        return False

    def __getitem__(self, item):
        return self.stuff[self.check(item)[0]]

    def __setitem__(self, key, value):
        keys = self.check(key)
        self.stuff[keys[0]] = value
        self.fancy_list[keys[1][1]][keys[1][0]] = value

    def __repr__(self):
        return str('\n'.join(reversed([str(i) for i in self.fancy_list])))


class Sprite:
    def __init__(self, img, x, y, scale=1, drop_shadow=0, origin='bl'):
        self.rect_expansion_amount = 0

        self.img = img
        self._img = image_stuff(img, scale)
        self.x, self.y = x, y
        self.velocity = 0, 0
        self.current_speed = 0
        self._dim = self._img.get_size()
        self._width, self._height = self._dim
        self.origin = origin
        if self.origin == 'bl':
            self._rect = self.x - self.rect_expansion_amount, self.y - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount
        elif self.origin == 'm':
            self._rect = self.x - self._width // 2 - self.rect_expansion_amount, self.y - self._height // 2 - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount
        self._old_rect = 0, 0, 0, 0
        self.scale = scale
        self._old_scale = scale
        self.drop_shadow = drop_shadow

        self._update_area = True
        self._update_stuff = True

        self._img_bytes = image_to_bytes_stuff(self.img)

    def _update(self, game):
        self.current_speed = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity = 0, 0

        if self.origin == 'bl':
            self._rect = self.x - self.rect_expansion_amount, self.y - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount
        elif self.origin == 'm':
            self._rect = self.x - self._width // 2 - self.rect_expansion_amount, self.y - self._height // 2 - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount

        if self._img_bytes != (b2 := image_to_bytes_stuff(self.img)):
            self._img_bytes = b2
            self._img = image_stuff(self.img, self.scale)
            self._dim = self._img.get_size()
            self._width, self._height = self._dim[0], self._dim[1]
            self._update_area = True
            self._old_img = copy.copy(self.img)
            if self.origin == 'bl':
                self._rect = self.x - self.rect_expansion_amount, self.y - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount
            elif self.origin == 'm':
                self._rect = self.x - self._width // 2 - self.rect_expansion_amount, self.y - self._height // 2 - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount
            self._old_scale = self.scale
            self._update_stuff = False
        elif self._rect != self._old_rect:
            self._update_area = True

    def _draw(self, game):
        if self.drop_shadow != 0:
            ds = calculate_drop_shadow((self._width, self._height), self.drop_shadow)
            game.blit_image(image_stuff(ds), self._rect[0] - self.drop_shadow, self._rect[1] - self.drop_shadow)

        game.blit_image(self._img, self._rect[0], self._rect[1])

    def _update_screen(self, game, erase=False):
        if self._update_area or erase:
            game.update_screen(self._rect[0], self._rect[1], self._rect[2], self._rect[3], self._old_rect)
            self._old_rect = self._rect
            self._update_area = False

    def print_info(self, sprite_object=True, img=True, x=True, y=True, scale=True, drop_shadow=True, origin=True, update=True):
        string = ''
        if sprite_object:
            string += f'SPRITE object'
        if img:
            string += f'  img: {self.img}'
        if x:
            string += f'  x: {self.x}'
        if y:
            string += f'  y: {self.y}'
        if scale:
            string += f'  scale: {self.scale}'
        if drop_shadow:
            string += f'  drop_shadow: {self.drop_shadow}'
        if origin:
            string += f'  origin: {self.origin}'
        if update:
            f'  updating_this_frame: {self._update_area}'
        return string

    def __repr__(self):
        return f'SPRITE object  img: {self.img}  x: {self.x}  y: {self.y}  scale: {self.scale}  drop_shadow: {self.drop_shadow}  origin: {self.origin}  updating this frame: {self._update_area}'


def do_nothing(*idk):
    pass


class Text:
    def __init__(self, text, font, size, color, x, y, align='bottom left'):
        self.rect_expansion_amount = 0

        self.text = text
        self.font = font
        self._font2 = pygame.freetype.Font(font, size)
        self._font_surf, self.rect = self._font2.render(text, color, size=size)
        self.dim = self.rect.width, self.rect.height
        self.width, self.height = self.dim[0], self.dim[1]
        self.size = size
        self.color = color
        self.x, self.y = x, y
        self.align = align
        self._old_rect = 0, 0, 0, 0
        self._old_text = None
        self._x_offset = 0
        self._y_offset = 0

        self._update_area = True

    def _update(self, game):
        if self.text != self._old_text:
            self._font2 = pygame.freetype.Font(self.font, self.size)
            self._font_surf, self._rect = self._font2.render(str(self.text), self.color, size=self.size)
            self._font_surf = self._font_surf.convert_alpha()
            self.dim = self._font_surf.get_size()
            self.width, self.height = self.dim[0], self.dim[1]
            self._update_area = True
            self._old_text = self.text

        if self.align == 'top left':
            self._x_offset = -self.width
            self._y_offset = 0
        elif self.align == 'top':
            self._x_offset = -self.width // 2
        elif self.align == 'top right':
            self._x_offset = 0
            self._y_offset = 0
        elif self.align == 'left':
            self._x_offset = -self.width
            self._y_offset = -self.height // 2
        elif self.align == 'center':
            self._x_offset = -self.width // 2
            self._y_offset = -self.height // 2
        elif self.align == 'right':
            self._x_offset = 0
            self._y_offset = -self.height // 2
        elif self.align == 'bottom left':
            self._x_offset = -self.width
            self._y_offset = -self.height
        elif self.align == 'bottom':
            self._x_offset = -self.width // 2
            self._y_offset = self.height
        elif self.align == 'bottom right':
            self._x_offset = 0
            self._y_offset = self.height
        else:
            raise Exception(f'Alignments can be "left", "center", or "right", but {self.align} given')

        self._rect = self.x + self._x_offset, self.y + self._y_offset, self.width, self.height

    def _draw(self, game):
        game.blit_image(self._font_surf, self.x + self._x_offset, self.y + self._y_offset)

    def _update_screen(self, game, erase=False):
        if self._update_area or erase:
            game.update_screen(self._rect[0], self._rect[1], self._rect[2], self._rect[3], self._old_rect)
            self._old_rect = self._rect
            self._update_area = False


class Button:
    def __init__(self, x, y, width, height, text, font, font_size, text_color, color, corner_radius=0):
        self.x, self.y, self.width, self.height, self.text, self.font, self.font_size, self.text_color, self.color, self.corner_radius = x, y, width, height, text, font, font_size, text_color, color, corner_radius
        self._image = PyBookImage(width, height)
        self._image.draw_rectangle(0, 0, width, height, color, corner_radius)
        self._sprite_object = Sprite(self._image, x, y)
        self._text_object = Text(self.text, self.font, self.font_size, self.text_color, self.x + self.width // 2, self.y + self.height // 2, 'center')

        self._update_area = True

        self._previous_state = 'none'
        self._state = 'none'
        self.pressed = False
        self._colors = color, tuple([i + 50 for i in color]), tuple([i - 40 for i in color])

    def _update(self, game):
        self.pressed = False
        if self._state != self._previous_state:
            self._image.fill((0, 0, 0, 0))
            if self._state == 'none':
                self._image.draw_rectangle(0, 0, self.width, self.height, self._colors[0], self.corner_radius)
            elif self._state == 'hover':
                game.force_mouse_cursor_to_hand()
                self._image.draw_rectangle(0, 0, self.width, self.height, self._colors[1], self.corner_radius)
            elif self._state == 'pressed':
                self._image.draw_rectangle(0, 0, self.width, self.height, self._colors[2], self.corner_radius)
        self._previous_state = self._state
        self._sprite_object._update(game)
        self._text_object._update(game)
        if self._sprite_object._update_area or self._text_object._update_area:
            self._update_area = True

        if self._state == 'pressed' and game.just_released('left'):
            self.pressed = True
            self._state = 'hover'
        if rectangle_distance((self._sprite_object.x + self.width // 2, self._sprite_object.y + self.height // 2), game.mouse_position, (self.width // 2, self.height // 2)):
            self._state = 'hover'
            game.force_mouse_cursor_to_hand()
        else:
            self._state = 'none'
        if self._state == 'hover' and game.is_pressed('left'):
            self._state = 'pressed'

    def _draw(self, game):
        self._sprite_object._draw(game)
        self._text_object._draw(game)

    def _update_screen(self, game, erase=False):
        self._sprite_object._update_screen(game, erase)
        self._text_object._update_screen(game, erase)
        self._update_area = False


class Game:
    def __init__(self, viewport_resolution, title='Untitled Game', icon=None, frame=True, fps=60, resolution=(3840, 2160), disable_scaling=True):
        self.current_scene = None
        self._old_scene = self.current_scene
        self._run = True
        self.default_resolution = viewport_resolution
        self._resolution = self.default_resolution
        self.framerate = fps
        self.title = title
        self._title = title
        self.frame = frame
        self.scale = viewport_resolution[0] / resolution[0]
        self.mouse_cursor = 'normal'
        self._force_mouse_cursor_to_hand = False
        self._non_forced_cursor = self.mouse_cursor
        self._old_cursor = 'normal'

        self.os = system().lower()
        if self.os == 'darwin':
            self.os = 'macos'

        self.input_downs = []
        self.input_ups = []
        self.currently_pressed = []
        self.mouse_position = 0, 0
        self.quit_letters = 'q', 'u', 'i', 't'
        self.quit_progress = 0

        self.total_time = 0
        self.frame_count = 0
        self.delta = 0
        self._previous_frame_total_ticks = 0

        self.file_paths = None

        self._update_screen_in = 0

        pygame.init()
        if icon is not None:
            pygame.display.set_icon(pygame.image.load(icon))
        pygame.display.set_caption(title)
        if self.default_resolution == (pygame.display.Info().current_w, pygame.display.Info().current_h):
            self.frame = False
        if self.frame:
            self.screen = pygame.display.set_mode(self._resolution)
        else:
            self.screen = pygame.display.set_mode(self._resolution, pygame.NOFRAME)
        self.clock = pygame.time.Clock()

        self.display_resolution = self.screen.get_size()

        if disable_scaling:
            if system().lower() == 'windows':  # Say you're using Windows, and you have a 4K display. To make everything not really small, you set the scaling
                import ctypes  # to 200%. Great, but you want to be able to utilize the native resolution of your display. So, you have this, which tells Windows to ignore the scaling.

                PROCESS_PER_MONITOR_DPI_AWARE = 2
                ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

    def force_mouse_cursor_to_hand(self):
        self._force_mouse_cursor_to_hand = True

    def ny(self, y):
        return self._resolution[1] - y

    def generate_rect(self, x, y=None, width=None, height=None):
        if type(x) == tuple:
            y, width, height = x[1], x[2], x[3]
            x = x[0]
        x *= self.scale
        y *= self.scale
        width *= self.scale
        height *= self.scale
        return pygame.Rect(x, self._resolution[1] - y - height, width, height)

    def update_screen(self, x=None, y=None, width=None, height=None, old_rect=None):
        if type(x) == tuple:
            y, width, height = x[1], x[2], x[3]
            x = x[0]

        if x is None and y is None and width is None and height is None and old_rect is None:
            pygame.display.flip()
        else:
            x *= self.scale
            y *= self.scale
            width *= self.scale
            height *= self.scale

            if old_rect is not None:
                ox = old_rect[0] * self.scale
                oy = old_rect[1] * self.scale
                owidth = old_rect[2] * self.scale
                oheight = old_rect[3] * self.scale

                # pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(x, self._resolution[1] - y - height, width, height))
                # pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(ox, self._resolution[1] - oy - oheight, owidth, oheight))

                # pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect.union(pygame.Rect(x, self._resolution[1] - y - height, width, height), pygame.Rect(old_rect[0], self._resolution[1] - old_rect[1] - old_rect[3], old_rect[2], old_rect[3])))
                pygame.display.update(pygame.Rect.union(pygame.Rect(x, self._resolution[1] - y - height, width, height), pygame.Rect(ox, self._resolution[1] - oy - oheight, owidth, oheight)))
            else:
                pygame.display.update(pygame.Rect(x, self._resolution[1] - y - height, width, height))

    # pygame.display.update()

    def blit_image(self, image, x, y):
        x *= self.scale
        y *= self.scale
        res = round(image.get_width() * self.scale), round(image.get_height() * self.scale)
        self.screen.blit(pygame.transform.smoothscale(image, res), (x, self._resolution[1] - y - res[1]))

    def get_color_at_pixel(self, x, y):
        return self.screen.get_at((x, self._resolution[1] - y))[:3]

    def change_resolution(self, to):
        self._resolution = to
        if self.fullscreen:
            if self.frame:
                self.screen = pygame.display.set_mode(self._resolution, pygame.FULLSCREEN, pygame.HWSURFACE)
            else:
                self.screen = pygame.display.set_mode(self._resolution, pygame.FULLSCREEN, pygame.NOFRAME, pygame.HWSURFACE)
        else:
            if self.frame:
                self.screen = pygame.display.set_mode(self._resolution, pygame.HWSURFACE)
            else:
                self.screen = pygame.display.set_mode(self._resolution, pygame.NOFRAME, pygame.HWSURFACE)

        self._update_screen_in = 0.2

    def run_game(self):
        self._run = True
        mouse = pygame.mouse
        while self._run:
            self._force_mouse_cursor_to_hand = False
            self.frame_count += 1
            self.total_time += self.delta
            self.clock.tick(self.framerate)
            t = pygame.time.get_ticks()
            self.input_ups.clear()
            self.input_downs.clear()
            self.file_paths = None

            if self.title != self._title:
                pygame.display.set_caption(self.title)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._run = False

                if event.type == pygame.DROPFILE:
                    self.file_paths = str(event.file)

                if event.type == pygame.KEYDOWN:
                    key = pygame.key.name(event.key)
                    if key == 'left' or key == 'right' or key == 'up' or key == 'down':
                        key += '_arrow'
                    key = key.replace(' ', '_')
                    if key == 'left_shift' or key == 'right_shift':
                        self.input_downs.append('shift')
                    self.input_downs.append(key)
                    if key == self.quit_letters[self.quit_progress]:
                        self.quit_progress += 1
                        if self.quit_progress == len(self.quit_letters):
                            self._run = False
                    else:
                        self.quit_progress = 0
                if event.type == pygame.KEYUP:
                    key = pygame.key.name(event.key)
                    if key == 'left' or key == 'right' or key == 'up' or key == 'down':
                        key += '_arrow'
                    key = key.replace(' ', '_')
                    if key == 'left_shift' or key == 'right_shift':
                        self.input_ups.append('shift')
                    self.input_ups.append(key)

                if event.type == pygame.MOUSEMOTION:
                    position = mouse.get_pos()
                    self.mouse_position = position[0] // self.scale, (self._resolution[1] - position[1]) // self.scale
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pressed = mouse.get_pressed(3)
                    if pressed[0]:
                        self.input_downs.append('left')
                    if pressed[2]:
                        self.input_downs.append('right')
                    if pressed[1]:
                        self.input_downs.append('middle')
                if event.type == pygame.MOUSEBUTTONUP:
                    pressed = mouse.get_pressed(3)
                    if not pressed[0] and 'left' in self.currently_pressed:
                        self.input_ups.append('left')
                    if not pressed[2] and 'right' in self.currently_pressed:
                        self.input_ups.append('right')
                    if not pressed[1] and 'middle' in self.currently_pressed:
                        self.input_ups.append('middle')

            for i in self.input_downs:
                self.currently_pressed.append(i)

            for i in self.input_ups:
                self.currently_pressed.remove(i)

            if self._update_screen_in > 0 and self._update_screen_in - self.delta <= 0:
                self.update_screen()
            if self._update_screen_in > 0:
                self._update_screen_in -= self.delta
                if self._update_screen_in < 0:
                    self._update_screen_in = 0

            self.current_scene.run_scene()
            if self.current_scene != self._old_scene:
                self.current_scene.redraw = True
                self._old_scene = self.current_scene

            if self._force_mouse_cursor_to_hand:
                if self.mouse_cursor != 'hand':
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    self._old_cursor = 'hand'
            else:
                if self.mouse_cursor != self._old_cursor:
                    if self.mouse_cursor == 'normal':
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    elif self.mouse_cursor == 'hand':
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        raise Exception(f'Mouse cursor options are "normal" or "hand", but {self.mouse_cursor} was given.')
                    self._old_cursor = self.mouse_cursor

            self.delta = (t - self._previous_frame_total_ticks) / 1000
            self._previous_frame_total_ticks = t

    def just_pressed(self, button):
        if button in self.input_downs:
            return True
        return False

    def just_released(self, button):
        if button in self.input_ups:
            return True
        return False

    def just_interacted(self, button):
        if button in self.input_downs or button in self.input_ups:
            return True
        return False

    def is_pressed(self, button):
        if button in self.currently_pressed:
            return True
        return False

    def get_action_strength(self, button):
        if button in self.currently_pressed:
            return 1
        return 0

    def quit(self):
        self._run = False

    def switch_scene(self, scene):
        self.current_scene = scene
        scene.redraw = True

    def constrict_to_screen(self, value, constricted_to, width=0, height=0, scale=False):
        def constrict(valueidk, plus, axis=0):
            if valueidk < 0:
                if not scale:
                    return 0
                else:
                    return 0, plus + valueidk
            elif valueidk + plus > self._resolution[axis]:
                if not scale:
                    return self._resolution[axis] - plus
                else:
                    return valueidk, plus - ((valueidk + plus) - (self._resolution[axis]))
            if not scale:
                return valueidk
            else:
                return valueidk, plus

        if constricted_to == 'x':
            if type(value) == int or type(value) == float:
                return constrict(value, width)
            return constrict(value.x, value.width)
        elif constricted_to == 'y':
            if type(value) == int or type(value) == float:
                return constrict(value, width, 1)
            return constrict(value.x, value.height, 1)

        if type(value) == int or type(value) == float:
            return constrict(value, width), constrict(constricted_to, height, 1)
        return constrict(value.x, value.width), constrict(constricted_to.x, constricted_to.height, 1)

    def scene(self):
        new_scene = self.Scene(self)
        if self.current_scene is None:
            self.current_scene = new_scene
        return new_scene

    class Scene:
        def __init__(self, game):
            self._game = game
            self._stuff = []
            self._update_loop = do_nothing
            self.resolution = self._game.default_resolution
            self.background = 0, 0, 0
            self._old_background = self.background
            self._background_center = 0, 0
            self._redraw = False

        def clear(self):
            self._stuff = []

        def __contains__(self, item):
            if item in self._stuff:
                return True
            return False

        def set_background(self, background, _update=True):
            if type(background) == pygame.Surface:
                self.background = background
                self._game.screen.blit(self.background, self._background_center)
            elif type(background) == tuple:
                self.background = background
                self._game.screen.fill(self.background)
            else:
                self.background, self._background_center = image_stuff(background, self._game._resolution)
                self._game.screen.blit(self.background, self._background_center)

        def coordinate_in_sprite(self, coord, object):
            if object.origin == 'm':
                object_point = object.x, object.y
            else:
                object_point = object.x + object.width // 2, object.y + object.height // 2
            if rectangle_distance(coord, object_point, (object._dim[0] // 2, object._dim[1] // 2)):
                return True
            return False

        def run_scene(self):
            if self.resolution != self._game._resolution:
                self._game.change_resolution(self.resolution)

            self.set_background(self.background)
            if self.background != self._old_background:
                self._old_background = self.background
                self._redraw = True

            try:
                self._update_loop(self._game.delta)
            except TypeError:
                self._update_loop()

            for i in self._stuff:
                i._update(self._game)

            draw_all = False

            for i in self._stuff:
                if i._update_area:
                    draw_all = True
                    break

            if draw_all or self._redraw:
                for i in self._stuff:
                    i._draw(self._game)
            if self._redraw:
                self._game.update_screen()
                self._redraw = False
            else:
                for i in self._stuff:
                    i._update_screen(self._game)

        def update_loop(self, function):
            self._update_loop = function

        def add(self, *objects, position=-1):
            if type(objects[0]) == tuple or type(objects[0]) == list:
                for i in objects[0]:
                    i._update_area = True
                    self._stuff.append(i)
            else:
                for i in objects:
                    i._update_area = True
                    self._stuff.append(i)
            # self.stuff.insert(position, i)  # ??? An item was inserted in the second to last slot, and not the last slot???

        def remove(self, *objects):
            for i in objects:
                self._stuff.remove(i)
                self._redraw = True

        def key_bind(self, key, value, value2, negative, key_down_list, key_up_list):
            if key in key_down_list:
                value += value2 if negative else -value2
            elif key in key_up_list:
                value -= value2 if negative else -value2
            return value


def distance(obj_1, obj_2):
    if (type(obj_1) == int or type(obj_1) == float) and (type(obj_2) == int or type(obj_2) == float):
        return abs(obj_2 - obj_1)

    x1 = obj_1[0] if type(obj_1) == tuple else (obj_1.x + obj_1._width // 2 if obj_1.origin == 'bl' else obj_1.x)
    y1 = obj_1[1] if type(obj_1) == tuple else (obj_1.y + obj_1._height // 2 if obj_1.origin == 'bl' else obj_1.y)
    x2 = obj_2[0] if type(obj_2) == tuple else (obj_2.x + obj_2._width // 2 if obj_2.origin == 'bl' else obj_2.x)
    y2 = obj_2[1] if type(obj_2) == tuple else (obj_2.y + obj_2._height // 2 if obj_2.origin == 'bl' else obj_2.y)

    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def rectangle_distance(object_1, object_2, radius: int or float or tuple or list):
    if type(radius) == tuple or type(radius) == list:
        if len(radius) != 2:
            raise Exception(f'Radius should either be a float or an iterable of size 2, but a {"tuple" if type(radius) == tuple else "list"} of size {len(list)} was given instead.')
        if object_1[0] - radius[0] <= object_2[0] <= object_1[0] + radius[0] and object_1[1] - radius[1] <= object_2[1] <= object_1[1] + radius[1]:
            return True
    else:
        if object_1[0] - radius <= object_2[0] <= object_1[0] + radius and object_1[1] - radius <= object_2[1] <= object_1[1] + radius:
            return True
    return False


def move_toward(val1, to, amount_at_a_time, velocity=False):
    # Takes one value, moves it closer by AMOUNT_AT_A_TIME until it's TO.
    # To clarify, if TO is farther away from VAL1, it'll take that much longer to get there.

    new_val = val1

    if type(val1) == int and type(to) == int:
        if to > new_val:
            new_val += amount_at_a_time
            if new_val > to:
                new_val = to
        else:
            new_val -= amount_at_a_time
            if new_val < to:
                new_val = to
        dist = normalize(new_val - val1)
        if velocity:
            return dist
        return new_val
    elif type(val1) == tuple and type(to) == tuple:
        vector = to[0] - val1[0], to[1] - val1[1]
        dist = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
        vector = normalize(vector)

        if amount_at_a_time > dist:
            amount_at_a_time = dist

        vector = vector[0] * amount_at_a_time, vector[1] * amount_at_a_time

        if velocity:
            return vector
        return val1[0] + vector[0], val1[1] + vector[1]

    else:
        raise TypeError(f'The lerp function accepts two integers or two tuples, but a {type(val1)} and a {type(to)} were given.')


def normalize(vector):
    distance2 = (vector[0] ** 2 + vector[1] ** 2) ** 0.5

    if distance2 == 0:
        return vector

    return vector[0] / distance2, vector[1] / distance2