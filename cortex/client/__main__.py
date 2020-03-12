import click
from .client import upload_sample


@click.group()
def cli():
    pass


@cli.command(name='upload-sample')
@click.option('--host', '-h', default='127.0.0.1', show_default=True, help='Server IP address')
@click.option('--port', '-p', default=8000, show_default=True, help='Server port')
@click.argument('sample_path', required=True)
def _upload_sample(host, port, sample_path):
    upload_sample(host, port, sample_path)


if __name__ == '__main__':
    cli(prog_name='cortex.client')
