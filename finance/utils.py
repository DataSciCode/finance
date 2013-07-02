from django.db.models import Model
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from django.forms.models import model_to_dict
from decimal import Decimal

def to_dict(data, attrs=None):
    if isinstance(data, dict):
        res = {}
        if attrs:
            for a in attrs:
                res[a] = to_dict(data[key])
        else:
            for key in data:
                res[key] = to_dict(data[key])
        return res
    elif isinstance(data, list):
        res = []
        for element in data:
            res.append(to_dict(element))
        return res
    elif isinstance(data, QuerySet):
        return to_dict(list(data))
    elif isinstance(data, Model):
        print model_to_dict(data)
        r = model_to_dict(data)
        if attrs:
            res = {}
            for a in attrs:
                res[a] = r[a]
            return res
        else:
            return r
    else:
        return data
