#!/usr/bin/env python3
"""Generate Android launcher icons at various DPIs."""
import struct, zlib, math, os, sys

def create_png(size, filename, bg=(13, 13, 13), fg=(230, 57, 70)):
    pixels = []
    cx, cy = size // 2, size // 2
    r = size * 0.35
    for y in range(size):
        row = bytearray()
        for x in range(size):
            dx, dy = x - cx, y - cy
            bar = abs(y - cy) < r*0.1 and abs(x - cx) < r*1.1
            plate_l = abs(x - (cx - r*0.7)) < r*0.22 and abs(y - cy) < r*0.55
            plate_r = abs(x - (cx + r*0.7)) < r*0.22 and abs(y - cy) < r*0.55
            if bar or plate_l or plate_r:
                row.extend([fg[0], fg[1], fg[2], 255])
            else:
                row.extend([*bg, 255])
        pixels.append(bytes(row))

    def chunk(chunk_type, data):
        c = chunk_type + data
        flip = struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return flip

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
    idat_data = b''
    for row in pixels:
        idat_data += b'\x00' + row
    idat = chunk(b'IDAT', zlib.compress(idat_data))
    iend = chunk(b'IEND', b'')
    with open(filename, 'wb') as f:
        f.write(sig + ihdr + idat + iend)

if __name__ == '__main__':
    base = sys.argv[1] if len(sys.argv) > 1 else '/opt/data/projects/gym-recomendador/android'
    sizes = {
        'mipmap-mdpi': 48,
        'mipmap-hdpi': 72,
        'mipmap-xhdpi': 96,
        'mipmap-xxhdpi': 144,
    }
    for folder, size in sizes.items():
        path = os.path.join(base, 'app', 'src', 'main', 'res', folder)
        os.makedirs(path, exist_ok=True)
        create_png(size, os.path.join(path, 'ic_launcher.png'))
        print(f'  ✓ {folder}/ic_launcher.png ({size}x{size})')
