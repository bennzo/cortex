import click
from .saver import _cli_save, _cli_run_saver


@click.group()
def cli():
    pass


@cli.command(name='save')
@click.option('--database', '-h', default='monogodb://127.0.0.1:5432', show_default=True, help='Database IP address')
@click.argument('field', required=True)
@click.argument('data_path', required=True)
def _save(database, field, data_path):
    return _cli_save(database, field, data_path)


@cli.command(name='run-saver')
@click.argument('database', required=True)
@click.argument('message_queue', required=True)
def _run_saver(database, message_queue):
    _cli_run_saver(db_url=database, mq_url=message_queue)


if __name__ == '__main__':
    cli(prog_name='cortex.saver')
