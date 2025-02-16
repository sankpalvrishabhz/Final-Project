from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth import login
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.

def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after registration
            return redirect('store')  # Redirect to the home page
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')  # Redirect to homepage or dashboard
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'store/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    return render(request, 'store/product_detail.html', {'product': product,'cartItems':cartItems})

def store(request):
     # if request.user.is_authenticated:
     #      customer = request.user.customer
     #      order, created = Order.objects.get_or_create(customer=customer, complete=False)
     #      items = order.orderitem_set.all()
     #      cartItems = order.get_cart_items
     # else:
	# 	# Create empty cart for now for non-logged in user
     #      items = []
     #      order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
     #      cartItems = order['get_cart_items']
     #      cookieData = cookieCart(request)
     data = cartData(request)
     cartItems = data['cartItems']
     order = data['order']
     items = data['items']

     products = Product.objects.all()
     context = {'products':products, 'cartItems':cartItems}
     return render(request, 'store/store.html', context)

def cart(request):
     # if request.user.is_authenticated:
     #      customer = request.user.customer
     #      order, created = Order.objects.get_or_create(customer=customer, complete=False)
     #      items = order.orderitem_set.all()
     #      cartItems = order.get_cart_items

     # else:
	# 	#Create empty cart for now for non-logged in user
     #      try:
     #           cart = json.loads(request.COOKIES['cart'])
     #      except:
     #           cart = {}
     #           print('CART:', cart)

     #      items = []
     #      order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
     #      cartItems = order['get_cart_items']

     #      for i in cart:
     #           try:
     #                cartItems += cart[i]['quantity']
     #                product = Product.objects.get(id=i)
     #                total = (product.price * cart[i]['quantity'])
     #                order['get_cart_total'] += total
     #                order['get_cart_items'] += cart[i]['quantity']

     #                item = {
     #                     'id':product.id,
     #                     'product':{'id':product.id,'name':product.name, 'price':product.price, 
     #                     'imageURL':product.imageURL}, 'quantity':cart[i]['quantity'],
     #                     'digital':product.digital,'get_total':total,
     #                     }
     #                items.append(item)

     #                if product.digital == False:
     #                     order['shipping'] = True
     #           except:
     #                pass
     data = cartData(request)
     cartItems = data['cartItems']
     order = data['order']
     items = data['items']

     context = {'items':items, 'order':order, 'cartItems':cartItems}
     return render(request, 'store/cart.html', context)

def checkout(request):
     # if request.user.is_authenticated:
     #      customer = request.user.customer
     #      order, created = Order.objects.get_or_create(customer=customer, complete=False)
     #      items = order.orderitem_set.all()
     #      cartItems = order.get_cart_items

     # else:
	# 	#Create empty cart for now for non-logged in user
     #      items = []
     #      order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
     #      cartItems = order['get_cart_items']
     data = cartData(request)     
     cartItems = data['cartItems']
     order = data['order']
     items = data['items']

     context = {'items':items, 'order':order, 'cartItems':cartItems}
     return render(request, 'store/checkout.html', context)

def updateItem(request):
     data = json.loads(request.body)
     productId = data['productId']
     action = data['action']
     print('Action:', action)
     print('Product:', productId)
     if hasattr(request.user, 'customer'):
          customer = request.user.customer
     else:
          customer = None  # Handle case where customer does not exist
     product = Product.objects.get(id=productId)
     order, created = Order.objects.get_or_create(customer=customer, complete=False)

     orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

     if action == 'add':
          orderItem.quantity = (orderItem.quantity + 1)
     elif action == 'remove':
          orderItem.quantity = (orderItem.quantity - 1)

     orderItem.save()

     if orderItem.quantity <= 0:
          orderItem.delete()

     return JsonResponse('Item was added', safe=False)

def processOrder(request):
     transaction_id = datetime.datetime.now().timestamp()
     data = json.loads(request.body)

     if request.user.is_authenticated:
          if hasattr(request.user, 'customer'):
               customer = request.user.customer
          else:
               customer = None
          order, created = Order.objects.get_or_create(customer=customer, complete=False)
     else:
          customer, order = guestOrder(request, data)

     total = float(data['form']['total'])
     order.transaction_id = transaction_id
     if total == order.get_cart_total:
          order.complete = True
     order.save()
     if order.shipping == True:
          ShippingAddress.objects.create(
               customer=customer,
               order=order,
               address=data['shipping']['address'],
               city=data['shipping']['city'],
               state=data['shipping']['state'],
               zipcode=data['shipping']['zipcode'],
          )

     return JsonResponse('Payment submitted..', safe=False)

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to profile page after saving
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'store/profile.html', {'form': form})
