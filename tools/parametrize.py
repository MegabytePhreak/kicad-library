__author__ = 'MegabytePhreak'

from argparse import ArgumentParser, FileType
import csv
from kicad_parsers.symbols import load_lib
from copy import deepcopy
from os import path
import json
from pprint import pprint
from collections import OrderedDict


def merge_config(base, new):
    for key, value in base.items():
        if key in new:
            if hasattr(value, 'update'):
                value.update(new[key])
            else:
                for item in new[key]:
                    if item.startswith('-'):
                        while item[1:] in value:
                            value.remove(item[1:])
                    else:
                        value.append(item)


def load_config(f, table):
    config = {
        'ignore_fields': [],
        'translate_fields': {},
        'prepend_fields': {},
        'visible_fields': []
    }
    if f:
        json_config = json.load(f)
        merge_config(config, json_config)
        if 'tables' in json_config:
            if table in json_config['tables']:
                table_config = json_config['tables'][table]
                merge_config(config, table_config)

    return config


def parametrize(args=None):

    parser = ArgumentParser(
        description='Parametrize Kicad Libraries from CSV files')

    parser.add_argument(
        'library',
        type=FileType('r'),
        help='Library to use as a basis for parametrization')
    parser.add_argument(
        'csv',
        type=FileType('r'),
        help='CSV file with rows for each parametrization of a symbol')
    parser.add_argument(
        'output_name',
        type=str,
        default='.',
        help='Name to give to output libraries')
    parser.add_argument(
        '--strict',
        type=bool,
        default=False,
        help='Require all symbols to be present')
    parser.add_argument(
        '-C',
        '--config',
        type=FileType('r'),
        default=None,
        help='Configuration File')

    if args:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()

    config = load_config(args.config, path.basename(args.output_name))
    #pprint(config)

    symbol_lib = {x.get_field('Name'): x for x in load_lib(args.library)}
    symbols = []

    csv_data = csv.DictReader(args.csv)
    csv_data = list(csv_data)
    csv_data.sort(key=lambda x: x['PARTNUMBER'])

    for row in csv_data:
        symbol_name = row['SYMBOL']
        if not args.strict and not symbol_name in symbol_lib:
            print("Symbol '%s' not found for part '%s', skipping" %
                  (symbol_name, row["PARTNUMBER"]))
            continue

        symbol = deepcopy(symbol_lib[symbol_name])

        for key, value in row.items():
            if key in config['ignore_fields']:
                continue
            if key in config['translate_fields']:
                key = config['translate_fields'][key]

            if value == '' or value is None:
                value = '~'
            elif key in config['prepend_fields']:
                value = config['prepend_fields'][key] + value

            #print("Adding field '%s' = '%s'" % (key, value))
            symbol.set_or_add_field(key, value)

            if key in config['visible_fields']:
                symbol.set_visible(key, True)

        symbols.append(symbol)

    with open("%s.lib" % args.output_name, 'w') as output:
        output.write('EESchema-LIBRARY Version 2.4\n')
        for symbol in symbols:
            output.write(symbol.serialize())
            output.write('\n')

    with open("%s.dcm" % args.output_name, 'w') as output:
        output.write('EESchema-DOCLIB  Version 2.0\n')
        for symbol in symbols:
            if symbol.has_field('Description'):
                output.write('$CMP %s\n' % symbol.get_field('Name'))
                output.write('D %s\n' % symbol.get_field('Description'))
                output.write('$ENDCMP\n')


if __name__ == '__main__':
    parametrize()
