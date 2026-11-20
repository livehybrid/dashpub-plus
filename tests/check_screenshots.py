#!/usr/bin/env python3
"""Check what one screenshotter run left behind.

    python tests/check_screenshots.py <directory>

The screenshotter catches its own errors and exits 0 whatever happens, so its
exit status says nothing. This looks at the files: one JPEG for the index and
one per dashboard the stub's index links to, each a real full-HD image.
"""
import struct
import sys
from pathlib import Path

EXPECTED = ["index.jpg", "dash_one.jpg", "dash_two.jpg"]
MIN_WIDTH, MIN_HEIGHT, MIN_BYTES = 1920, 1080, 3_000


def jpeg_size(data):
    """(width, height) from the first start-of-frame marker."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG")
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            raise ValueError("corrupt JPEG marker")
        marker = data[i + 1]
        length = struct.unpack(">H", data[i + 2 : i + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", data[i + 5 : i + 9])
            return width, height
        i += 2 + length
    raise ValueError("no frame header found")


def main(directory):
    folder = Path(directory)
    problems = []
    for name in EXPECTED:
        path = folder / name
        if not path.is_file():
            problems.append(f"{name}: missing")
            continue
        data = path.read_bytes()
        try:
            width, height = jpeg_size(data)
        except ValueError as err:
            problems.append(f"{name}: {err}")
            continue
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            problems.append(f"{name}: {width}x{height}, expected at least {MIN_WIDTH}x{MIN_HEIGHT}")
        if len(data) < MIN_BYTES:
            problems.append(f"{name}: only {len(data)} bytes, looks blank")
        print(f"{name}: {width}x{height}, {len(data)} bytes")

    extra = sorted(p.name for p in folder.iterdir() if p.name not in EXPECTED)
    if extra:
        problems.append(f"unexpected files (links outside the site must not be followed): {extra}")

    for problem in problems:
        print(f"FAIL {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
