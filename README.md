# mff-sheets
Marvel Future Fight infographic generator

## basics

`text_sheets.py` is a simple script to generate aesthetic infographic-style guides for text-heavy content. Examples of infographics made using this tool include:

* [Galactic Imperative Epic Quest Guide](http://21000dollor.com/eq/gotg.png)
* [6.1 Update Recap](http://21000dollor.com/recap/6.1.png)

Each infographic you generate will have its own project folder within the subdirectory `infographics`. Each of these folders should contain the following:

* A text document called `script.txt` that will be parsed to generate the infographic.
* An image called `title.png`. This image should be 2000px wide but can be as tall as you want. 
    * If you wish to add text or your infographic's title to this image, you will have to do it in a separate image editing program. This program will simply paste that title image up the top.
* A folder named `titlecards`.
    * Inside this folder, place the section title background images. Name them as `1.png`, `2.png`, etc. in order of appearance in the infographic from top to bottom.
    * These images should be automatically resized to fit. It is recommended that "new contents" promo images used in the in-game scrolling ad are used as titlecards.
* Any other images you want, in `.png` format, named however you like.
    * A lot of common images, such as character portraits, are stored in `_resources/portraits` and `_resources/items`. However images that you generate yourself or ones not found in the `_resources` folder need to be placed within the infographic's project folder.

Examples of these folders used to generate various infographics can be found in the `infographics` folder.

## script

It is useful to think of each newline in the `script.txt` document as a function call with a double pipe (`||`) separating each argument. It is important to properly separate arguments with double pipes and provide the correct number of arguments in the correct format for each line. The error messages will not be very useful.

Blank lines are ignored, so you can use those to format your script file somewhat.

Each line will start with a short prefix for the type of function that line will be calling, then a double pipe, then whatever arguments you need to provide (also double pipe-separated).

### c: card

Writes a title card. Remember that the cards were simply named `1`, `2`, etc. so you will not need to include which image you are wanting to use as a card. If this is the first card line in the script file, it will take image `1`, and so on.

`c||[bg_colour]||[text_outline_colour]||[card_title]`

* `bg_colour`: There will be a "band" of a single colour pasted over the centre of the card to be used as the text background. Pass in an RGB(A) tuple here, it is recommended to use a colour that features prominently in the card image. It is also recommended to pass a 4th tuple value of 200 (or similar) to provide a translucent effect.
* `text_outline_colour`: The card text will be outlined in this colour. Pass in an RGB tuple here, it is recommended to use an accent colour in the card image.
* `card_title`: The actual text to print in the card. The fill colour is white. Keep it relatively short so it fits.

Example: `c||(55,97,212,200)||(233,0,0)||Characters`

### h: heading

Writes a centred heading. This is done in the italicised MFF in-game font and is always transformed into uppercase.

`h||[heading_text]`

* `heading_text`: The text to use in the heading.

Example: `h||New Awakened Skills`

### t: text

Writes basic paragraph text. The text is automatically adjusted and line breaks added to fit, but if you want to add a no-spacing line break, you can insert `[n]` inline. If you want spacing with a line break, just write another text line.

`t||[text]`

* `text`: The text to print.

Example: `t||Listed below are the new characters in this update.`

### b: break

Insert blank space. Most functions here should automatically create space after them, but if you need more or they aren't working properly you can use this.

`b||[pixels]`

* `pixels`: The amount of vertical pixels to leave blank, as an integer.

Example: `b||100`

### img: image

Insert an image stored in your infographic project folder.

`img||[alignment]||[filename]`

* `alignment`: You can either pass in the strings `center` or `centre` and the image will be aligned to the center. Otherwise, you can pass in an integer to determine the amount of pixels from the left edge of the infographic you want the image to be pasted. For reference, the `text` function writes text at 100px from the left.
* `filename`: The filename of the image you want to insert. Note that this image has to be stored in the infographic project folder and you will have to copy images from `_resources` out if you want to use them in this way. Only the file name is needed, not `.png`. 

Example: `img||centre||stagelist`

### p: portrait

Inserts an image, usually a character portrait, within a coloured outline or "frame".

`p||[frame_type]||[portrait_name]||[text]`

* `frame_type`: The colour of the frame. Takes in the following:
    * `white`: Plain white frame. Used to represent "Common", or "1*".
    * `speed`: Green frame. Used to represent "Advanced", "Speed Type", or "2*".
    * `blast`: Blue frame. Used to represent "Rare", "Blast Type", or "3*".
    * `universal`: Purple frame. Used to represent "Heroic", "Universal Type", or "4*".
    * `legendary`: Yellow-orange frame. Used to represent "Legendary" or "5*".
    * `combat`: Red frame. Used to represent "Mythic", "Combat Type", or "6*".
    * `twice`: Very pleasant apricot and neon magenta gradient frame. Used to represent things that do not fall into the above categories (e.g. have no associated rarity).
* `portrait_name`: The name of the portrait to put inside the frame. This should be the filename of some image stored in `_resources/portraits` or `_resources/items`.
* `text`: The heading text to go alongside the portrait. This is in the italicised MFF in-game font and is forced uppercase.

Example: `p||combat||gladiator||Gladiator`

### lp: local portrait

The same as `p`, but for files not found in `_resources/portraits` or `_resources/items`.

`lp||[frame_type]||[portrait_name]||[text]`

* `frame_type`: Same as above.
* `portrait_name`: The name of the portrait to be put inside the frame. This should be the filename of some image stored in your infographic-specific project folder.
* `text`: Same as above.

Example: `lp||white||deluxemission||Deluxe Pack: 5100 Crystals`

### pt: portrait text

Inserts regular text below a portrait's heading. Used to explain details of that portrait. Since `pt` handles the spacing after a portrait, *you need to include a `pt` after every `p` and `lp` in the script*. If the portrait does not require any extra text, just call a blank `pt` (i.e. `pt||`).

`pt||[portrait_text]`

* `portrait_text`: Text to put under a portrait heading. This does not automatically add line breaks, you need to do those yourself inline using `[n]`. 1-3 lines is optimal for aesthetic purposes, 4 lines is okay too. 

Example: `pt||An all-around super solid character, with great PvE viability and some potential usage in PvP. The worst thing about him is that he's Combat for no reason.[n]High damage with a huge healing factor, decent def down, accumulation and almost permanent uptime on piercing everything.`

### subp: sub-portrait

Places a smaller portrait under a portrait in `p`. Should always come after either a `p` or another `subp`, since sub-portraits can be laid out in sequence (e.g. to represent item drops from a mission type, or the characters needed to unlock Jean Grey).

`subp||[frame_type]||[portrait_name]||[prior_subps]||[increment_y?]`

* `frame_type`: Same as `p`.
* `portrait_name`: Same as `p`.
* `prior_subps`: The amount of contiguous `subp` lines that precede the current one. Starts at 0.
* `increment_y?`:
    * Enter `yes` if this is the final `subp` to go under the portrait, and you do not intend on adding text.
    * Enter `no` if you want to add more sub-portraits after this one, or text.

Example: `subp||universal||betaraybill||0||no`

### subpt: sub-portrait text

Like `pt`, but left-padded to account for subportraits having been added. Prints text to the right of the right-most sub-portrait.

`subpt||[prior_subps]||[portrait_text]`

* `prior_subps`: The amount of contiguous `subp` lines that precede the current one. Should be 1 greater than the number in the `subp` of the previous line.
* `portrait_text`: Same as `pt`.

#### multi-line example

Using a portrait, multiple sub-portraits, and sub-portrait text:

```
lp||white||brbawaken||Beta Ray Bill [Might of Uru]
subp||universal||betaraybill||0||no
subp||blast||starlord||1||no
subp||universal||thor||2||no
subp||universal||odin||3||no
subpt||4||Probably the second best Awakening Skill behind Mystique, but costs 1.5x the materials and requires Odin.[n]Makes Bill insane in PvE so probably worth the grind, especially if Odin's rework is a banger.
```

* The local portrait image shows Beta Ray Bill's Awakened Skill icon.
* The local portrait heading text shows the skill name.
* The sub-portraits show Bill's character portrait, along with the 3 characters necessary to Awaken.
* The sub-portrait text provides a short description of the skill. `[n]` is used to declare a line break.

### eq: epic quest stage portraits

A special function for generating an Epic Quest stage list. Probably not too useful outside this use case.

`eq||[stage]||[p1_frame]||[p1_portrait]||[p1_subtitle]||[p2_frame]||[p2_portrait]||[p2_subtitle]||[stage_name]||[description]`

* `stage`: Stage number, to be put on the left hand side in big text. Enter `i` after the stage number to mark it as "important" with an orange colour.
* `p1` refers to the regular reward, `p2` the deluxe reward.
  * `p[x]_frame`: Same as other commands, frame for the portrait.
  * `p[x]_portrait`: Same as other commands, portrait to use.
  * `p[x]_subtitle`: The trait associated with that reward portrait. For example, 6 stars, Lv.20 or 20 (quantity of reward).
* `stage_name`: The name of the stage.
* `description`: What needs to be done to complete the stage.

## generating infographic

Once your script and folder is set up, simply call `text_sheets.py` and enter the name of the infographic project folder. The output will be saved into the `output` subdirectory and named whatever the project folder is called. You also have the option to split the larger image into pieces, with each "card" being the start of a new image, by responding `yes` to the prompt that appears.
