Bottle Peewee
#############

.. _description:

Bottle Peewee -- Provide Peewee ORM integration to Bottle framework.

.. _badges:

.. image:: http://img.shields.io/travis/klen/bottle-peewee.svg?style=flat-square
    :target: http://travis-ci.org/klen/bottle-peewee
    :alt: Build Status

.. image:: http://img.shields.io/coveralls/klen/bottle-peewee.svg?style=flat-square
    :target: https://coveralls.io/r/klen/bottle-peewee
    :alt: Coverals

.. image:: http://img.shields.io/pypi/v/bottle-peewee.svg?style=flat-square
    :target: https://pypi.python.org/pypi/bottle-peewee

.. image:: http://img.shields.io/pypi/dm/bottle-peewee.svg?style=flat-square
    :target: https://pypi.python.org/pypi/bottle-peewee

.. image:: http://img.shields.io/gratipay/klen.svg?style=flat-square
    :target: https://www.gratipay.com/klen/
    :alt: Donate

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 2.6

.. _installation:

Installation
=============

**Bottle Peewee** should be installed using pip: ::

    pip install bottle-peewee

.. _usage:

Usage
=====

::

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


Configuration
-------------

PEEWEE_CONNECTION -- A connection string to database

.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/bottle-peewee/issues

.. _contributing:

Contributing
============

Development of Bottle Peewee happens at: https://github.com/klen/bottle-peewee


Contributors
=============

* klen_ (Kirill Klenov)

.. _license:

License
=======

Licensed under a `BSD license`_.

.. _links:

.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _klen: https://github.com/klen
