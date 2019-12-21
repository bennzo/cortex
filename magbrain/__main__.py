import click
import magbrain
import functools


@click.group()
def root():
    pass


@root.group()
def server():
    pass


@root.group()
def client():
    pass


@server.command()
@click.option('--address', help='Server address - <host>:<port>')
@click.option('--data_dir', help='Path of directory containing user thoughts')
@functools.wraps(magbrain.run_webserver)
def run_webserver(*args, **kwargs):
    return magbrain.run_webserver(*args, **kwargs)


@server.command()
@click.option('--host', help='Server IP address')
@click.option('--port', help='Server port')
@click.option('--data', help='Path to the data directory')
# @functools.wraps(magbrain.run_server)
def run(*args, **kwargs):
    return magbrain.run_server(*args, **kwargs)


@client.command()
@click.option('--host', help='Server IP address')
@click.option('--port', help='Server port')
@click.option('--sample', help='Path to the mind sample')
# @functools.wraps(magbrain.run_client)
def run(*args, **kwargs):
    return magbrain.run_client(*args, **kwargs)


if __name__ == '__main__':
    root(prog_name='magbrain')
