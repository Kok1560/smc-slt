from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from datetime import date
from .models import *
from .forms import *
from members.models import CustomUser

# ======================================= Helpers ==================================================

def update_inventory(product_id, quantity_change):
    parent = Product.objects.filter(product_id=product_id).first()
    if parent:
        parent_name = parent.product_name
    else:
        return  # Exit function if product doesn't exist

    inventory = Inventory.objects.get(product_name=parent_name)
    inventory.remain_quantity += quantity_change
    inventory.save()

# ======================================= Product Functions ==================================================

def page_list_product(request):
    context = {'products': Product.objects.all()}
    return render(request, 'pages/page-list-product.html', context)

def page_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            inventory = Inventory.objects.get(product_name=form.cleaned_data['product_name'])
            if inventory.remain_quantity == inventory.inventory_quantity:
                messages.warning(request, "You Can't Add More Devices")
            else:
                product = form.save()
                inventory.remain_quantity = Product.objects.filter(product_name=product.product_name).count()
                inventory.save()
                return redirect('/page-add-product')
        else:
            messages.warning(request, "This Device Was Exist!")
    context = {'productform': ProductForm()}
    return render(request, 'pages/page-add-product.html', context)

def page_update_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)  # Ensure the product exists

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)  # Attach instance for update

        if form.is_valid():
            # Check if this product already exists in the database
            existing_product = Product.objects.filter(product_id=product_id).exists()

            if not existing_product:
                messages.warning(request, "Product does not exist! Cannot update.")
            else:
                form.save()  # ✅ This now updates the product instead of creating a new one!
                messages.success(request, "Product updated successfully!")
            return redirect('/page-list-product')
        else:
            messages.warning(request, "Invalid data provided!")
    else:
        form = ProductForm(instance=product)
        form.fields['product_id'].widget.attrs['readonly'] = True

    context = {'productform': form}
    return render(request, 'pages/page-update-product.html', context)


def page_view_product(request, product_id):
    context = {'productform': get_object_or_404(Product, product_id=product_id)}
    return render(request, 'pages/page-view-product.html', context)

def page_delete_product(request, product_id):
    print(f"Deleting Product ID: {product_id}")  # Debugging
    product = get_object_or_404(Product, product_id__iexact=product_id)  # Case-insensitive lookup
    
    if request.method == 'POST':
        filtered_result = Order.objects.filter(product_id=product.product_id).last()
        status = [m.status for m in Maintenance.objects.filter(product_id=product.product_id)]
        
        if filtered_result and filtered_result.state == 'add':
            messages.warning(request, "This Device In Party")
        elif product.product_id in [p.product_id for p in Maintenance.objects.all()] and status[-1] == 'Pending':
            messages.warning(request, "This Device In Maintenance")
        else:
            update_inventory(product.product_id, -1)
            product.delete()
        
        return redirect('/page-list-product')

    return render(request, 'pages/page-delete-product.html')



# ======================================= Inventory Functions ==================================================

def page_list_inventory(request):
    context = {'inventories': Inventory.objects.all()}
    return render(request, 'pages/page-list-inventory.html', context)

