import click
from .server import _cli_run_server
from ..utils import strip_str


@click.group()
def cli():
    pass


@cli.command(name='run-server')
@click.option('--host', '-h', type=str, default='127.0.0.1', show_default=True, callback=strip_str,
              help='Server IP address')
@click.option('--port', '-p', type=str, default=8000, show_default=True, help='Server port')
@click.argument('message_queue', type=str, required=True, callback=strip_str)
def _run_server(host, port, message_queue):
    _cli_run_server(host=host, port=port, message_queue=message_queue)


if __name__ == '__main__':
    cli(prog_name='cortex.server')
