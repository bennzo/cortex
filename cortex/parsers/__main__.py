import sys
import click
from .parser import run_parser, setup_parser
from ..utils import strip_str


@click.group()
def cli():
    pass


@cli.command(name='parse')
@click.argument('field', type=str, required=True, callback=strip_str)
@click.argument('data_path', type=str, required=True, callback=strip_str)
def _parse(field, data_path):
    with open(data_path, 'rb') as f:
        raw_data = f.read()
    data_bytes = run_parser(field, raw_data)
    sys.stdout.buffer.write(data_bytes)


@cli.command(name='run-parser')
@click.argument('field', type=str, required=True, callback=strip_str)
@click.argument('message_queue', type=str, required=True, callback=strip_str)
def _setup_parser(field, message_queue):
    parser = setup_parser(field, message_queue)
    parser.consume()


if __name__ == '__main__':
    cli(prog_name='cortex.parsers')
