# This script will fetch the text table from 'text-table.txt' in the working
# directory and prompt for a string of hex values separated by spaces, such as
# 80 81 82, which will output ABC.

import os, argparse

def get_table(table_path):
    """Return the table as a dict."""
    table = {'4F': '='}
    with open(table_path) as f:
        for line in f.readlines():
            data = line.split('=')
            table[data[0]] = data[1].strip('\n')
    return table

def convert_to_text(hex_text, table):
    """Given space-separated hex values, return the text they represent."""
    data = hex_text.split()
    result = ""
    for character in data:
        result += table[character]
    return result

def convert_from_text(text, table):
    table = dict((v, k) for k, v in table.items())
    result = ""
    for character in text:
        result += table[character] + ' '
    return result

def main():
    parser = argparse.ArgumentParser(
                description='Convert text to or from hex values.'
            )
    parser.add_argument(
        '--hex',
        help='Convert from hex',
        action='store_true'
    )
    parser.add_argument(
        '--text',
        help='Convert to hex',
        action='store_true')
    args = parser.parse_args()
    
    table_path = os.path.abspath('text-table.txt')
    table = get_table(table_path)

    if args.hex:
        hex_text = input('Please enter space-separated hex values: ')
        print(convert_to_text(hex_text, table))
    elif args.text:
        text = input('Please enter the text: ')
        print(convert_from_text(text, table))

if __name__ == '__main__':
    main()