def page_add_inventory(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if not request.POST.get('product_name', '').strip():
            messages.warning(request, 'Fields cannot be empty or only contain spaces.')
        elif form.is_valid():
            form.save()
        else:
            messages.warning(request, "This Inventory is Already Exist")
        return redirect('/page-add-inventory')
    context = {'inventoryform': InventoryForm()}
    return render(request, 'pages/page-add-inventory.html', context)

def page_update_inventory(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            if inventory.inventory_quantity < inventory.remain_quantity:
                messages.warning(request, "This Quantity Less Than Devices")
            else:
                form.save()
            return redirect('/page-list-inventory')
    context = {'inventoryform': InventoryForm(instance=inventory)}
    return render(request, 'pages/page-update-inventory.html', context)

def page_delete_inventory(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    if request.method == 'POST':
        try:
            inventory.delete()
            return redirect('/page-list-inventory')
        except ProtectedError:
            messages.warning(request, "You Should Delete Devices Inside This Parent First.")
    return render(request, 'pages/page-delete-inventory.html')

def page_view_inventory(request, id):
    context = {'inventoryform': get_object_or_404(Inventory, id=id)}
    return render(request, 'pages/page-view-inventory.html', context)

# ======================================= Party Functions ==================================================

def page_add_party(request):
    if request.method == 'POST':
        form = PartyForm(request.POST)
        if not all(request.POST.get(field, '').strip() for field in ['party_name', 'leader_name', 'wh_leader']):
            messages.warning(request, 'Fields cannot be empty or only contain spaces.')
        elif form.is_valid():
            form.save()
            return redirect('/page-add-party')
    context = {'partyform': PartyForm()}
    return render(request, 'pages/page-add-party.html', context)

def page_list_party(request):
    context = {'parties': Party.objects.all()}
    return render(request, 'pages/page-list-party.html', context)

def page_update_party(request, party_code):
    party = get_object_or_404(Party, party_code=party_code)
    if request.method == 'POST':
        form = PartyForm(request.POST, instance=party)
        if form.is_valid():
            form.save()
            return redirect('/page-list-party')
    context = {'partyform': PartyForm(instance=party)}
    return render(request, 'pages/page-update-party.html', context)

def page_delete_party(request, party_code):
    party = get_object_or_404(Party, party_code=party_code)
    if request.method == 'POST':
        try:
            party.delete()
            return redirect('/page-list-party')
        except ProtectedError:
            messages.warning(request, "Delete Orders Inside Party First")
    return render(request, 'pages/page-delete-party.html')

# ======================================= Order Functions ==================================================

def page_add_order(request, party_code):
    product_choices = [('', 'Select a product or package')] + \
                      [(product.product_id, product.product_id) for product in Product.objects.all()] + \
                      [(package.pack_name, package.pack_name) for package in Package.objects.all()]
    party = get_object_or_404(Party, party_code=party_code)
    maint_products = [product.product_id for product in Maintenance.objects.all()]

    if party.end_date is not None:
        messages.warning(request, 'This Party Was End')
        return redirect('/page-list-party')

    if request.method == 'POST':
        selected_products = request.POST.getlist('selected_products')
        if selected_products:
            state, names = [], []
            for product in selected_products:
                filtered_result = Order.objects.filter(product_id=product).last()
                status = [m.status for m in Maintenance.objects.filter(product_id=product)]
                if filtered_result and filtered_result.state == 'add':
                    if party == filtered_result.party_code:
                        state.append(True)
                    else:
                        names.append(filtered_result.product_id)
                        state.append(False)
                elif product in maint_products and status[-1] == 'Pending':
                    messages.warning(request, f"This {product} In Maintenance")
                else:
                    Order.objects.create(product_id=product, party_code=party, state='add')
                    update_inventory(product, -1)

            if len(state) == len(selected_products):
                if all(state):
                    messages.warning(request, "Package is Already Added Before")
                elif all(not item for item in state):
                    messages.warning(request, "This Package In Another Party")
                else:
                    for name in names:
                        messages.warning(request, f"{name} In Another Party")
            else:
                for name in names:
                    messages.warning(request, f"{name} In Another Party")

            return redirect(f'/add-order-{party_code}')

        form = OrderForm(request.POST)
        if form.is_valid():
            product_name = form.cleaned_data['product_id']
            filtered_result = Order.objects.filter(product_id=product_name).last()
            products = [product.product_id for product in Order.objects.filter(party_code=party_code, state='add')]
            status = [m.status for m in Maintenance.objects.filter(product_id=product_name)]

            if product_name in products:
                messages.warning(request, "This Device Was Added")
            elif product_name in [pack.pack_name for pack in Package.objects.all()]:
                package = Package.objects.filter(pack_name=product_name).first()
                if package:
                    products_in_package = Product.objects.filter(pack_name=package)
                    if not products_in_package:
                        messages.warning(request, "This Package is Empty")
                    else:
                        context = {
                            'products_in_package': products_in_package,
                            'orderform': form,
                            'orders': Order.objects.filter(party_code=party_code, state='add'),
                            'party_code': party_code
                        }
                        return render(request, 'pages/page-add-order.html', context)
                else:
                    messages.warning(request, "No package found with this name")
            elif filtered_result and filtered_result.state == 'add':
                messages.warning(request, "This Device In Another Party")
            elif product_name in maint_products and status[-1] == 'Pending':
                messages.warning(request, f"This {product_name} In Maintenance")
            else:
                form.save()
                update_inventory(product_name, -1)
                return redirect(f'/add-order-{party_code}')

    add_order = OrderForm(initial={'party_code': party_code, 'state': 'add'})
    add_order.fields['product_id'].widget.choices = product_choices
    context = {
        'orderform': add_order,
        'orders': Order.objects.filter(party_code=party_code, state='add'),
        'party_code': party_code,
    }
    return render(request, 'pages/page-add-order.html', context)

def delete_product_order(request, id):
    product_delete = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        product_delete.delete()
        update_inventory(product_delete.product_id, 1)
        return redirect(f'/add-order-{product_delete.party_code}')
    return render(request, 'pages/page-delete-order.html')

def invoice_page(request, party_code):
    if Order.objects.filter(party_code=party_code).count() == 0:
        messages.warning(request, "This Party is Empty!")
        return redirect('/page-list-party')

    party_details = get_object_or_404(Party, party_code=party_code)
    party_orders = Order.objects.filter(party_code=party_code, state='add')
    party_returns = Order.objects.filter(party_code=party_code, state='recovery')
    
    add_product_names = [Product.objects.get(product_id=order.product_id).product_name for order in party_orders]
    return_product_names = [Product.objects.get(product_id=order.product_id).product_name for order in party_returns]

    add_zipped_orders = zip(set(add_product_names), [add_product_names.count(name) for name in set(add_product_names)])
    return_zipped_orders = zip(set(return_product_names), [return_product_names.count(name) for name in set(return_product_names)])

    context = {
        'partydetails': party_details,
        'partyorders': add_zipped_orders,
        'partyreturns': return_zipped_orders,
        'returnsorder': party_returns
    }
    return render(request, 'pages/pages-invoice.html', context)

def page_return_order(request, party_code):
    product_choices = [('', 'Select a product')] + [(product.product_id, product.product_id) for product in Order.objects.filter(party_code=party_code, state='add')]
    if Party.objects.get(party_code=party_code).end_date is not None:
        messages.warning(request, 'This Party Was End')
        return redirect('/page-list-party')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            if product_id in [order.product_id for order in Order.objects.filter(party_code=party_code, state='recovery')]:
                messages.warning(request, "This Device Was Added")
            else:
                form.save()
                update_inventory(product_id, 1)
                product = Product.objects.get(product_id=product_id)
                product.amount_of_parties += 1
                product.save()

                if sorted([order.product_id for order in Order.objects.filter(party_code=party_code, state='add')]) == \
                   sorted([order.product_id for order in Order.objects.filter(party_code=party_code, state='recovery')]):
                    party = Party.objects.get(party_code=party_code)
                    party.end_date = date.today()
                    party.save()
            return redirect(f'/return-order-{party_code}')
    else:
        form = OrderForm(initial={'party_code': party_code, 'state': 'recovery'})
        form.fields['product_id'].widget.choices = product_choices

    context = {
        'returnform': form,
        'orders': Order.objects.filter(party_code=party_code, state='add'),
        'returnorders': Order.objects.filter(party_code=party_code, state='recovery')
    }
    return render(request, 'pages/page-return-order.html', context)

# ======================================= Maintenance Functions ==================================================

def page_add_maint(request):
    product_choices = [('', 'Select a product')] + [(product.product_id, product.product_id) for product in Product.objects.all()]
    if request.method == 'POST':
        form = MaintForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            filtered_result = Order.objects.filter(product_id=product_id).last()
            status = [m.status for m in Maintenance.objects.filter(product_id=product_id)]

            if product_id in [order.product_id for order in Order.objects.all()] and filtered_result and filtered_result.state == 'add':
                messages.warning(request, "This Device In Party")
            elif status and status[-1] == 'Pending':
                messages.warning(request, "This Device Was Added")
            else:
                form.save()
                update_inventory(product_id, -1)
            return redirect('/page-add-maint')
    else:
        form = MaintForm()
        form.fields['product_id'].widget.choices = product_choices
    context = {'maintform': form}
    return render(request, 'pages/page-add-maint.html', context)

def return_maint(request, id):
    maint_instance = get_object_or_404(Maintenance, id=id)
    if maint_instance.maint_date is not None:
        messages.warning(request, "This Device Already Returned!")
        return redirect('/page-list-maint')

    if request.method == 'POST':
        form = ReturnMaintForm(request.POST, instance=maint_instance)
        if form.is_valid():
            if not all([maint_instance.status, maint_instance.received_by, maint_instance.maint_date]):
                messages.warning(request, "You Should Fill All Fields")
            elif maint_instance.status == 'Pending':
                messages.warning(request, "Change Status From Pending to Good or Failed")
            else:
                product_name = maint_instance.product_id
                quantity_change = 1 if maint_instance.status == 'Good' else -1
                update_inventory(product_name, quantity_change)
                if maint_instance.status == 'Failed':
                    Product.objects.filter(product_id=product_name).delete()
                form.save()
                return redirect('/page-list-maint')
    else:
        form = ReturnMaintForm(instance=maint_instance)
    context = {'form': form, 'maint_instance': maint_instance}
    return render(request, 'pages/return-maint.html', context)

def page_list_maint(request):
    context = {'maints': Maintenance.objects.all()}
    return render(request, 'pages/page-list-maint.html', context)

def page_delete_maint(request, id):
    maint = get_object_or_404(Maintenance, id=id)
    if request.method == 'POST':
        if maint.status in ['Good', 'Failed']:
            maint.delete()
        else:
            maint.delete()
            update_inventory(maint.product_id, 1)
        return redirect('/page-list-maint')
    return render(request, 'pages/page-delete-maint.html')

# ======================================= Reports Functions ==================================================

def page_product_report(request):
    context = {'productsreport': Product.objects.all()}
    return render(request, 'pages/page-product-report.html', context)

def page_inventory_report(request):
    context = {'inventoryreport': Inventory.objects.all()}
    return render(request, 'pages/page-inventory-report.html', context)

def search_for_device(request, id):
    product = get_object_or_404(Product, product_id=id)
    product_name = product.product_id
    filtered_result = Order.objects.filter(product_id=product_name).last()
    maint_devices = [product.product_id for product in Maintenance.objects.all()]

    if product_name in maint_devices:
        place = "This Device In Maintenance"
    elif filtered_result is None or filtered_result.state != "add":
        place = "This Device In Inventory"
    else:
        place = f"This Device In Party Has Code: {filtered_result.party_code}"

    context = {'place': place, 'product_name': product_name}
    return render(request, 'pages/search-for-device.html', context)

# ======================================= Users Functions ==================================================

def page_list_users(request):
    context = {'form': CustomUser.objects.all()}
    return render(request, 'pages/page-list-users.html', context)

# ======================================= Package Functions ==================================================

def page_add_package(request):
    if request.method == 'POST':
        form = PackageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/page-add-package')
        else:
            messages.warning(request, "This Pack Name Was Exist")
    context = {'packageform': PackageForm()}
    return render(request, 'pages/page-add-package.html', context)

def page_list_package(request):
    context = {'packageform': Package.objects.all()}
    return render(request, 'pages/page-list-package.html', context)

def page_update_package(request, id):
    package = get_object_or_404(Package, id=id)
    if request.method == 'POST':
        form = PackageForm(request.POST, instance=package)
        if form.is_valid():
            form.save()
            return redirect('/page-list-package')
    context = {'packform': PackageForm(instance=package)}
    return render(request, 'pages/page-update-package.html', context)


def delete_package(request, id):
    try:
        pack_delete = get_object_or_404(Package, id=id)
        if request.method == 'POST':
            pack_delete.delete()
            return redirect('/page-list-package')
    except ProtectedError:
        messages.warning(request, "Delete Orders Inside Party First")
    return render(request, 'pages/page-delete-package.html')

