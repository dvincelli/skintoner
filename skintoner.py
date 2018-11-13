# requirements: Pillow 4.2.1
from PIL import Image
from PIL.ImagePalette import ImagePalette
import sys
import argparse
import logging

logging.basicConfig(level=logging.CRITICAL)


skin_tone_2 = (0xfa, 0xdc, 0xbc)
skin_tone_3 = (0xe0, 0xbb, 0x95)
skin_tone_4 = (0xbf, 0x8f, 0x68)
skin_tone_5 = (0x9b, 0x64, 0x3d)
skin_tone_6 = (0x59, 0x45, 0x39)

HEIGHT = 16
WIDTH = 16


# thanks stackoverflow.
def quantizetopalette(silf, palette, dither=False):
    """Convert an RGB or L mode image to use a given P image's palette."""

    silf.load()

    # use palette from reference image
    palette.load()
    if palette.mode != "P":
        raise ValueError("bad mode for palette image")
    if silf.mode != "RGB" and silf.mode != "L":
        raise ValueError(
            "only RGB or L mode images can be quantized to a palette"
            )
    im = silf.im.convert("P", 1 if dither else 0, palette.im)
    # the 0 above means turn OFF dithering

    # Later versions of Pillow (4.x) rename _makeself to _new
    try:
        return silf._new(im)
    except AttributeError:
        return silf._makeself(im)


def to_slack_tone(pixel):
    return ':skin-tone-{}:'.format(pixel + 2)


def to_gitlab_tone(pixel):
    return ':tone{}:'.format(pixel+1)


def main(dialect, image):
    palette = skin_tone_2 + skin_tone_3 + skin_tone_4 + skin_tone_5 + skin_tone_6 + skin_tone_6 + skin_tone_6 + skin_tone_6
    palimage = Image.new('P', (HEIGHT, WIDTH))
    palimage.putpalette(palette * 32)

    img = Image.open(image)
    img = img.resize((HEIGHT, WIDTH))
    img = quantizetopalette(img, palimage, dither=False)

    if dialect == 'slack':
        mapper = to_slack_tone
    else:
        mapper = to_gitlab_tone

    lines = []
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            pixel = img.getpixel((x, y))
            markup = mapper(pixel)
            lines.append(markup)
        print(' '.join(lines) + '  ')
        lines = []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Transform image into slack or gitlab pixel art')
    parser.add_argument(
        '--dialect', metavar='dialect', type=str, choices=('gitlab', 'slack'),
        default='slack', help='Produce gitlab or slack mark-up')
    parser.add_argument(
        'image', metavar='image', type=str,
        help='Produce gitlab or slack mark-up')

    args = parser.parse_args()

    main(args.dialect, args.image)
