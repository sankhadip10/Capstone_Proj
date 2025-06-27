from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q, F,Value,Func
from django.db.models.functions import Concat
from django.db.models import Count,Max,Min,Avg,Sum
from store.models import Product, OrderItem, Order, Customer


# Create your views here.
def say_hello(request):
    # return HttpResponse("Hello World!")
    # querry_set = Product.objects.filter(unit_price__range=(20,30))
    # querry_set = Product.objects.filter(collection__id__range=(1,2,3))
    # querry_set = Product.objects.filter(title__icontains='coffee')
    # querry_set = Product.objects.filter(title__startswith='coffee')
    # querry_set = Product.objects.filter(last_update__year=2021)
    # querry_set = Product.objects.filter(description__isnull=True

    # Products:inventory <10 AND price <20
    # querry_set = Product.objects.filter(inventory__lt=10,unit_price__lt=20)
    # querry_set = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)
    # querry_set = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=10))
    # print(querry_set)
    # Products: invnetory = price
    # querry_set = Product.objects.filter(inventory=F('unit_price'))

    # querry_set = Product.objects.filter(inventory=F('collection__id'))
    # sorting
    # querry_set = Product.objects.order_by('title')
    # querry_set = Product.objects.order_by('unit_price','-title')
    # querry_set = Product.objects.order_by('unit_price','-title').reverse()
    # querry_set = Product.objects.filter(collection__id=1).order_by('unit_price')
    # querry_set = Product.objects.order_by('unit_price')[0]
    # querry_set = Product.objects.earliest('unit_price')
    # querry_set = Product.objects.latest('unit_price')

    # querry_set = Product.objects.all()[:5]
    # querry_set = Product.objects.all()[5:10]

    # querry_set =Product.objects.values('id','title')
    # querry_set =Product.objects.values('id','title','collection__title')
    # tuple
    # querry_set =Product.objects.values_list('id','title','collection__title')

    # select products that have been ordered and sort them by title
    # querry_set = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')

    # querry_set = Product.objects.only('id','title')
    # querry_set = Product.objects.defer('description')

    # querry_set = Product.objects.select_related('collection').all()

    # querry_set = Product.objects.select_related('collection').all()
    # select_related(1)
    # prefetch_related(n)
    # querry_set = Product.objects.select_related('collection__someOtherField').all()
    # querry_set = Product.objects.prefetch_related('promotions').all()
    # querry_set = Product.objects.prefetch_related('promotions').select_related('collection').all()
    # querry_set = Order.objects.select_related(
    #     'customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]

    # return render(request, 'hello.html', {'name': 'Sankha', 'products': list(querry_set)})

    # result = Product.objects.filter(collection__id=1).aggregate(count = Count('id'),min_price = Min('unit_price'))

    #Annotation
    # queryset=Customer.objects.annotate(is_new=Value(True))
    # queryset=Customer.objects.annotate(new_id=F('id')+1)
    # queryset=Customer.objects.annotate(
    #     full_name=Func(F('first_name'),Value(' '),F('last_name'),function='CONCAT')
    # )

    queryset=Customer.objects.annotate(
        full_name=Concat('first_name',Value(' '),'last_name')
    )
    # return render(request, 'hello.html', {'name': 'Sankha', 'orders': list(querry_set)})
    # return render(request, 'hello.html', {'name': 'Sankha', 'result': result})
    return render(request, 'hello.html', {'name': 'Sankha', 'result': list(queryset)})
