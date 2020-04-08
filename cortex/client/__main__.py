import click
from .client import upload_sample
from ..utils import strip_str


@click.group()
def cli():
    pass


@cli.command(name='upload-sample')
@click.option('--host', '-h', type=str, default='127.0.0.1', show_default=True, callback=strip_str,
              help='Server IP address')
@click.option('--port', '-p', type=int, default=8000, show_default=True, help='Server port')
@click.option('--sample-format', '-f', type=str, default='protobuf',
              show_default=True, help='Format of the uploaded sample', callback=strip_str)
@click.argument('sample_path', type=str, required=True, callback=strip_str)
def _upload_sample(host, port, sample_format, sample_path):
    upload_sample(host, port, sample_path, sample_format=sample_format)


if __name__ == '__main__':
    cli(prog_name='cortex.client')
