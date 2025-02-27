from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200)

	def __str__(self):
		return str(self.name)

# class Product(models.Model):
#     name = models.CharField(max_length=200)
#     # description = models.TextField()
#     price = models.FloatField()
#     digital = models.BooleanField(default=False,null=True, blank=True)
#     image = models.ImageField(null=True, blank=True)

#     def __str__(self):
#         return self.name
	
#     @property
#     def imageURL(self):
#         try:
#             url = self.image.url
#         except:
#             url = ''
#         return url

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="No description available.")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    digital = models.BooleanField(default=False,null=True, blank=True)
    # image = models.ImageField(upload_to='static/images/', null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    def __str__(self):
        return self.name

class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)

	def __str__(self):
		return str(self.id)
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping
	
	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 

# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     product_name = models.CharField(max_length=200)
#     order_date = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')])

#     def __str__(self):
#         return f"{self.product_name} - {self.user.username}"
    
class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total

class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles', blank=True, null=True)
    # address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
