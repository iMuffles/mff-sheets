from io import BytesIO
import requests
from typing import ByteString
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import numpy as np
from ast import literal_eval
import sys
import os
Image.MAX_IMAGE_PIXELS = 1000000000

import urllib.request
import io
import requests

class TextSheet:
    def __init__(self, filename):

        # Read files
        with open(f"infographics/{filename}/script.txt", 'r') as f:
            self.content = f.readlines()

        # Colours
        self.charcoal = (54, 69, 79)

        # Variables
        self.filename = filename
        self.y = 0
        self.img = 1
        self.cards = []  # list of cards for slicing into sections later

        # Slate and Mask
        self.slate = Image.new('RGBA', (2000, 45000), self.charcoal)

        # Parse
        self.parse()

        # Cut
        self.slate = self.slate.crop((0, 0, 2000, self.y + 50))

        # Chuck title on top
        w1, h1 = self.slate.size
        head_img = Image.open(f'infographics/{filename}/title.png').convert(
            "RGBA")
        w2, h2 = head_img.size
        new_slate = Image.new('RGBA', (2000, h1 + h2))
        new_slate.paste(head_img, (0, 0), head_img)
        new_slate.paste(self.slate, (0, h2), self.slate)

        # Format self.card coords to account for title
        self.cards.append(self.y + 50)
        self.cards = [x + h2 for x in self.cards]
        self.cards.insert(0, 0)

        new_slate.show()

        new_slate = new_slate.convert('RGB')
        new_slate.save(f'output/{filename}.png')
        print("SAVED")

        print("Create album of separate images?")
        if input().lower() in ['y', 'yes', 'ye', 'yeah', 'yeas']:
            try:
                os.mkdir(f'output/{self.filename}')
            except FileExistsError:
                pass
            for i in range(1, len(self.cards)):
                section = new_slate.crop(
                    (0, self.cards[i - 1], 2000, self.cards[i]))
                section.save(f'output/{self.filename}/{i}.png')

    def parse(self):
        """Begin parsing the file"""

        for row in self.content:
            print(row)  # debug
            if row == '\n' or row[0] == '#':
                continue
            row_L, row_R = row.split("||", 1)
            if row_L == 'c':  # card
                card_colour, outline_colour, card_title, card_link = row_R.split("||", 3)
                card_colour = literal_eval(card_colour)
                outline_colour = literal_eval(outline_colour)
                self.write_card(card_title, card_colour, outline_colour, card_link)
            if row_L == 'h':  # heading
                self.write_header(row_R)
            elif row_L == 't':  # text
                self.write_text(row_R)
            elif row_L == 'b':  # break
                self.write_break(row_R)
            elif row_L == 'p':  # portrait
                frame, portrait_name, portrait_text = row_R.split("||", 2)
                self.write_portrait(frame, portrait_name, portrait_text,
                                    'shared')
            elif row_L == 'lp':  # local portrait
                frame, portrait_name, portrait_text = row_R.split("||", 2)
                self.write_portrait(frame, portrait_name, portrait_text,
                                    'local')
            elif row_L == 'pt':  # portrait text
                self.write_portrait_text(row_R)
            elif row_L == 'img':  # insert image
                align, filename = row_R.split("||", 1)
                filename = filename.rstrip()
                self.write_image(align, filename)
            elif row_L == 'subp':  # sub-portrait
                frame, portrait_name, x_offset, inc_y = row_R.split("||", 3)
                x_offset = int(x_offset)
                self.write_subportrait(frame, portrait_name, x_offset, inc_y)
            elif row_L == 'subpt':  # sub-portrait text
                x_offset, text = row_R.split("||", 1)
                x_offset = int(x_offset)
                self.write_subportrait_text(text, x_offset)
            elif row_L == "eq":
                stage_num, p1_frame, p1_portrait, p1_sub, p2_frame, p2_portrait, p2_sub, stage_name, desc = row_R.split(
                    "||", 8)
                self.write_eqstage(stage_num, p1_frame, p1_portrait,
                                   p1_sub, p2_frame, p2_portrait, p2_sub, stage_name, desc)
            elif row_L == "eqb":
                stage_num, p1_frame, p1_portrait, p1_sub, stage_name, desc = row_R.split(
                    "||", 5)
                self.write_basic_eqstage(
                    stage_num, p1_frame, p1_portrait, p1_sub, stage_name, desc)
            elif row_L == "colimg":
                self.write_columns(row_R)

    def write_card(self, title, colour, outline, link):
        """Generates a "band" based on the data given"""

        self.cards.append(self.y)

        # Background and resize
        response = requests.get(
                f"https://21000dollor.com/static/assets/banners/upscale_jpg/{link.rstrip()}.jpg")
        bg = Image.open(BytesIO(response.content)).convert('RGBA')
        self.img += 1
        basewidth = 2000
        wpercent = (basewidth / float(bg.size[0]))
        hsize = int((float(bg.size[1]) * float(wpercent)))
        bg = bg.resize((basewidth, hsize), Image.Resampling.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(4))

        h = 500

        # Generate the "band"
        band = Image.new('RGBA', (2000, h), colour)
        slate = Image.new('RGBA', (2000, h))
        slate.paste(band, (0, 0), band)

        # Paste the band on the background
        _, bg_h = bg.size
        _, band_h = slate.size
        h = int((bg_h / 2) - (band_h / 2))
        bg.paste(slate, (0, h), slate)

        # Write text onto the background
        self.multi_text(bg,
                        'MFF_Italics',
                        150, (1000, int(bg_h / 2) - 30),
                        title.upper(),
                        centre=True,
                        hcentre=True,
                        border=outline,
                        border_thickness=5)

        # Paste the background onto the slate
        self.slate.paste(bg, (0, self.y), bg)
        self.y += bg_h + 25

    def write_header(self, text):

        # Write text
        self.multi_text(self.slate,
                        'MFF_Italics',
                        75, (1000, self.y + 25),
                        text.upper(),
                        centre=True)

        # Increase y
        self.y += 150

    def write_text(self, text):

        # Formatting
        text = text.replace('â€™', "'")
        text = text.replace('[t]', '\t')
        if '[n]' in text:
            text = text.replace('[n]', '\n')
        else:
            # Justify
            max_line = 120
            final_string = ""
            current_line = ""
            for word in text.split(" "):
                if len(current_line) + len(word) < max_line:
                    current_line += word + ' '
                else:
                    final_string += current_line + "\n"
                    current_line = word + ' '
            final_string += current_line
            text = final_string

        # Write text
        _, h = self.multi_text(self.slate,
                               'Regular.otf',
                               35, (100, self.y),
                               text,
                               spacing=10)

        # Increase y
        self.y += h + 25

    def write_portrait(self, frame, portrait_name, text, src):

        # Get portrait image
        portrait = self._get_portrait(portrait_name)
        frame = self._portrait_to_frame(portrait, frame)

        # Paste portrait onto sheet
        self.slate.paste(frame, (100, self.y), frame)

        # Write text
        _, h = self.multi_text(self.slate, 'MFF_Italics', 50, (260, self.y),
                               text.upper())

        # Increase y
        self.y += h - 22

    def write_subportrait(self, frame, portrait_name, x_offset, inc_y):

        # Get portrait image
        # if src == 'shared':
        try:
            response = requests.get(
                f"https://21000dollor.com/static/assets/portraits_128/{portrait_name}.png")
            portrait = Image.open(BytesIO(response.content))
        except:
            response = requests.get(
                f"https://21000dollor.com/static/assets/items/{portrait_name}.png")
            portrait = Image.open(BytesIO(response.content)).convert(
                'RGBA').resize((128, 128))

        frame = self._portrait_to_frame(portrait, frame)
        frame = frame.resize((69, 69))

        # Paste portrait onto sheet
        self.slate.paste(frame, (260 + (75 * x_offset), self.y + 1), frame)

        # Increase y
        if inc_y == 'yes\n':
            self.y += 110

    def write_portrait_text(self, text):

        # Formatting
        text = text.replace('â€™', "'")
        text = text.replace('[t]', '\t')
        if '[n]' in text:
            text = text.replace('[n]', '\n')

        # Write text
        _, h = self.multi_text(self.slate, 'Regular.otf', 25, (260, self.y),
                               text)

        # Increase y
        if h > 100:
            self.y += h + 10
        else:
            self.y += 110

    def write_subportrait_text(self, text, x_offset):

        # Formatting
        text = text.replace('â€™', "'")
        text = text.replace('[t]', '\t')
        if '[n]' in text:
            text = text.replace('[n]', '\n')

        # Write text
        _, h = self.multi_text(self.slate, 'Regular.otf', 25,
                               (275 + (75 * x_offset), self.y), text)

        # Increase y
        if h > 100:
            self.y += h + 10
        else:
            self.y += 110

    def write_image(self, align, filename):

        # Open image
        image = Image.open(
            f"infographics/{self.filename}/{filename}.png").convert('RGBA')
        w, h = image.size

        # Paste depending on alignment
        l = 0
        if align == "centre" or align == "center":
            l = 1000 - int(w / 2)
        self.slate.paste(image, (l, self.y), image)

        # Increase y
        self.y += h + 20

    def write_eqstage(self, stage_num, p1_frame, p1_portrait, p1_sub, p2_frame, p2_portrait, p2_sub, stage_name, desc):

        # Write stage number
        # # The space allocated is 100 wide and 138 tall with topleft = (0, self.y)
        if 'i' in stage_num:  # Important
            self.multi_text(self.slate, 'MFF', 60, (50, self.y + (138 / 2)),
                            stage_num[:-1], centre=True, hcentre=True, colour=(247, 148, 29))
        else:
            self.multi_text(self.slate, 'MFF', 60, (50, self.y +
                                                    (138 / 2)), stage_num, centre=True, hcentre=True)

        # Get portrait images
        try:
            response = requests.get(
                f"https://21000dollor.com/static/assets/portraits_128/{p1_portrait}.png")
            portrait1 = Image.open(BytesIO(response.content))
        except:
            response = requests.get(
                f"https://21000dollor.com/static/assets/items/{p1_portrait}.png")
            portrait1 = Image.open(BytesIO(response.content)).convert(
                'RGBA').resize((128, 128))
        try:
            response = requests.get(
                f"https://21000dollor.com/static/assets/portraits_128/{p2_portrait}.png")
            portrait2 = Image.open(BytesIO(response.content))
        except:
            response = requests.get(
                f"https://21000dollor.com/static/assets/items/{p2_portrait}.png")
            portrait2 = Image.open(BytesIO(response.content)).convert(
                'RGBA').resize((128, 128))

        # Open and paste portraits into frames
        type_frame = {
            'white': 'frame1',
            'blast': 'frame3',
            'speed': 'frame2',
            'combat': 'frame6',
            'universal': 'frame4',
            'legendary': 'frame5',
            'twice': 'frametwice',
        }
        frame1 = Image.open(f'_resources/template/{type_frame[p1_frame]}.png'
                            ).convert('RGBA').resize((138, 138))
        frame2 = Image.open(f'_resources/template/{type_frame[p2_frame]}.png'
                            ).convert('RGBA').resize((138, 138))
        frame1.paste(portrait1, (5, 5), portrait1)
        frame2.paste(portrait2, (5, 5), portrait2)

        # Write subtitles onto frames
        frame1 = self._write_frame_subs(frame1, p1_sub)
        frame2 = self._write_frame_subs(frame2, p2_sub)

        # Paste frames onto sheet
        self.slate.paste(frame1, (100, self.y), frame1)
        self.slate.paste(frame2, (100 + 148, self.y), frame2)

        # Write stage name
        _, h = self.multi_text(self.slate, 'MFF', 40, (260 + 143, self.y),
                               stage_name)

        # Increase y
        self.y += h - 22 + 65

        # Write objective
        self.multi_text(self.slate, 'MFF', 40, (260 + 143,
                                                self.y), desc, colour=(171, 213, 255))

        # Increase y
        self.y += 85

    def write_basic_eqstage(self, stage_num, p1_frame, p1_portrait, p1_sub, stage_name, desc):

        # Write stage number
        # # The space allocated is 100 wide and 138 tall with topleft = (0, self.y)
        if 'i' in stage_num:  # Important
            self.multi_text(self.slate, 'MFF', 60, (50, self.y + (138 / 2)),
                            stage_num[:-1], centre=True, hcentre=True, colour=(247, 148, 29))
        else:
            self.multi_text(self.slate, 'MFF', 60, (50, self.y +
                                                    (138 / 2)), stage_num, centre=True, hcentre=True)

        # Get portrait images
        try:
            response = requests.get(
                f"https://21000dollor.com/static/assets/portraits_128/{p1_portrait}.png")
            portrait1 = Image.open(BytesIO(response.content))
        except:  # is item
            try:
                response = requests.get(
                    f"https://21000dollor.com/static/assets/items/{p1_portrait}.png")
                portrait1 = Image.open(BytesIO(response.content)).convert(
                    'RGBA').resize((128, 128))
            except:  # is local
                portrait1 = Image.open(
                    f'infographics/{self.filename}/{p1_portrait}.png').convert(
                        'RGBA').resize((128, 128))

        # Open and paste portraits into frames
        type_frame = {
            'white': 'frame1',
            'blast': 'frame3',
            'speed': 'frame2',
            'combat': 'frame6',
            'universal': 'frame4',
            'legendary': 'frame5',
            'twice': 'frametwice',
        }
        frame1 = Image.open(f'_resources/template/{type_frame[p1_frame]}.png'
                            ).convert('RGBA').resize((138, 138))
        frame1.paste(portrait1, (5, 5), portrait1)

        # Write subtitles onto frames
        frame1 = self._write_frame_subs(frame1, p1_sub)

        # Paste frames onto sheet
        self.slate.paste(frame1, (100, self.y), frame1)

        # Write stage name
        _, h = self.multi_text(self.slate, 'MFF', 40, (255, self.y),
                               stage_name)

        # Increase y
        self.y += h - 22 + 65

        # Write objective
        self.multi_text(self.slate, 'MFF', 40, (255, self.y),
                        desc, colour=(171, 213, 255))

        # Increase y
        self.y += 85

    def write_columns(self, colstring):
        """
        colstring is a string of (item, frame) tuples as strings,
            delimited by ||
        width is 2000px, with 100px margins
        """

        # Split colstring
        items = colstring.split("||")

        if len(items) < 10:
            # Find column size
            colsize = int(1800 / len(items))

            # First x position is middle of column - (138 / 2)
            first_x = 100 + int(colsize / 2) - (138 / 2)

            # Loop through and paste
            for i, item in enumerate(items):
                item = item.replace(')', '').replace('(', '').split(',')
                item[1] = item[1].rstrip() # in case of endline

                # Get portrait and frame
                portrait = self._get_portrait(item[0])
                frame = self._portrait_to_frame(portrait, item[1])

                # Paste frame on slate
                self.slate.paste(frame, (int(first_x + (i * colsize)), self.y), frame)

            self.y += 175
        else: # grid
            # Column size is 200px
            colsize = 200

            # First x position is middle of first column with 100px left margin
            first_x = 200 - (138 / 2)

            # Loop through and paste
            for i, item in enumerate(items):
                item = item.replace(')', '').replace('(', '').split(',')
                item[1] = item[1].rstrip() # in case of endline

                # Get portrait and frame
                portrait = self._get_portrait(item[0])
                frame = self._portrait_to_frame(portrait, item[1])

                # Paste frame on slate
                x = first_x + (colsize * (i % 9))
                y = self.y + (175 * (i // 9))
                self.slate.paste(frame, (int(x), int(y)), frame)

            self.y += 175 * ((i // 9) + 1)

    def _get_portrait(self, portrait_name):
        """
        portrait_name is a string that is either a character portrait, item name or local file name
        """

        try:
            response = requests.get(
                f"https://21000dollor.com/static/assets/portraits_128/{portrait_name}.png")
            return Image.open(BytesIO(response.content))
        except:  # is item
            try:
                response = requests.get(
                    f"https://21000dollor.com/static/assets/items/{portrait_name}.png")
                return Image.open(BytesIO(response.content)).convert('RGBA').resize((128, 128))
            except:  # is local
                return Image.open(
                    f'infographics/{self.filename}/{portrait_name}.png').convert(
                        'RGBA').resize((128, 128))

    def _portrait_to_frame(self, portrait_img, frame_name):
        """
        portrait_img is a PIL Image object
        frame_name is a string
        """

        # Map frame names to frames
        type_frame = {
            'white': 'frame1',
            'blast': 'frame3',
            'speed': 'frame2',
            'combat': 'frame6',
            'universal': 'frame4',
            'legendary': 'frame5',
            'twice': 'frametwice',
            'blue': 'frame3',
            'green': 'frame2',
            'red': 'frame6',
            'purple': 'frame4',
            'advanced': 'frame2',
            'rare': 'frame3',
            'heroic': 'frame4',
            'mythic': 'frame6'
        }

        frame = Image.open(f'_resources/template/{type_frame[frame_name]}.png'
                            ).convert('RGBA').resize((138, 138))
        frame.paste(portrait_img, (5, 5), portrait_img)

        return frame


    def _write_frame_subs(self, frame, sub):

        mapping = {
            '*': 'yellowstar',
            '+': 'redstar'
        }

        if ('*' in sub or '+' in sub) and len(sub) == 2:  # Stars
            num = int(sub[0])
            star = Image.open(
                f'_resources/items/{mapping[sub[1]]}.png').resize((21, 21))
            for i in range(num):
                frame.paste(star, (112 - (i * 21), 112), star)
        else:  # Simply write the text
            w, _ = self.multi_text(
                frame, 'MFF', 20, (999, 999), sub, border=(0, 0, 0), border_thickness=2)
            self.multi_text(frame, 'MFF', 20, (128 - w, 113),
                            sub, border=(0, 0, 0), border_thickness=2)

        return frame

    def write_break(self, px):

        # Increase y
        self.y += int(px)

    def multi_text(self,
                   bg,
                   font,
                   fontsize,
                   topleft,
                   text,
                   colour=(255, 255, 255),
                   centre=False,
                   hcentre=False,
                   align='left',
                   border=False,
                   border_thickness=3,
                   spacing=4):
        """Overlays multiline text on the slate"""

        draw = ImageDraw.Draw(bg)
        if '.' in font:
            font = ImageFont.truetype(f"_resources/font/{font}", fontsize)
        else:
            font = ImageFont.truetype(f"_resources/font/{font}.ttf", fontsize)
        _, _, w, h = draw.multiline_textbbox((0, 0), text, font=font, anchor="la")
        print(w, h)
        w, h = draw.multiline_textsize(text, font=font)
        print(w, h)
        if centre:
            topleft = (topleft[0] - (w / 2), topleft[1])
        if hcentre:
            topleft = (topleft[0], topleft[1] - (h / 2))

        if border:
            # thicker border
            x, y = topleft
            for i in range(1, border_thickness):
                draw.text((x - i, y - i), text, font=font, fill=border)
                draw.text((x + i, y - i), text, font=font, fill=border)
                draw.text((x - i, y + i), text, font=font, fill=border)
                draw.text((x + i, y + i), text, font=font, fill=border)

        draw.text(topleft,
                  text,
                  fill=colour,
                  font=font,
                  align=align,
                  spacing=spacing)

        return w, h

    def image_fill(self, rgb, x, y):
        """Generates an image of a single colour with a specified area."""

        img = Image.new('RGBA', (x, y), rgb)
        return img

    def transparent_gradient(self, img):
        """Generates a transparent gradient of an image."""

        img.save('temp/temp.png')
        img = Image.open("temp/temp.png").convert("RGBA")
        img.convert("RGBA")
        arr = np.array(img)
        alpha = arr[:, :, 3]
        n = len(alpha)
        alpha[:] = np.interp(np.arange(n), [0, 0.01 * n, 1 * n, n],
                             [255, 255, 0, 0])[:, np.newaxis]
        img = Image.fromarray(arr, mode='RGBA')

        return img


which = input("Which infographic?\n")
TextSheet(which)
