from argparse import ArgumentParser, SUPPRESS
from pathlib import Path
import sqlite3 as sql

from dotenv import dotenv_values
from trello import TrelloClient

from backup import backup_boards


def argument_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Backup boards from Trello')
    parser.add_argument('--public-key', metavar='KEY', dest='PUBLIC_KEY',
                        help='Public key of Trello user')
    parser.add_argument('--token', dest='APP_TOKEN', help='Token for Trello API')
    parser.add_argument('-p', '--database-path', type=Path, required=True, dest='PATH',
                        help='Path to sqlite database. If file does not exist, it will be created')
    parser.add_argument('-e', '--env-file', type=Path, dest='ENV_FILE', help='Path to .env file',
                        default=Path(__file__).parent.parent / '.env', )
    parser.add_argument('-b', '--board-id', nargs='*', action='extend', metavar='BOARD',
                        dest='BOARD_IDS', default=SUPPRESS,
                        help='Specify short id of board which you want to backup. '
                             'You can get this id from the url of that board')
    parser.add_argument('-w', '--workspace-id', nargs='*', action='extend', metavar='WORKSPACE',
                        dest='WORKSPACE_IDS', default=SUPPRESS,
                        help='Specify workspaces whose boards you want to backup. '
                             'You can get this id from the url of that workspace')
    return parser


def main():
    parser = argument_parser()
    args = vars(parser.parse_args())

    args.update(dotenv_values(args['ENV_FILE']))

    key = args['PUBLIC_KEY']
    token = args['APP_TOKEN']
    workspace_ids = args.get('WORKSPACE_IDS', [])
    board_ids = args.get('BOARD_IDS', [])
    path: Path = args['PATH']

    if len(workspace_ids) + len(board_ids) == 0:
        print('Neither workspace nor board is specified. Maybe, you forget it?')

    client = TrelloClient(api_key=key, api_secret=token)

    with sql.connect(path) as conn:
        backup_boards(client, conn, board_external_short_ids=board_ids, workspace_ids=workspace_ids)


if __name__ == '__main__':
    main()
