import click
from .gui import run_server
from ..utils import strip_str


@click.group()
def cli():
    pass


@cli.command(name='run-server')
@click.option('--host', '-h', type=str, default='127.0.0.1', show_default=True, callback=strip_str,
              help='GUI Server IP address')
@click.option('--port', '-p', type=int, default=8080, show_default=True, help='GUI Server port')
@click.option('--api-host', '-H', type=str, default='127.0.0.1', show_default=True, callback=strip_str,
              help='API Server IP address')
@click.option('--api-port', '-P', type=int, default=5000, show_default=True, help='API Server port')
def _run_gui_server(host, port, api_host, api_port):
    return run_server(host=host, port=port, api_host=api_host, api_port=api_port)


if __name__ == '__main__':
    cli(prog_name='cortex.gui')
