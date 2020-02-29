from pathlib import Path
from cortex.website import Website

web = Website()

_INDEX_HTML = '''
<html>
    <head>Brain Computer Interface</head>
    <body>
        <ul>
            {users}
        </ul>
    </body>
</html>
'''
_USER_LINE_HTML = '''
<li><a href="/users/{user_id}">user {user_id}</a></li>
'''

_USER_THOUGHTS_MENU = '''
<html>
    <head>
        <title>Brain Computer Interface: User {user_id}</title>
    </head>
    <body>
        <table>
            {thoughts}
        </table>
    </body>
</html>
'''
_USER_THOUGHT_LINE = '''
<tr>
    <td>{ts}</td>
    <td>{thought}</td>
</tr>
'''


@web.route('/')
def index():
    global data_dir
    users_html = []
    user_list = [user_dir.name for user_dir in data_dir.iterdir()]
    for user in user_list:
        users_html.append(_USER_LINE_HTML.format(user_id=user))
    html = _INDEX_HTML.format(users='\n'.join(users_html))
    return 200, html


@web.route(r'^/users/(?P<uid>\d+)$')
def user_thoughts(uid):
    global data_dir
    user_dir = data_dir / str(uid)
    if user_dir.exists():
        thoughts_html = []
        for thought_file in user_dir.iterdir():
            date_time = thought_file.stem.split('_')
            date_time[1] = date_time[1].replace('-', ':')
            ts = str.join(' ', date_time)
            with open(thought_file, 'r') as f:
                for thought in f:
                    thoughts_html.append(_USER_THOUGHT_LINE.format(ts=ts, thought=thought))
        html = _USER_THOUGHTS_MENU.format(user_id=uid, thoughts=str.join('\n', thoughts_html))
        return 200, html
    else:
        return 404, ""


def run_webserver(address, data_dir):
    globals()['data_dir'] = Path(data_dir)
    web.run(address)


def main(argv):
    if len(argv) != 3:
        print(f'USAGE: {argv[0]} <address> <data_dir>')
        return 1
    try:
        ip_addr, port = argv[1].split(':')
        run_webserver((ip_addr, int(port)), argv[2])
    except Exception as error:
        print(f'ERROR: {error}')
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
