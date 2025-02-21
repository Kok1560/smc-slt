from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls import handler404
from django.shortcuts import render

urlpatterns = [
    path('page-list-product', views.page_list_product, name='page_list_product'),
    path('page-add-product', views.page_add_product, name='page_add_product'),
    path('page-list-inventory', views.page_list_inventory, name='page_list_inventory'),
    path('page-add-inventory', views.page_add_inventory, name='page_add_inventory'),
    path('page-list-party', views.page_list_party, name='page_list_party'),
    path('page-add-party', views.page_add_party, name='page_add_party'),
    path('page-list-maint', views.page_list_maint, name='page_list_maint'),
    path('page-add-maint', views.page_add_maint, name='page_add_maint'),
    path('add-order-<int:party_code>', views.page_add_order, name='page_add_order'),
    path('page-product-report', views.page_product_report, name='page_product_report'),
    path('page-inventory-report', views.page_inventory_report, name='page_inventory_report'),
    path('search-for-device', views.search_for_device, name='search_for_device'),
    path('update-inventory-<int:id>', views.page_update_inventory, name='page_update_inventory'),
    path('update-product-<str:product_id>', views.page_update_product, name='page_update_product'),
    path('delete-inventory-<int:id>', views.page_delete_inventory, name='page_delete_inventory'),
    path('view-product-<str:product_id>', views.page_view_product, name='page_view_product'),
    path('delete-product-<path:product_id>', views.page_delete_product, name='page_delete_product'),
    path('view-inventory-<int:id>', views.page_view_inventory, name='page_view_inventory'),
    path('update-party-<int:party_code>', views.page_update_party, name='page_update_party'),
    path('delete-party-<int:party_code>', views.page_delete_party, name='page_delete_party'),
    path('delete-product-order-<int:id>', views.delete_product_order, name='delete_product_order'),
    path('invoice-<int:party_code>', views.invoice_page, name='invoice_page'),
    path('return-order-<int:party_code>', views.page_return_order, name='page_return_order'),
    path('delete-maint-<int:id>', views.page_delete_maint, name='page_delete_maint'),
    path('search-product-<str:id>', views.search_for_device, name='search_for_device'),
    path('page-list-users', views.page_list_users, name='page_list_users'),
    path('page-add-package', views.page_add_package, name='page_add_package'),
    path('page-list-package', views.page_list_package, name='page_list_package'),
    path('update-package-<int:id>', views.page_update_package, name='page_update_package'),
    path('delete-package-<int:id>', views.delete_package, name='delete_package'),
    path('return-maint-<int:id>', views.return_maint, name='return_maint'),
]

def custom_404(request, exception):
    return render(request, '404.html', status=404)

