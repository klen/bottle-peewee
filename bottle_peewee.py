# Package information
# ===================

__version__ = "0.1.0"
__project__ = "bottle-peewee"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"


import datetime

from peewee import PeeweeException, Proxy, ForeignKeyField, Model
from playhouse.db_url import connect


class PeeweePlugin(object):

    """ Integrate peewee to bottle. """

    name = 'peewee'
    api = 2
    default_connection = 'sqlite:///db.sqlite'

    def __init__(self, connection=None):
        self.database = None
        self.connection = connection or self.default_connection
        self.proxy = Proxy()
        self.uri = None
        self.serializer = Serializer()

    def setup(self, app):
        """ Initialize the application. """

        self.connection = app.config.get('DATABASE_URI', self.connection)
        self.database = connect(self.connection)
        self.proxy.initialize(self.database)

    def apply(self, callback, route):

        def wrapper(*args, **kwargs):
            if self.uri.startswith('sqlite'):
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


def get_dictionary_from_model(model, fields=None, exclude=None):
    model_class = type(model)
    data = {}

    fields = fields or {}
    exclude = exclude or {}
    curr_exclude = exclude.get(model_class, [])
    curr_fields = fields.get(model_class, model._meta.get_field_names())

    for field_name in curr_fields:
        if field_name in curr_exclude:
            continue
        field_obj = model_class._meta.fields[field_name]
        field_data = model._data.get(field_name)
        if isinstance(field_obj, ForeignKeyField) and field_data and field_obj.rel_model in fields:
            rel_obj = getattr(model, field_name)
            data[field_name] = get_dictionary_from_model(rel_obj, fields, exclude)
        else:
            data[field_name] = field_data
    return data


def get_model_from_dictionary(model, field_dict):
    if isinstance(model, Model):
        model_instance = model
        check_fks = True
    else:
        model_instance = model()
        check_fks = False
    models = [model_instance]
    for field_name, value in field_dict.items():
        field_obj = model._meta.fields[field_name]
        if isinstance(value, dict):
            rel_obj = field_obj.rel_model
            if check_fks:
                try:
                    rel_obj = getattr(model, field_name)
                except field_obj.rel_model.DoesNotExist:
                    pass
                if rel_obj is None:
                    rel_obj = field_obj.rel_model
            rel_inst, rel_models = get_model_from_dictionary(rel_obj, value)
            models.extend(rel_models)
            setattr(model_instance, field_name, rel_inst)
        else:
            setattr(model_instance, field_name, field_obj.python_value(value))
    return model_instance, models


class Serializer(object):
    date_format = '%Y-%m-%d'
    time_format = '%H:%M:%S'
    datetime_format = ' '.join([date_format, time_format])

    def convert_value(self, value):
        if isinstance(value, datetime.datetime):
            return value.strftime(self.datetime_format)
        elif isinstance(value, datetime.date):
            return value.strftime(self.date_format)
        elif isinstance(value, datetime.time):
            return value.strftime(self.time_format)
        elif isinstance(value, Model):
            return value.get_id()
        else:
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

    def serialize_object(self, obj, fields=None, exclude=None):
        data = get_dictionary_from_model(obj, fields, exclude)
        return self.clean_data(data)


class Deserializer(object):
    @staticmethod
    def deserialize_object(model, data):
        return get_model_from_dictionary(model, data)

# pylama:ignore=W0212
