from django.http import HttpResponse
from django.urls import path

app_name = 'app'


def view(r):
    return HttpResponse(f'<h1>{r.ip}</h1>')


urlpatterns = [path('', view), ]
