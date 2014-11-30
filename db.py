import sqlite3
import os


class Database:
    @classmethod
    def get_instance(cls):
        try:
            return cls.db_instance
        except AttributeError:
            cls.db_instance = Database()
            return cls.db_instance

    def __init__(self):
        self.db = sqlite3.connect('db.sqlite')
        # Couldn't find a clean way to figure out if db is alreay installed or not
        self._install_db()

    def _install_db(self):
        # Try to install database (in a safe way)
        self.create_table(
            table_name='auth',
            columns=[
                ('id', 'INTEGER'),
                ('username', 'TEXT UNIQUE'),
                ('password', 'TEXT')
            ],
            primary_key=['id']
        )
        self.create_table(
            table_name='members',
            columns=[
                ('id', 'INTEGER'),
                ('tag_id', 'TEXT UNIQUE'),
                ('english_name', 'TEXT'),
                ('persian_name', 'TEXT')
            ],
            primary_key=['id']
        )
        self.create_table(
            table_name='sessions',
            columns=[
                ('session_id', 'INTEGER'),
                ('session_name', 'TEXT')
            ],
            primary_key=['session_id']
        )
        self.create_table(
            table_name='sessions_attendance',
            columns=[
                ('session_id', 'INTEGER'),
                ('tag_id', 'TEXT')
            ],
            primary_key=['session_id', 'tag_id']
        )

    def create_table(self, table_name, columns, primary_key):
        columns_str = ', '.join(map(lambda column: ' '.join(column), columns))
        primary_key_str = ', '.join(primary_key)
        try:
            cursor = self.db.cursor()
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {}  ({}, PRIMARY KEY ({}))'.format(
                    table_name, columns_str, primary_key_str
                )
            )
            self.db.commit()
        except sqlite3.Error as e:
            self.db.rollback()
            print('Database error occurred, {}'.format(e.args[0]))
            exit(1)
        else:
            setattr(
                self, 'table_{}'.format(table_name),
                map(lambda column: column[0], columns)
            )

    def get_auth(self):
        return self.db.execute(
            'SELECT username, password FROM auth LIMIT 1'
        ).fetchone()

    def save_auth(self, username, password):
        try:
            cursor = self.db.cursor()
            cursor.execute('DELETE FROM auth')  # Only 1 auth data
            cursor.execute(
                'INSERT INTO auth (username, password) VALUES (?, ?)',
                (username, password)
            )
            self.db.commit()
        except sqlite3.Error:
            self.db.rollback()
            raise

    def save_members(self, memebers):
        for member_id, names in memebers.items():
            try:
                self.db.execute(
                    'INSERT INTO members VALUES (?, ?, ?, ?)',
                    (
                        member_id, names['tag_id'],
                        names['english_name'], names['persian_name']
                    )
                )
                self.db.commit()
            except sqlite3.IntegrityError:
                pass            # No duplication

    def get_members_list(self):
        members_list = self.db.execute('SELECT * FROM members').fetchall()
        return self._dict_result('members', members_list)

    def save_sessions(self, sessions):
        for session_id, session_info in sessions.items():
            try:
                self.db.execute(
                    'INSERT INTO sessions VALUES (?, ?)',
                    (session_id, session_info['session_name'])
                )
                self.db.commit()
            except sqlite3.IntegrityError:
                pass            # No duplication

    def get_sessions_list(self):
        sessions_list = self.db.execute('SELECT * FROM sessions').fetchall()
        return self._dict_result('sessions', sessions_list)

    def add_attendance(self, session_id, tag_id):
        try:
            self.db.execute(
                'INSERT INTO sessions_attendance VALUES (?, ?)',
                (session_id, tag_id)
            )
            self.db.commit()
        except sqlite3.IntegrityError:
            raise DuplicationError

    def register_member(self, tag_id, english_name, persian_name):
        try:
            self.db.execute(
                'INSERT INTO members (tag_id, english_name, persian_name) \
                VALUES (?, ?, ?)',
                (tag_id, english_name, persian_name)
            )
            self.db.commit()
        except sqlite3.IntegrityError:
            raise DuplicationError

    def get_member(self, field, value):
        member = self.db.execute(
            'SELECT * FROM members where {} = {}'.format(field, value)
        ).fetchall()
        return self._dict_result('members', member)

    def _dict_result(self, table_name, result):
        table_columns = getattr(self, 'table_{}'.format(table_name))
        result_dict = {}
        for item in result:
            result_dict[item[0]] = dict(zip(table_columns[1:], item[1:]))

        return result_dict


class DuplicationError(Exception):
    pass
