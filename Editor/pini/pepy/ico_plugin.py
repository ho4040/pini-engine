#
# The Python Imaging Library.
# $Id$
#
# Windows Icon support for PIL
#
# History:
#       96-05-27 fl     Created
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#

# This plugin is a refactored version of Win32IconImagePlugin by Bryan Davis
# <casadebender@gmail.com>.
# https://code.google.com/p/casadebender/wiki/Win32IconImagePlugin
#
# Icon format references:
#   * http://en.wikipedia.org/wiki/ICO_(file_format)
#   * http://msdn.microsoft.com/en-us/library/ms997538.aspx


__version__ = "0.1"

from PIL import Image, ImageFile, BmpImagePlugin, PngImagePlugin, _binary
import bmpimageplugin
from bmpimageplugin import *
from cStringIO import StringIO
from math import log, ceil

i8 = _binary.i8
i16 = _binary.i16le
i32 = _binary.i32le
o8 = _binary.o8
o16 = _binary.o16le
o32 = _binary.o32le

_MAGIC = b"\0\0\1\0"


def _accept(prefix):
    return prefix[:4] == _MAGIC


class IcoFile:
    format = 'ICO'
    def __init__(self, buf):
        """
        Parse image from file-like object containing ico file data
        """

        # check magic
        s = buf.read(6)
        if not _accept(s):
            raise SyntaxError("not an ICO file")

        self.buf = buf
        self.entries = []

        # Number of items in file
        self.nb_items = i16(s[4:])

        # Get headers for each item
        for i in xrange(self.nb_items):
            s = buf.read(16)

            icon_header = {
                'width': i8(s[0]),
                'height': i8(s[1]),
                'nb_color': i8(s[2]),  # No. of colors in image (0 if >=8bpp)
                'reserved': i8(s[3]),
                'planes': i16(s[4:]),
                'bpp': i16(s[6:]),
                'size': i32(s[8:]),
                'offset': i32(s[12:])
            }

            # See Wikipedia
            for j in ('width', 'height'):
                if not icon_header[j]:
                    icon_header[j] = 256

            # See Wikipedia notes about color depth.
            # We need this just to differ images with equal sizes
            icon_header['color_depth'] = (icon_header['bpp'] or
                                          (icon_header['nb_color'] != 0 and
                                           ceil(log(icon_header['nb_color'],
                                                    2))) or 256)

            icon_header['dim'] = (icon_header['width'], icon_header['height'])
            icon_header['square'] = (icon_header['width'] *
                                     icon_header['height'])

            self.entries.append(icon_header)

        self.entries = sorted(self.entries, key=lambda x: x['color_depth'])
        # ICO images are usually squares
        # self.entries = sorted(self.entries, key=lambda x: x['width'])
        self.entries = sorted(self.entries, key=lambda x: x['square'])
        self.entries.reverse()

    def sizes(self):
        """
        Get a list of all available icon sizes and color depths.
        """
        return set((h['width'], h['height']) for h in self.entries)

    def getimage(self, size, bpp=False):
        """
        Get an image from the icon
        """
        for (i, h) in enumerate(self.entries):
            if size == h['dim'] and (bpp is False or bpp == h['color_depth']):
                return self.frame(i)
        return self.frame(0)

    def get_images(self):
        images = []
        for i, header in enumerate(self.entries):
            f = self.frame(i)
            if f.format:
                images.append(self.frame(i))
        return images

    def frame(self, idx):
        """
        Get an image from frame idx
        """

        header = self.entries[idx]

        self.buf.seek(header['offset'])
        data = self.buf.read(8)
        self.buf.seek(header['offset'])

        if data[:8] == PngImagePlugin._MAGIC:
            # png frame
            s = StringIO()
            s.write(self.buf.read(header['size']))
            s.seek(0)
            self.buf.seek(header['offset'])
            im = Image.open(s)
        else:
            # XOR + AND mask bmp frame
            s = StringIO()
            s.write(self.buf.read(header['size']))
            s.seek(0)
            self.buf.seek(header['offset'])
            im = bmpimageplugin.DibImageFile(s)
            #im = im.to_bitmapimage(header)
            #print im.tile
            # change tile dimension to only encompass XOR image
            im.size = (im.size[0], int(im.size[1] / 2))
            #print im.size
            d, e, o, a = im.tile[0]
            im.tile[0] = d, (0, 0) + im.size, o, a

            # figure out where AND mask image starts
            mode = a[0]
            bpp = 8
            for k in BmpImagePlugin.BIT2MODE.keys():
                if mode == BmpImagePlugin.BIT2MODE[k][1]:
                    bpp = k
                    break

            if 32 == bpp:
                # 32-bit color depth icon image allows semitransparent areas
                # PIL's DIB format ignores transparency bits, recover them.
                # The DIB is packed in BGRX byte order where X is the alpha
                # channel.

                # Back up to start of bmp data
                self.buf.seek(o)
                # extract every 4th byte (eg. 3,7,11,15,...)
                alpha_bytes = self.buf.read(im.size[0] * im.size[1] * 4)[3::4]

                # convert to an 8bpp grayscale image
                mask = Image.frombuffer(
                    'L',            # 8bpp
                    im.size,        # (w, h)
                    alpha_bytes,    # source chars
                    'raw',          # raw decoder
                    ('L', 0, -1)    # 8bpp inverted, unpadded, reversed
                )
            else:
                # get AND image from end of bitmap
                w = im.size[0]
                if (w % 32) > 0:
                    # bitmap row data is aligned to word boundaries
                    w += 32 - (im.size[0] % 32)

                # the total mask data is
                # padded row size * height / bits per char

                and_mask_offset = o + int(im.size[0] * im.size[1] *
                                          (bpp / 8.0))
                total_bytes = int((w * im.size[1]) / 8)

                self.buf.seek(and_mask_offset)
                maskData = self.buf.read(total_bytes)

                # convert raw data to image
                mask = Image.frombuffer(
                    '1',            # 1 bpp
                    im.size,        # (w, h)
                    maskData,       # source chars
                    'raw',          # raw decoder
                    ('1;I', int(w/8), -1)  # 1bpp inverted, padded, reversed
                )

                # now we have two images, im is XOR image and mask is AND image

            if im.mode != 'RGBA':
                im = im.convert('RGBA')
            im.putalpha(mask)

        return im


