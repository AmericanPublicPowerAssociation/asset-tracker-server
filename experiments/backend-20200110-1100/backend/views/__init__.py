from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='home')
def home(request):
    return Response('home')


@view_config(route_name='hello')
def hello(request):
    return Response('hello')
