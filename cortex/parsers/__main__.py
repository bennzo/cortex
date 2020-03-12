import click
from .parser import run_parser, setup_parser


@click.group()
def cli():
    pass


@cli.command(name='parse')
@click.argument('field', required=True)
@click.argument('data_path', required=True)
def _parse(field, data_path):
    with open(data_path, 'rb') as f:
        raw_data = f.read()
        return run_parser(field, raw_data)


@cli.command(name='run-parser')
@click.argument('field', required=True)
@click.argument('message_queue', required=True)
def _setup_parser(field, message_queue):
    parser = setup_parser(field, message_queue)
    parser.consume()


if __name__ == '__main__':
    cli(prog_name='cortex.parsers')
