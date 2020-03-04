import click
from .client import upload_sample


@click.group()
def cli():
    pass


@cli.command(name='upload-sample')
@click.option('--host', '-h', default='127.0.0.1', show_default=True, help='Server IP address')
@click.option('--port', '-p', default=8000, show_default=True, help='Server port')
@click.option('--sample-format', default='protobuf', show_default=True, help='Format of the mind sample')
@click.argument('sample_path', required=True)
def _cli_upload_sample(host, port, sample_path, sample_format):
    print(host, port, sample_path, sample_format)
    upload_sample(host, port, sample_path, sample_format)


if __name__ == '__main__':
    cli(prog_name='cortex.client')
