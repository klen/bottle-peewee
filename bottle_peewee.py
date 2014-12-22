# Package information
# ===================
import datetime

from peewee import PeeweeException, Proxy, Model
from playhouse.db_url import connect
from playhouse.shortcuts import model_to_dict, dict_to_model


__version__ = "0.1.5"
__project__ = "bottle-peewee"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"


class PeeweePlugin(object):

    """ Integrate peewee to bottle. """

    name = 'peewee'
    api = 2
    default_connection = 'sqlite:///db.sqlite'

    def __init__(self, connection=None):
        self.database = None
        self.connection = connection or self.default_connection
        self.proxy = Proxy()
        self.serializer = Serializer()

    def setup(self, app):
        """ Initialize the application. """

        app.config.setdefault('PEEWEE_CONNECTION', self.connection)
        self.connection = app.config.get('PEEWEE_CONNECTION')
        self.database = connect(self.connection)
        self.proxy.initialize(self.database)

    def apply(self, callback, route):

        def wrapper(*args, **kwargs):
            if self.connection.startswith('sqlite'):
                return callback(*args, **kwargs)

            self.database.connect()
            try:
                with self.database.transaction():
                    response = callback(*args, **kwargs)
            except PeeweeException:
                self.database.rollback()
                raise
            finally:
                self.database.commit()
                if not self.database.is_closed():
                    self.database.close()

            return response

        return wrapper

    def to_dict(self, obj, **kwargs):
        return self.serializer.serialize_object(obj, **kwargs)


class Serializer(object):
    date_format = '%Y-%m-%d'
    time_format = '%H:%M:%S'
    datetime_format = ' '.join([date_format, time_format])

    def convert_value(self, value):
        if isinstance(value, datetime.datetime):
            return value.strftime(self.datetime_format)

        if isinstance(value, datetime.date):
            return value.strftime(self.date_format)

        if isinstance(value, datetime.time):
            return value.strftime(self.time_format)

        if isinstance(value, Model):
            return value.get_id()

        return value

    def clean_data(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                self.clean_data(value)
            elif isinstance(value, (list, tuple)):
                data[key] = map(self.clean_data, value)
            else:
                data[key] = self.convert_value(value)
        return data

    def serialize_object(self, obj, **kwargs):
        data = model_to_dict(obj, **kwargs)
        return self.clean_data(data)


class Deserializer(object):

    @staticmethod
    def deserialize_object(model, data):
        return dict_to_model(model, data)
