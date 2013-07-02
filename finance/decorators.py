from utils import to_dict
from django.http import Http404, HttpResponse
import json as js
from time import mktime
import datetime
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist

def post(f):
    def call(request):
        if request.method == 'POST':
            return f(request)
        else:
            raise Http404
    return call

class DjangoEncoder(js.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        elif isinstance(obj, Decimal):
            return str(obj)
        return js.JSONEncoder.default(self, obj)

def json(f):
    def call(request, *args, **kwargs):
        response = HttpResponse(js.dumps(to_dict(f(request, *args, **kwargs)), cls=DjangoEncoder), content_type="application/json")
        return response
    return call

def optional(f):
    def call(request):
        try:
            return f(request)
        except ObjectDoesNotExist:
            return {"error": 1, "message": "Object does not exist"}
    return call
