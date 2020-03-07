import click
from .parser import run_parser, setup_parser


@click.group()
def cli():
    pass


@cli.command(name='parse')
@click.argument('field', required=True)
@click.argument('data_path', required=True)
def _parse(field, data_path):
    return run_parser(field, data_path)


@cli.command(name='run-parser')
@click.argument('field', required=True)
@click.argument('message_queue', required=True)
def _setup_parser(field, message_queue):
    setup_parser(field, message_queue)


if __name__ == '__main__':
    cli(prog_name='cortex.parsers')
