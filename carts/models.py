from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
from decimal import Decimal
from django.db.models.signals import post_save,post_delete


from products.models import Variation

class CartItem(models.Model):
	cart = models.ForeignKey("Cart")
	item = models.ForeignKey(Variation)
	quantity = models.PositiveIntegerField(default=1)
	line_item_total = models.DecimalField(max_digits=10,decimal_places=2)

	def __str__(self):
		return self.item.title

	def remove(self):
		return self.item.remove_from_cart()

	def get_title(self):
		return "%s - %s" %(self.item.product.title,self.item.title)

def cart_item_pre_save_receiver(sender,instance,*args,**kwargs):
	qty = instance.quantity
	if int(qty) >= 1:
		price = instance.item.get_price()
		line_item_total = Decimal(price) * Decimal(qty)
		instance.line_item_total = line_item_total	
	

pre_save.connect(cart_item_pre_save_receiver,sender=CartItem)

def post_save_signal_in_cartitem(sender,instance,*args,**kwargs):
	instance.cart.update_subtotal()

post_save.connect(post_save_signal_in_cartitem,sender=CartItem)
post_delete.connect(post_save_signal_in_cartitem,sender=CartItem)

class Cart(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True)
	items = models.ManyToManyField(Variation,through=CartItem)
	timestamp = models.DateTimeField(auto_now_add=True,auto_now=False)
	updated = models.DateTimeField(auto_now_add=False,auto_now=True)
	subtotal = models.DecimalField(max_digits=50,decimal_places=3,default=25.0)
	tax_total = models.DecimalField(max_digits=50,decimal_places=2,default=25.0)
	total = models.DecimalField(max_digits=50,decimal_places=2,default=25.0)
	tax_percentage = models.DecimalField(max_digits=10,decimal_places=2,default=0.035)

	def __str__(self):
		return str(self.id)

	def update_subtotal(self):
		subtotal = 0;
		for item in self.cartitem_set.all():
			subtotal += item.line_item_total
		self.subtotal = "%0.2f" %(subtotal)
		self.save()

def do_tax_and_total_receiver(sender,instance,*args,**kwargs):
	subtotal = Decimal(instance.subtotal)
	tax_total = round(subtotal * Decimal(instance.tax_percentage))
	total = round(subtotal + Decimal(tax_total))
	instance.tax_total = "%.2f" %(tax_total)
	instance.total = "%.2f" %(total)

pre_save.connect(do_tax_and_total_receiver,sender=Cart)


