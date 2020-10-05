from PIL import Image, ImageFont, ImageDraw, ImageFilter
import numpy as np
from ast import literal_eval
import sys
import os


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
            if row == '\n':
                continue
            row_L, row_R = row.split("||", 1)
            if row_L == 'c':  # card
                card_colour, outline_colour, card_title = row_R.split("||", 2)
                card_colour = literal_eval(card_colour)
                outline_colour = literal_eval(outline_colour)
                self.write_card(card_title, card_colour, outline_colour)
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

    def write_card(self, title, colour, outline):
        """Generates a "band" based on the data given"""

        self.cards.append(self.y)

        # Background and resize
        bg = Image.open(
            f"infographics/{self.filename}/titlecards/{self.img}.png").convert(
                'RGBA')
        self.img += 1
        basewidth = 2000
        wpercent = (basewidth / float(bg.size[0]))
        hsize = int((float(bg.size[1]) * float(wpercent)))
        bg = bg.resize((basewidth, hsize), Image.ANTIALIAS)
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
                        150, (1000, int(bg_h / 2) + 50),
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
        if src == 'shared':
            portrait = Image.open(f'_resources/images/{portrait_name}.png'
                                  ).convert('RGBA').resize((128, 128))
        elif src == 'local':
            portrait = Image.open(
                f'infographics/{self.filename}/{portrait_name}.png').convert(
                    'RGBA').resize((128, 128))
        type_frame = {
            'white': 'frame1',
            'blast': 'frame3',
            'speed': 'frame2',
            'combat': 'frame6',
            'universal': 'frame4',
            'legendary': 'frame5',
            'twice': 'frametwice',
        }
        frame = Image.open(f'_resources/template/{type_frame[frame]}.png'
                           ).convert('RGBA').resize((138, 138))
        frame.paste(portrait, (5, 5), portrait)

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
        portrait = Image.open(
            f'_resources/images/{portrait_name}.png').convert('RGBA').resize(
                (128, 128))
        # # elif src == 'local':
        #     portrait = Image.open(f'infographics/{self.filename}/{portrait_name}.png'
        #                           ).convert('RGBA').resize((128, 128))
        type_frame = {
            'white': 'frame1',
            'blast': 'frame3',
            'speed': 'frame2',
            'combat': 'frame6',
            'universal': 'frame4',
            'legendary': 'frame5',
            'twice': 'frametwice',
        }
        frame = Image.open(f'_resources/template/{type_frame[frame]}.png'
                           ).convert('RGBA').resize((138, 138))
        frame.paste(portrait, (5, 5), portrait)
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
        w, h = draw.multiline_textsize(text, font=font)
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


which = input("Which infographic?")
TextSheet(which)
