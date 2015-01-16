import logging
import sys
from peewee import CompositeKey, ForeignKeyField, CharField, DateTimeField, Proxy
from peewee import SqliteDatabase, IntegrityError, DoesNotExist, fn, Model

database_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy


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


def create_instance(db_file):
    global database_proxy
    database = SqliteDatabase(db_file)
    database_proxy.initialize(database)
    create_tables()
    log_queries()


def create_tables():
    Auth.create_table(fail_silently=True)
    Member.create_table(fail_silently=True)
    Session.create_table(fail_silently=True)
    SessionAttendance.create_table(fail_silently=True)


def log_queries():
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))
