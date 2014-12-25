from peewee import CompositeKey, ForeignKeyField, CharField, DateTimeField
from peewee import SqliteDatabase, IntegrityError, DoesNotExist, fn, Model

from main import RfAttendance

app = RfAttendance.get_running_app()
import logging
import sys
logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
database = SqliteDatabase(
    app.load_config().get('General', 'database_file')
)


class BaseModel(Model):
    class Meta:
        database = database


class Auth(BaseModel):
    username = CharField()
    password = CharField()


class Member(BaseModel):
    tag_id = CharField(unique=True)
    name = CharField()


class Session(BaseModel):
    name = CharField(unique=True)
    date = DateTimeField()


class SessionAttendance(BaseModel):
    session = ForeignKeyField(Session, 'attendance')
    member = ForeignKeyField(Member, 'sessions')

    class Meta:
        primary_key = CompositeKey('session', 'member')


def create_tables():
    database = SqliteDatabase(
        app.load_config().get('General', 'database_file')
    )

    Auth.create_table(fail_silently=True)
    Member.create_table(fail_silently=True)
    Session.create_table(fail_silently=True)
    SessionAttendance.create_table(fail_silently=True)

create_tables()
