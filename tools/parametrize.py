__author__ = 'MegabytePhreak'

from argparse import ArgumentParser, FileType
from csv import DictReader
from kicad_parsers.symbols import load_lib
from copy import deepcopy
from os import path

def parametrize(args = None):

    parser = ArgumentParser(description='Parametrize Kicad Libraries from CSV files')

    parser.add_argument('library', type=FileType('r'),
                        help='Library to use as a basis for parametrization')
    parser.add_argument('csv', type=FileType('r'),
                        help='CSV file with rows for each parametrization of a symbol')
    parser.add_argument('output_name', type=str, default='.',
                        help='Name to give to output libraries')

    if args:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()

    symbol_lib = {x.get_field('Name'): x for x in load_lib(args.library)}
    symbols = []

    csv_data = DictReader(args.csv)
    for row in csv_data:
        symbol = deepcopy(symbol_lib[row['Symbol']])

        for key,value in row.items():
            if key == 'Symbol':
                continue
            if value == '':
                value = '~'
            symbol.set_or_add_field(key,value)

        symbols.append(symbol)

    with open("%s.lib" % args.output_name, 'w') as output:
        output.write('EESchema-LIBRARY Version 2.3\n')
        for symbol in symbols:
            output.write(symbol.serialize())
            output.write('\n')

    with open("%s.dcm" % args.output_name, 'w') as output:
        output.write('EESchema-DOCLIB Version 2.0\n')
        for symbol in symbols:
            if symbol.has_field('Description'):
                output.write('$CMP %s\n' % symbol.get_field('Name'))
                output.write('D %s\n' % symbol.get_field('Description'))
                output.write('$ENDCMP\n')

if __name__ == '__main__':
    parametrize()










