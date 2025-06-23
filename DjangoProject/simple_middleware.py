def simple_middleware(get_response):
    def middleware(request):

        #forward going area
        print("this is before view")
        response = get_response(request)

        #backward going area
        print("this is after view")

        return response
    return middleware

def another_middleware(get_response):

    print("Setup second middleware")

    def middleware(request):

        # forward going area
        print("This is another middleware before view")
        response = get_response(request)
        print("This is another middleware after view")
        # backward going area

        return response

    return middleware


# def sum(a,b):
#     return a+b
#
# def perform_ops(op,a,b):
#     return op(a,b)
#
# perform_ops(sum,1,2)