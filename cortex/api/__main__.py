import click
from .api import run_api_server


@click.group()
def cli():
    pass


@cli.command(name='run-server')
@click.option('--host', '-h', default='127.0.0.1', show_default=True, help='API Server IP address')
@click.option('--port', '-p', default=5000, show_default=True, help='API Server port')
@click.option('--database', '-d', default='monogodb://127.0.0.1:27017', show_default=True, help='Database URL')
def _run_api_server(host, port, database):
    return run_api_server(host=host, port=port, database_url=database)


if __name__ == '__main__':
    cli(prog_name='cortex.api')
