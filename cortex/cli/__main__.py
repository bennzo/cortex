import json
from pprint import pprint
import click
import requests
from ..utils import strip_str


@click.group()
def cli():
    pass


# TODO: add type to all optional cli inputs
@cli.command(name='get-users')
@click.option('--host', '-h', type=str, default='127.0.0.1', show_default=True, callback=strip_str,
              help='API Server IP address')
@click.option('--port', '-p', type=int, default=5000, show_default=True, help='API Server port')
def _get_users(host, port):
    result = requests.get(f'http://{host}:{port}/users').json()
    pprint(result)


@cli.command(name='get-user')
@click.option('--host', '-h', type=str, default='127.0.0.1', show_default=True, callback=strip_str,
              help='API Server IP address')
@click.option('--port', '-p',  type=int, default=5000, show_default=True, help='API Server port')
@click.argument('user_id', type=int, required=True)
def _get_user(host, port, user_id):
    result = requests.get(f'http://{host}:{port}/users/{user_id}').json()
    pprint(result)


@cli.command(name='get-snapshots')
@click.option('--host', '-h', type=str, default='127.0.0.1', show_default=True, callback=strip_str,
              help='API Server IP address')
@click.option('--port', '-p',  type=int, default=5000, show_default=True, help='API Server port')
@click.argument('user_id', type=int, required=True)
def _get_snapshots(host, port, user_id):
    result = requests.get(f'http://{host}:{port}/users/{user_id}/snapshots').json()
    pprint(result)


@cli.command(name='get-snapshot')
@click.option('--host', '-h', type=str, default='127.0.0.1', show_default=True, callback=strip_str,
              help='API Server IP address')
@click.option('--port', '-p',  type=int, default=5000, show_default=True, help='API Server port')
@click.argument('user_id', type=int, required=True)
@click.argument('ss_id', type=int, required=True)
def _get_snapshot(host, port, user_id, ss_id):
    result = requests.get(f'http://{host}:{port}/users/{user_id}/snapshots/{ss_id}').json()
    pprint(result)


@cli.command(name='get-result')
@click.option('--host', '-h', type=str, default='127.0.0.1', show_default=True, callback=strip_str,
              help='API Server IP address')
@click.option('--port', '-p',  type=int, default=5000, show_default=True, help='API Server port')
@click.option('--save', '-s', type=str, default='', show_default=True, callback=strip_str,
              help='Path to a file in which the result will be saved. Note: The file must exist')
@click.argument('user_id', type=int, required=True)
@click.argument('ss_id', type=int, required=True)
@click.argument('field', type=str, required=True, callback=strip_str)
def _get_result(host, port, save, user_id, ss_id, field):
    result = requests.get(f'http://{host}:{port}/users/{user_id}/snapshots/{ss_id}/{field}').json()
    pprint(result)
    if save:
        with open(save, 'w') as fd:
            json.dump(result, fd)
    return result


if __name__ == '__main__':
    cli(prog_name='cortex.cli')
