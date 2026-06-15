#!/usr/bin/env python3
"""Generate a simple PNG icon for the Gym Recomendador PWA."""
import struct, zlib, math

def create_png(size, filename, bg=(13, 13, 13), fg=(230, 57, 70)):
    """Create a minimal PNG with a dumbbell-like icon."""
    # Generate RGBA pixel data (row by row, top to bottom)
    pixels = []
    cx, cy = size // 2, size // 2
    r = size * 0.35
    for y in range(size):
        row = bytearray()
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            # Draw a simple dumbbell shape
            in_circle = dist < r * 0.85
            # Two weight plates on left and right
            plate_l = abs(x - (cx - r*0.7)) < r*0.2 and abs(y - cy) < r*0.5
            plate_r = abs(x - (cx + r*0.7)) < r*0.2 and abs(y - cy) < r*0.5
            # Handle bar
            bar = abs(y - cy) < r*0.1 and abs(x - cx) < r*1.1
            # Center circle (gym plate)
            center = in_circle and abs(angle) > math.pi/4 and abs(angle) < 3*math.pi/4

            if plate_l or plate_r or bar:
                row.extend([fg[0], fg[1], fg[2], 255])
            elif center:
                row.extend([fg[0], fg[1], fg[2], 255])
            else:
                row.extend([*bg, 255])
        pixels.append(bytes(row))

    # Build PNG
    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))  # 8-bit RGBA
    idat_data = b''
    for row in pixels:
        idat_data += b'\x00' + row  # filter byte (none) + row data
    idat = chunk(b'IDAT', zlib.compress(idat_data))
    iend = chunk(b'IEND', b'')

    with open(filename, 'wb') as f:
        f.write(sig + ihdr + idat + iend)
    print(f'Created {filename} ({size}x{size})')

import os
outdir = os.path.join(os.path.dirname(__file__), '..', 'pwa', 'icons')
os.makedirs(outdir, exist_ok=True)
create_png(192, os.path.join(outdir, 'icon-192.png'))
create_png(512, os.path.join(outdir, 'icon-512.png'))
