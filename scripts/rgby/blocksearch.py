import os
import argparse
import extract_maps
import csv
from collections import defaultdict

BLOCK_SIZE = 32

grass_block_types = [0x0b]
water_block_types = [0x1d, 0x1e, 0x65, 0x64, 0x1f, 0x43]

def get_maps(rom, map_headers):
    """Load the maps into a dict.

    The dict that is returned will store the map blocks, as well as the width
    and height of the map."""

    maps = defaultdict(dict)
    for map_id, map_header in map_headers.items():
        #Skip all maps that aren't outdoors.
        if map_header['tileset'] != hex(0):
            continue

        width = int(map_header['x'], 16)
        height = int(map_header['y'], 16)
        map_pointer = int(map_header['map_pointer'], 16)
        map_end = map_pointer + (width * height)
        
        maps[map_id]['blocks'] = rom[map_pointer:map_end]
        maps[map_id]['width'] = width
        maps[map_id]['height'] = height
    return maps

def read_map_blocks(map_blocks):
    """Look for grass and water in the map.

    Takes a bytearray of map blocks, and returns two lists: a list of all the
    blocks that have grass, and a list of those that have water."""

    grass_blocks = []
    water_blocks = []

    for pos, block in enumerate(map_blocks):
        if block in grass_block_types:
            grass_blocks.append(pos)
        elif block in water_block_types:
            water_blocks.append(pos)
    return grass_blocks, water_blocks

def get_square_px(blocks, width, height):
    """Get the actual pixel positions of the blocks.

    Takes the blocks, width, and height, and returns a list of dicts of the
    format [{x1: ..., y1: ..., x2: ..., y2: ...}, ...]."""

    squares = []
    for block_id, block in enumerate(blocks):
        x1 = (block_id % width) * BLOCK_SIZE
        y1 = (block_id % height) * BLOCK_SIZE
        x2 = x1 + BLOCK_SIZE
        y2 = y1 + BLOCK_SIZE
        squares.append({'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2})
    return squares


def get_squares(map_dict):
    """Get the pixel positions for a map."""

    width = map_dict['width']
    height = map_dict['height']
    grass_blocks = map_dict['grass_blocks']
    water_blocks = map_dict['water_blocks']

    grass_squares = get_square_px(grass_blocks, width, height)
    water_squares = get_square_px(water_blocks, width, height)
    
    return grass_squares, water_squares

def write_csv(map_name, squares):
    """Dump the squares to a CSV file."""

    fname = os.path.join('data', map_name + '.csv')

    with open(fname, 'w') as f:
        gen_id = 1
        route_id = 1 # This will have to be changed.
        
        fieldnames = ('gen_id', 'route_id', 'type_id', 'x1', 'y1', 'x2', 'y2')
        writer = csv.DictWriter(f, fieldnames)
        writer.writeheader()
        
        type_id = 1 # Grass
        for square in squares['grass']:
            writer.writerow({
                'gen_id': gen_id,
                'route_id': route_id,
                'type_id': type_id,
                'x1': square['x1'],
                'y1': square['y1'],
                'x2': square['x2'],
                'y2': square['y2']
            })
         
        type_id = 2 # Water
        for square in squares['water']:
             writer.writerow({
                'gen_id': gen_id,
                'route_id': route_id,
                'type_id': type_id,
                'x1': square['x1'],
                'y1': square['y1'],
                'x2': square['x2'],
                'y2': square['y2']
            })           
 
def main():
    parser = argparse.ArgumentParser(
                description='Read map data from Pokemon RGB.')
    parser.add_argument('rom_path', help='The game ROM to be read')
    args = parser.parse_args()

    rom_path = os.path.abspath(args.rom_path)
    print("Using rom path", rom_path)
    print("Loading rom...", extract_maps.load_rom(rom_path))
    extract_maps.load_map_pointers()
    map_headers = extract_maps.read_all_map_headers()
    
    rom = extract_maps.rom
    map_ids = extract_maps.maps
    maps = get_maps(rom, map_headers)

    squares = defaultdict(dict)

    for map_id, map_dict in maps.items():
        map_dict['name'] = map_ids[map_id].lower().replace(' ', '-')

        grass_blocks, water_blocks = read_map_blocks(map_dict['blocks'])
        map_dict['grass_blocks'] = grass_blocks
        map_dict['water_blocks'] = water_blocks
        grass_squares, water_squares = get_squares(map_dict)
        
        squares[map_id]['grass'] = grass_squares
        squares[map_id]['water'] = water_squares

        if grass_squares or water_squares:
            write_csv(map_dict['name'], squares[map_id])

    for map_id, map_dict in maps.items():
        print(map_dict['name'])

    return {}

if __name__ == '__main__':
    print(main())
