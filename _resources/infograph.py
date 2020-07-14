from PIL import Image, ImageDraw, ImageFont


def colours(query):

    data = {
        'grey': (200, 200, 200),
        'orange': (247, 148, 29),
        'lightblue': (171, 213, 255),
        'mountaindew': (186, 255, 0),
        'normal_grey': (219, 211, 236),
        'advanced_green': (76, 167, 125),
        'rare_blue': (97, 138, 229),
        'heroic_purple': (168, 94, 226),
        'legendary_yellow': (229, 154, 80),
        'mythic_red': (212, 80, 97),
    }

    return data[query]


def text(bg,
         font,
         fontsize,
         topleft,
         text,
         colour=(255, 255, 255),
         centre=False,
         border=False,
         border_thickness=3):
    """Overlays text on the slate"""

    draw = ImageDraw.Draw(bg)
    try:
        font = ImageFont.truetype(f"../../_resources/font/{font}.ttf",
                                  fontsize)
    except:
        font = ImageFont.truetype(f"../_resources/font/{font}.ttf", fontsize)
    w, h = draw.textsize(text, font=font)
    if centre:
        topleft = (topleft[0] - (w / 2), topleft[1])

    if border:
        # thicker border
        x, y = topleft
        for i in range(1, border_thickness):
            draw.text((x - i, y - i), text, font=font, fill=border)
            draw.text((x + i, y - i), text, font=font, fill=border)
            draw.text((x - i, y + i), text, font=font, fill=border)
            draw.text((x + i, y + i), text, font=font, fill=border)

    draw.text(topleft, text, colour, font=font)

    return w, h


def multi_text(bg,
               font,
               fontsize,
               topleft,
               text,
               colour=(255, 255, 255),
               centre=False,
               hcentre=False,
               align='left',
               border=False,
               border_thickness=3):
    """Overlays multiline text on the slate"""

    draw = ImageDraw.Draw(bg)
    if '.' in font:
        try:
            font = ImageFont.truetype(f"../../_resources/font/{font}",
                                      fontsize)
        except:
            font = ImageFont.truetype(f"../_resources/font/{font}", fontsize)
    else:
        try:
            font = ImageFont.truetype(f"../../_resources/font/{font}.ttf",
                                      fontsize)
        except:
            font = ImageFont.truetype(f"../_resources/font/{font}.ttf",
                                      fontsize)
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

    draw.text(topleft, text, fill=colour, font=font, align=align)

    return w, h


def outline_card(card, colour=(255, 0, 0)):
    """Outlines a card"""

    draw = ImageDraw.Draw(card)
    w, h = card.size
    for i in range(3):
        draw.rectangle([(0 + i, 0 + i), (w - 1 - i, h - 1 - i)],
                       outline=colour)
