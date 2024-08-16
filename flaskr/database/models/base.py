from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy

VAL_MSG = 'Valor de {{}} debe ser {}'
NUMBER_VAL_MSG = VAL_MSG.format('un número')
ID_VAL_MSG = NUMBER_VAL_MSG.format('ID')

TABLENAMES = {
    'person': {
        'singular': 'person',
        'tb': 'Person',
        'plural': 'people'
    },
    'cne': {
        'singular': 'cne',
        'tb': 'Cne',
        'plural': 'cnes'
    },
    'prty': {
        'singular': 'property',
        'tb': 'Property',
        'plural': 'properties'
    },
    'block': {
        'singular': 'block',
        'tb': 'Block',
        'plural': 'blocks'
    },
    'commune': {
        'singular': 'commune',
        'tb': 'Commune',
        'plural': 'communes'
    },
    'region': {
        'singular': 'region',
        'tb': 'Region',
        'plural': 'regions'
    },
    'form': {
        'singular': 'form',
        'tb': 'Form',
        'plural': 'forms'
    },
    'transaction': {
        'singular': 'transaction',
        'tb': 'Transaction',
        'plural': 'transactions'
    },
    'multi_prty': {
        'singular': 'multi_property',
        'tb': 'MultiProperty',
        'plural': 'multi_properties'
    }
}


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
