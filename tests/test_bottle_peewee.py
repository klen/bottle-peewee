""" Tests for `bottle-peewee` module. """


def test_bottle_peewee():
    from bottle import Bottle
    from bottle_peewee import PeeweePlugin
    from peewee import Model, CharField

    app = Bottle()
    db = PeeweePlugin('sqlite:///:memory:')

    class User(Model):
        name = CharField()

        class Meta(object):
            database = db.proxy

    app.install(db)

    db.database.create_table(User)
    User.create(name='test')
    assert [user for user in User.select()]