##
# Image plugin for Windows Icon files.

class IcoImageFile(ImageFile.ImageFile):
    """
    PIL read-only image support for Microsoft Windows .ico files.

    By default the largest resolution image in the file will be loaded. This
    can be changed by altering the 'size' attribute before calling 'load'.

    The info dictionary has a key 'sizes' that is a list of the sizes available
    in the icon file.

    Handles classic, XP and Vista icon formats.

    This plugin is a refactored version of Win32IconImagePlugin by Bryan Davis
    <casadebender@gmail.com>.
    https://code.google.com/p/casadebender/wiki/Win32IconImagePlugin
    """
    format = "ICO"
    format_description = "Windows Icon"

    def _open(self):
        self.ico = IcoFile(self.fp)
        self.info['sizes'] = self.ico.sizes()
        self.size = self.ico.entries[0]['dim']
        self.load()

    def load(self):
        im = self.ico.getimage(self.size)
        # if tile is PNG, it won't really be loaded yet
        im.load()
        self.im = im.im
        self.mode = im.mode
        self.size = im.size

    def get_images(self):
        return self.ico.get_images()

    def load_seek(self):
        # Flage the ImageFile.Parser so that it
        # just does all the decode at the end.
        pass

SAVE = {
    "1": ("1", 1, 2),
    "L": ("L", 8, 256),
    "P": ("P", 8, 256),
    "RGB": ("BGR", 24, 0),
    "RGBA": ("BGRA", 32, 0),
}

