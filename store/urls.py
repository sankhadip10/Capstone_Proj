from django.urls import path
from rest_framework.routers import SimpleRouter,DefaultRouter
from rest_framework_nested import routers
from . import views
from pprint import pprint

router = routers.DefaultRouter()

# router = DefaultRouter()
router.register('products', views.ProductViewSet,basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet,basename='orders')

# pprint(router.urls)

products_router = routers.NestedDefaultRouter(router, 'products',lookup='product')
products_router.register('reviews', views.ReviewViewSet,basename='product-reviews')
products_router.register('images', views.ProductImageViewSet,basename='product-images')


carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

# URLConf
urlpatterns = router.urls + products_router.urls + carts_router.urls +[
# urlpatterns = [
#     # path('products/', views.product_list),
#     path('products/', views.ProductList.as_view()),
#     # path('products/<int:id>', views.product_detail),
#     path('products/<int:pk>', views.ProductDetail.as_view()),
#     # path('collections/', views.collection_list),
#     path('collections/', views.CollectionList.as_view()),
#     # path('collections/<int:pk>', views.collection_detail, name='collection-detail')
#     path('collections/<int:pk>', views.CollectionDetail.as_view(), name='collection-detail')
    path('test-payment/', views.test_payment_view, name='test-payment'),
]
