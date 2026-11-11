"""Readable FindPic reference from dm 7.2450 guest fixtures.

This deliberately simple matcher is an offline reference, not a full-screen
real-time backend. Only 24-bit BI_RGB BMP and the measured API subset are accepted.
"""
import math
import re
import struct
from pathlib import Path
from qmacro_color import PixelImage, scan_points


class PictureContractError(ValueError):
    pass


def load_bmp(path):
    raw = Path(path).read_bytes()
    if len(raw) < 54 or raw[:2] != b'BM':
        raise PictureContractError('Expected an ordinary BMP; encrypted DMDM is unsupported')
    declared, offset = struct.unpack_from('<I4xI', raw, 2)
    header, width, signed_height, planes, depth, compression = struct.unpack_from('<IiiHHI', raw, 14)
    if header < 40 or planes != 1 or depth != 24 or compression != 0:
        raise PictureContractError('Only 24-bit BI_RGB is verified')
    if width <= 0 or signed_height == 0 or width * abs(signed_height) > 16_000_000:
        raise PictureContractError('Invalid or excessive dimensions')
    height = abs(signed_height)
    stride = (width * 3 + 3) & ~3
    if offset < 14 + header or offset + stride * height > len(raw) or declared > len(raw):
        raise PictureContractError('Truncated BMP')
    pixels = bytearray(width * height * 3)
    for y in range(height):
        row = y if signed_height < 0 else height - 1 - y
        src = raw[offset + row * stride:offset + row * stride + width * 3]
        start = y * width * 3
        pixels[start:start + width * 3:3] = src[2::3]
        pixels[start + 1:start + width * 3:3] = src[1::3]
        pixels[start + 2:start + width * 3:3] = src[::3]
    return PixelImage(width, height, pixels)


def _samples(template):
    w, h = template.width, template.height
    rgb = template.rgb
    key = rgb[:3]
    corners = [rgb[i:i+3] for i in (0, (w-1)*3, (h-1)*w*3, (w*h-1)*3)]
    # Uniform templates remain opaque. Corner-key transparency was measured
    # only when a different foreground color exists somewhere in the template.
    transparent = all(c == key for c in corners) and any(rgb[i:i+3] != key for i in range(0, len(rgb), 3))
    return [(i // 3 % w, i // 3 // w, tuple(rgb[i:i+3]))
            for i in range(0, len(rgb), 3) if not transparent or rgb[i:i+3] != key]


def find_pic(image, rect, templates, delta, similarity, direction=0, cancelled=None):
    if direction not in range(4):
        raise PictureContractError('Only FindPic directions 0..3 were measured')
    if not isinstance(delta, str) or not re.fullmatch('[0-9a-fA-F]{6}', delta):
        raise PictureContractError('Unsupported delta expression')
    if not isinstance(similarity, (int, float)) or not math.isfinite(similarity) or not .6 <= similarity <= 1:
        raise PictureContractError('Unverified similarity range')
    x1, y1, x2, y2 = rect
    ox, oy = image.origin
    if not ox <= x1 <= x2 <= ox + image.width or not oy <= y1 <= y2 <= oy + image.height:
        raise PictureContractError('Rectangle outside captured frame')
    if not templates:
        raise PictureContractError('No templates supplied')
    margin = int(255 * (1 - similarity))
    tolerance = tuple(int(delta[i:i+2], 16) + margin for i in (0, 2, 4))
    # Native FindPic scans every position for template 0 before template 1.
    for index, template in enumerate(templates):
        if template is None:
            continue  # Nonempty unavailable filename retains its list index.
        samples = _samples(template)
        endx, endy = x2 - template.width + 1, y2 - template.height + 1
        for x, y in scan_points(x1, y1, endx, endy, direction):
            if cancelled is not None and cancelled():
                raise InterruptedError('Picture search cancelled')
            if all(all(abs(a-b) <= t for a, b, t in zip(image.pixel(x+dx, y+dy), target, tolerance))
                   for dx, dy, target in samples):
                return index, x, y
    return -1, -1, -1


def find_pic_files(image, rect, files, resolve_template, delta, similarity, direction=0, cancelled=None):
    """Native filename-list normalization: omit empty tokens, keep missing slots.

    Only absent files are skipped. Invalid/unsupported image data and capture
    failures propagate instead of masquerading as a negative visual result.
    """
    if not isinstance(files,str):raise PictureContractError('String template list required')
    templates=[]
    for name in files.split('|'):
        if not name:continue
        try:templates.append(resolve_template(name))
        except FileNotFoundError:templates.append(None)
    if not templates:return -1,-1,-1
    return find_pic(image,rect,templates,delta,similarity,direction,cancelled)
