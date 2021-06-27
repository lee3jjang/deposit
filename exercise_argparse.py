import argparse
import logging
logging.basicConfig(level='INFO', format=None)

parser = argparse.ArgumentParser(
    prog='MyProgram',
    description='Process some integers.',
    epilog='And that\'s how you\'d foo a bar.',
)
parser.add_argument('-s', '--src', nargs='?', help='src help', required=False, default=argparse.SUPPRESS)
parser.add_argument('-t', '--time', nargs='?', help='time help', required=False, default=argparse.SUPPRESS)
# parser.add_argument('bar', nargs='+', type=int, help='bar help')
# parser.add_argument('bar', nargs='?', type=int, help='bar help')
# parser.add_argument('integers', metavar='N', type=int, nargs='+')
args = parser.parse_args()
logging.info(args)
