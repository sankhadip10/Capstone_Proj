from django.http import HttpResponse
from django.http import HttpRequest

from DjangoProject.models import User
import json
from django.shortcuts import get_object_or_404

def say_hello(request):
    return HttpResponse("Hello, world. You're at the polls page.")


def say_hello_with_name(request: HttpRequest, name):
    print(request.headers)
    # print(request.)
    return HttpResponse("Hello, world. You're at the polls page ,%s" % name)


def users(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        users = User.objects.all()
        serialized_users = [user.name for user in users]
        return HttpResponse(json.dumps(serialized_users))

    if request.method == "POST":
        # return HttpResponse('POST request')
        body = json.loads(request.body)
        user = User(name=body['name'], email=body['email'], address=body['address'], username=body['username'],
                    title=body['title'])
        user.save()
        return HttpResponse(json.dumps({'id': user.id, 'name': user.name}))

def get_or_update_or_delete_user(request: HttpRequest,id:int) -> HttpResponse:

    if request.method == "GET":
        user = get_object_or_404(User,id=id)
        # user = User.objects.get(id=id)
        return HttpResponse(json.dumps({'id': user.id, 'name': user.name,'email':user.email, 'address': user.address, 'username': user.username, 'title': user.title}))

    if request.method == "PUT":
        # return HttpResponse('POST request')
        body = json.loads(request.body)

        # user = User.objects.get(id=id)
        user =get_object_or_404(User,id=id)
        user.name = body['name']
        user.email = body['email']
        user.address = body['address']
        user.username = body['username']
        user.title = body['title']
        user.save()
        return HttpResponse(json.dumps({'id': user.id, 'name': user.name}))

    if request.method == "DELETE":
        user = get_object_or_404(User,id=id)
        user.delete()
        return HttpResponse(json.dumps({'id': user.id, 'deleted': True}))