from django.contrib import admin
from DjangoProject.models import User,Product

# admin.site.register(User)
# admin.site.register(Product)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ['username','name','email']
    list_display = ['username','name']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ['name','price','description']