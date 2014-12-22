""" Tests for `bottle-peewee` module. """
from bottle import Bottle
from bottle_peewee import PeeweePlugin
import datetime as dt
from peewee import Model, CharField, DateTimeField, ForeignKeyField


def test_bottle_peewee():

    app = Bottle()
    db = PeeweePlugin('sqlite:///:memory:')

    class Role(Model):
        name = CharField()

        class Meta(object):
            database = db.proxy

    class User(Model):
        name = CharField()
        created = DateTimeField(default=dt.datetime.now)

        role = ForeignKeyField(Role)

        class Meta(object):
            database = db.proxy

    app.install(db)

    db.database.create_tables([User, Role])
    User.create(name='test', role=Role.create(name='admin'))
    assert [user for user in User.select()]

    data = db.to_dict(User.get())
    assert data
    assert data['name'] == 'test'
    assert data['created']
