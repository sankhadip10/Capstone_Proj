from django.http import HttpRequest,HttpResponse
import json

def webhook(request: HttpRequest):
    print(request.headers)
    print(json.loads(request.body))

    return HttpResponse('webhook received')