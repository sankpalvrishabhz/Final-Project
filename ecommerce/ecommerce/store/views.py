from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import *
from .forms import CreateUserForm
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# Create your views here.

# def register_view(request):
#      form = UserCreationForm()
#      if request.method == 'POST':
#           form = UserCreationForm(request.POST)
#           if form.is_valid():
#                form.save()
#      context = {'form':form}
#      return render(request, 'store/register.html', context)

def register_view(request):
     if request.method == 'POST':
          form = CreateUserForm(request.POST)
          if form.is_valid():
               # login(request, form.save())
               # user = form.cleaned_data.get('username')
               # messages.success(request, "Account details updated for " + user)
               form.save()
               return redirect("store")
     else:
          form = CreateUserForm()
     context = {"form": form}
     return render(request, 'store/register.html',context)

def login_view(request):
     if request.method == 'POST':
          form = AuthenticationForm(data=request.POST)
          if form.is_valid():
               # login(request, form.get_user())
               form.get_user()
               return redirect("store")
     else:
          form = AuthenticationForm()
     context = {"form": form}
     return render(request, 'store/login.html',context)

# def login_view(request):
#      if request.method == 'POST':
#           username = request.POST.get('username')
#           password = request.POST.get('password')
#           user = authenticate(request, username=username, password=password)
#           if user is not None:
#                login(request, user)
#                return redirect('store')
#           else:
#                messages.info(request, 'Username  OR password is incorrect')
#                return render(request, 'store/login.html', context)

#      context = {}
#      return render(request, 'store/login.html', context)

def logout_view(request):
     if request.method == 'POST':
          logout(request)
          return redirect("store")
     
def store(request):
     # if request.user.is_authenticated:
     #      customer = request.user.customer
     #      order, created = Order.objects.get_or_create(customer=customer, complete=False)
     #      items = order.orderitem_set.all()
     #      cartItems = order.get_cart_items
     # else:
		#Create empty cart for now for non-logged in user
          # items = []
          # order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
          # cartItems = order['get_cart_items']
          # cookieData = cookieCart(request)
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
		# #Create empty cart for now for non-logged in user
          # try:
          #      cart = json.loads(request.COOKIES['cart'])
          # except:
          #      cart = {}
          #      print('CART:', cart)

          # items = []
          # order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
          # cartItems = order['get_cart_items']

          # for i in cart:
          #      try:
          #           cartItems += cart[i]['quantity']
          #           product = Product.objects.get(id=i)
          #           total = (product.price * cart[i]['quantity'])
          #           order['get_cart_total'] += total
          #           order['get_cart_items'] += cart[i]['quantity']

          #           item = {
          #                'id':product.id,
          #                'product':{'id':product.id,'name':product.name, 'price':product.price, 
          #                'imageURL':product.imageURL}, 'quantity':cart[i]['quantity'],
          #                'digital':product.digital,'get_total':total,
          #                }
          #           items.append(item)

          #           if product.digital == False:
          #                order['shipping'] = True
          #      except:
          #           pass
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
		# #Create empty cart for now for non-logged in user
          # items = []
          # order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
          # cartItems = order['get_cart_items']
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

     customer = request.user.customer
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
          customer = request.user.customer
          order, created = Order.objects.get_or_create(customer=customer, complete=False)
     else:
          # print('User is not logged in')

          # print('COOKIES:', request.COOKIES)
          # name = data['form']['name']
          # email = data['form']['email']
          # cookieData = cookieCart(request)
          # items = cookieData['items']
          # customer, created = Customer.objects.get_or_create(
		# 	email=email,
		# )
          # customer.name = name
          # customer.save()
          # order = Order.objects.create(
		# 	customer=customer,
		# 	complete=False,
		# )

          # for item in items:
          #      product = Product.objects.get(id=item['id'])
          #      orderItem = OrderItem.objects.create(
          #           product=product,
          #           order=order,
          #           quantity=item['quantity'],
          #      )
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
