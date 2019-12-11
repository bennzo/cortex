import click
import brain
import functools


@click.group()
def cli():
    pass


@click.command()
@click.option('--address', help='Server address - <host>:<port>')
@click.option('--data_dir', help='Path of directory containing user thoughts')
@functools.wraps(brain.run_webserver)
def run_webserver(*args, **kwargs):
    return brain.run_webserver(*args, **kwargs)


@click.command()
@click.option('--address', help='Server address - <host>:<port>')
@click.option('--data', help='Path of directory containing user thoughts')
@functools.wraps(brain.run_server)
def run_server(*args, **kwargs):
    return brain.run_server(*args, **kwargs)


@click.command()
@click.option('--address', help='Server address - <host>:<port>')
@click.option('--user', help='User id')
@click.option('--thought', help='Thought string')
@functools.wraps(brain.upload_thought)
def upload_thought(*args, **kwargs):
    return brain.upload_thought(*args, **kwargs)


cli.add_command(run_webserver)
cli.add_command(run_server)
cli.add_command(upload_thought)

if __name__ == '__main__':
    cli(prog_name='brain')
