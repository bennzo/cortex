import click
from .saver import _cli_save, _cli_run_saver
from ..utils import strip_str


@click.group()
def cli():
    pass


@cli.command(name='save')
@click.option('--database', '-h', type=str, default='monogodb://127.0.0.1:27017', show_default=True, help='Database IP address',
              callback=strip_str)
@click.argument('field', type=str, required=True, callback=strip_str)
@click.argument('data_path', type=str, required=True, callback=strip_str)
def _save(database, field, data_path):
    return _cli_save(database, field, data_path)


@cli.command(name='run-saver')
@click.argument('database', type=str, required=True, callback=strip_str)
@click.argument('message_queue', type=str, required=True, callback=strip_str)
def _run_saver(database, message_queue):
    _cli_run_saver(db_url=database, mq_url=message_queue)


if __name__ == '__main__':
    cli(prog_name='cortex.saver')
