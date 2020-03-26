import click
from .gui import run_server


@click.group()
def cli():
    pass


@cli.command(name='run-server')
@click.option('--host', '-h', default='127.0.0.1', type=str, show_default=True, help='GUI Server IP address')
@click.option('--port', '-p', default=8080, type=int, show_default=True, help='GUI Server port')
@click.option('--api-host', '-H', default='127.0.0.1', type=str, show_default=True, help='API Server IP address')
@click.option('--api-port', '-P', default=5000, type=int, show_default=True, help='API Server port')
def _run_gui_server(host, port, api_host, api_port):
    return run_server(host=host, port=port, api_host=api_host, api_port=api_port)


if __name__ == '__main__':
    cli(prog_name='cortex.gui')
