import click
from .server import run_server


@click.group()
def cli():
    pass


@cli.command(name='run-server')
@click.option('--host', '-h', default='127.0.0.1', show_default=True, help='Server IP address')
@click.option('--port', '-p', default=8000, show_default=True, help='Server port')
@click.argument('message_queue', required=True)
def _cli_run_server(host, port, message_queue):
    run_server(host, port, message_queue)


if __name__ == '__main__':
    cli(prog_name='cortex.server')
