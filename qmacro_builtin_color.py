"""Owned Runner builtin color contract, distinct from dm.FindColor.

Only supplied RGB frames are read. No original code, capture, input or COM runs.
Evidence: Runner 0x6312e0 and bounded CPU fixtures builtin-color-contract.json.
Unsupported syntax/ranges fail explicitly instead of manufacturing a miss.
"""
import math
import re
import struct


class BuiltinContractError(ValueError):
    pass


def scan_points(left, top, right, bottom, scan_type):
    """Inclusive rectangle. Type1 expands square shells about floor(size/2)."""
    if scan_type not in (0, 1):
        raise BuiltinContractError('Only native scan types 0/1 have evidence')
    if left > right or top > bottom:
        raise BuiltinContractError('Reversed rectangle normalization not replayed')
    if scan_type == 0:
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                yield x, y
        return
    cx = left + (right - left + 1) // 2
    cy = top + (bottom - top + 1) // 2
    yield cx, cy
    radius = max(cx-left, right-cx, cy-top, bottom-cy)
    for r in range(1, radius+1):
        # Original order interleaves top/bottom, then left/right interior.
        for x in range(max(left, cx-r), min(right, cx+r)+1):
            if top <= cy-r <= bottom:
                yield x, cy-r
            if top <= cy+r <= bottom:
                yield x, cy+r
        for y in range(max(top, cy-r+1), min(bottom, cy+r-1)+1):
            if left <= cx-r <= right:
                yield cx-r, y
            if left <= cx+r <= right:
                yield cx+r, y


def color_contract(bgr, similarity):
    if not isinstance(bgr, str) or not re.fullmatch('[0-9a-fA-F]{6}', bgr):
        raise BuiltinContractError('Only six-digit BGR strings verified')
    if isinstance(similarity, bool) or not isinstance(similarity, (int, float)) or not math.isfinite(similarity) or not .1 <= similarity <= 1:
        raise BuiltinContractError('Unverified similarity range')
    sim32 = struct.unpack('<f', struct.pack('<f', similarity))[0]
    target = tuple(int(bgr[i:i+2], 16) for i in (4, 2, 0))
    return target, math.trunc((1-sim32)*100), sim32 > .99


def unpack_coordinates(packed):
    """VBScript CInt(Double / 8192) and signed Mod, including its rounding."""
    if type(packed) is not int or not -2147483648 <= packed <= 2147483647:
        raise BuiltinContractError('Expected signed 32-bit packed coordinates')
    x = round(packed/8192)
    if not -32768 <= x <= 32767:
        raise BuiltinContractError('Original CInt coordinate overflows')
    y = packed - math.trunc(packed/8192)*8192
    return x, y


def find_color(frame, left, top, right, bottom, bgr, scan_type=0, similarity=1):
    """Return original packed integer; supplied frame implements pixel(x,y)."""
    if any(type(v) is not int for v in (left, top, right, bottom, scan_type)):
        raise BuiltinContractError('Only integer rectangles and scan types verified')
    ox, oy = frame.origin
    if not ox <= left <= right < ox+frame.width or not oy <= top <= bottom < oy+frame.height:
        raise BuiltinContractError('Inclusive rectangle outside supplied capture')
    target, threshold, exact = color_contract(bgr, similarity)
    for x, y in scan_points(left, top, right, bottom, scan_type):
        rgb = frame.pixel(x, y)
        if len(rgb) != 3 or any(type(c) is not int or not 0 <= c <= 255 for c in rgb):
            raise BuiltinContractError('Invalid RGB sample')
        if (tuple(rgb) == target if exact else sum(abs(a-b) for a,b in zip(rgb,target)) < threshold):
            packed = x*8192+y
            if not -2147483648 <= packed <= 2147483647:
                raise BuiltinContractError('Packed coordinate overflow')
            return packed
    return -8193


def find_color_ex(frame, left, top, right, bottom, bgr, scan_type=0, similarity=1):
    packed = find_color(frame,left,top,right,bottom,bgr,scan_type,similarity)
    return packed, *unpack_coordinates(packed)
