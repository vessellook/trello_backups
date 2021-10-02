import sqlite3 as sql
from typing import List, Optional

from trello import TrelloClient, List as TrelloList, Board, Card, Attachments


def set_schema(con: sql.Connection):
    for table in ['board', 'list', 'card', 'attachment']:
        con.execute(f'DROP TABLE IF EXISTS {table}')

    con.execute(
        """CREATE TABLE board (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_long_id TEXT UNIQUE,
            external_short_id TEXT UNIQUE,
            name TEXT
        )""")
    con.execute(
        """CREATE TABLE list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE,
            name TEXT,
            board_id INT REFERENCES board(id)
        )""")
    con.execute(
        """CREATE TABLE card (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE,
            name TEXT,
            description TEXT,
            list_external_id TEXT,
            board_id INT REFERENCES board(id)
        )""")
    con.execute(
        """CREATE TABLE attachment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE,
            name TEXT,
            url TEXT,
            card_id INT REFERENCES card(id)
        )""")


def insert_board(con: sql.Connection, board: Board, short_id=None) -> int:
    if short_id is None:
        cur = con.execute(
            "INSERT INTO board (external_long_id, name) VALUES (?, ?)", (board.id, board.name))
    else:
        cur = con.execute(
            "INSERT INTO board (external_long_id, name, external_short_id) VALUES (?, ?, ?)",
            (board.id, board.name, short_id))
    return cur.lastrowid


def insert_lists(con: sql.Connection, board_id: int, lists: List[TrelloList]):
    con.executemany(
        "INSERT INTO list (external_id, name, board_id) VALUES (?, ?, ?)",
        ((trello_list.id, trello_list.name, board_id) for trello_list in lists))


def insert_card(con: sql.Connection, board_id: int, card: Card) -> int:
    cur = con.execute(
        "INSERT INTO card (external_id, name, description, list_external_id, board_id)"
        " VALUES (?, ?, ?, ?, ?)",
        (card.id, card.name, card.desc, card.list_id, board_id))
    return cur.lastrowid


def insert_attachments(con: sql.Connection, card_id: int, attachments: List[Attachments]):
    con.executemany(
        "INSERT INTO attachment (external_id, name, url, card_id) VALUES (?, ?, ?, ?)",
        ((a.id, a.name, a.url, card_id) for a in attachments))


def get_board_ids(client: TrelloClient, workspace_ids) -> List[str]:
    boards = []
    for workspace_id in workspace_ids:
        workspace = client.get_organization(workspace_id)
        boards.extend(workspace.all_boards())
    return [board.id for board in boards]


def backup_board(conn: sql.Connection, board: Board, short_id: Optional[str] = None):
    lists = board.all_lists()
    cards = board.all_cards()
    board_id = insert_board(conn, board, short_id)
    insert_lists(conn, board_id, lists)
    for card in cards:
        attachments = [Attachments.from_json(a) for a in card.attachments]
        card_id = insert_card(conn, board_id, card)
        if attachments:
            insert_attachments(conn, card_id, attachments)


def backup_boards(client: TrelloClient, conn: sql.Connection, board_external_short_ids: list,
                  workspace_ids: list):
    set_schema(conn)
    for external_short_id in board_external_short_ids:
        backup_board(conn, client.get_board(external_short_id), short_id=external_short_id)
    for external_long_id in get_board_ids(client, workspace_ids):
        backup_board(conn, client.get_board(external_long_id), short_id=None)
