def bingo(gn):
    def whatever(*args, **kwargs):
        print('bingo')
        res=gn(*args, **kwargs)
        print('After')
        return res
    return whatever


@bingo
def say_hello(a,b):
    # print("Hello World")
    print(a,b)
    return a+b

ans = say_hello(10,20)
print(ans)