def get_data(im):
    s = StringIO()
    if im.format != 'DIB':
        im.save(s, im.format)
    else:
        s.write(im.buf)
    s.seek(0)

    if im.format == 'BMP':
        bmp_f = s
        bmp_f.seek(10)
        offset = i32(bmp_f.read(4))
        dib_size = i32(bmp_f.read(4))
        dib = o32(dib_size)+bytearray(bmp_f.read(36))
        dib[:4] = o32(40)
        dib[8:12] = o32(i32(str(dib[8:12]))*2)
        dib[16:20] = o32(0)
        dib = dib[:40]
        bmp_f.seek(offset)
        data = bytearray(bmp_f.read())
        data = dib+data
    else:
        data = bytearray(s.read())

    return data



def _save(image, fp, filename, check=0):
    data = None
    images = []
    if image.format != 'ICO':
        bmp_f = StringIO()
        image.save(bmp_f, format='BMP')
        bmp_f.seek(0)
        im2 = Image.open(bmp_f)
        if im2.format:
            images.append(im2)
    else:
        images = image.get_images()

    number_of_images = len(images)

    header_size = 6+16*number_of_images

    # ico header
    fp.write(o16(0) +                    # reserved
             o16(1) +                    # file type
             o16(number_of_images))      # number of images

    current_offset = header_size
    for i, im in enumerate(images):

        data = get_data(im)

        try:
            rawmode, bits, colors = SAVE[im.mode]
        except KeyError:
            raise IOError("cannot write mode %s as BMP" % im.mode)
        matte_data = bytearray()
        if im.format == 'BMP':

        #write matte data. Taken from imagemagick
            scanline_pad = (((im.size[0]+31) & ~31)-im.size[0]) >> 3
            row_len = im.size[0]*4
            for y in reversed(xrange(im.size[1])):
                d = data[40:]
                #BGRA
                row_pixels = d[row_len*y:row_len*y+row_len]
                bit=0
                byte=0
                for x in xrange(im.size[0]):
                    p=row_pixels[x]

                    byte<<=1
                    bit+=1
                    if bit == 8:
                        matte_data+=o8(byte)
                        bit=0
                        byte=0
                if not bit == 0:
                    matte_data+=o8(byte<<(8-bit))
                for i in xrange(scanline_pad):
                    matte_data+=o8(0)

        fp.write(o8(im.size[0]) +            # width
                 o8(im.size[1]) +            # height
                 o8(0) +                     # color palette
                 o8(0) +                     # reserved
                 o16(1) +                    # planes
                 o16(bits) +                 # depth
                 o32(len(data+matte_data)) +        # size of image in bytes
                 o32(current_offset)            # offset

            )
        current_offset += len(data+matte_data)

    for im in images:

        data = get_data(im)
        fp.write(data)

        if im.format == 'BMP':

        #write matte data. Taken from imagemagick
            scanline_pad = (((im.size[0]+31) & ~31)-im.size[0]) >> 3
            row_len = im.size[0]*4
            for y in reversed(xrange(im.size[1])):
                d = data[40:]
                #BGRA
                row_pixels = d[row_len*y:row_len*y+row_len]
                bit=0
                byte=0
                for x in xrange(im.size[0]):
                    p=row_pixels[x]

                    byte<<=1
                    bit+=1
                    if bit == 8:
                        fp.write(o8(byte))
                        bit=0
                        byte=0
                if not bit == 0:
                    fp.write(o8(byte<<(8-bit)))
                for i in xrange(scanline_pad):
                    fp.write(o8(0))


    fp.flush()


#
# --------------------------------------------------------------------

Image.register_open(IcoFile.format, IcoImageFile, _accept)
Image.register_save(IcoFile.format, _save)

Image.register_extension(IcoFile.format, '.ico')
