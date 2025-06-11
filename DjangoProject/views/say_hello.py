from django.http import HttpResponse
from django.http import HttpRequest


def say_hello(request):
    return HttpResponse("Hello, world. You're at the polls page.")

def say_hello_with_name(request:HttpRequest,name):
    print(request.headers)
    # print(request.)
    return HttpResponse("Hello, world. You're at the polls page ,%s"% name)