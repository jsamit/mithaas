from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.utils.safestring import mark_safe

class ProductQuerySet(models.query.QuerySet):
	def active(self):
		return self.filter(active=True)

class ProductModelManager(models.Manager):
	def get_queryset(self):
		return ProductQuerySet(self.model,using=self._db)

	def all(self,*args,**kwargs):
		return self.get_queryset().active()

	def get_related(self,instance):
		product_1 = self.get_queryset().filter(category__in=instance.category.all())
		product_2 = self.get_queryset().filter(default=instance.default)
		qs = (product_1 | product_2).exclude(id=instance.id).distinct()
		return qs

class Product(models.Model):
	title = models.CharField(max_length=120)
	description = models.TextField(null=True,blank=True)
	price = models.DecimalField(decimal_places=2,max_digits=20)
	active = models.BooleanField(default=True)

	category = models.ManyToManyField("Category")
	default = models.ForeignKey("Category",related_name="default_category",null=True,blank=True)

	objects = ProductModelManager()
	def __str__(self):
		return self.title

	class Meta:
		ordering = ["-title"]

	@property
	def get_absolute_url(self):
		return reverse("product_detail",kwargs={"pk" : self.pk})

	def get_image_url(self):
		img = self.productimages_set.first()
		if img:
			return img.image.url
		return img #None

class Variation(models.Model):
	product = models.ForeignKey(Product)
	title = models.CharField(max_length=120)
	price = models.DecimalField(decimal_places=2,max_digits=20)
	sale_price = models.DecimalField(decimal_places=2,max_digits=20,null=True,blank=True)
	active = models.BooleanField(default=True)
	inventory = models.IntegerField(null=True,blank=True)

	def __str__(self):
		return self.title

	def get_price(self):
		if self.sale_price is not None:
			return self.sale_price
		else:
			return self.price

	def get_html_price(self):
		if self.sale_price is not None:
			html_text = "<span class='sale-price'>%s</span> <span class='og-price'>%s</span>" %(self.sale_price, self.price)
		else:
			html_text = "<span class='price'>%s</span>" %(self.price)
		return mark_safe(html_text)

	def get_absolute_url(self):
		return self.Product.get_absolute_url()

	def add_to_cart(self):
		return "%s?item=%s&qty=1" %(reverse("cart"),self.id)

	def get_title(self):
		return "%s - %s" %(self.product.title, self.title)

	def remove_from_cart(self):
		return "%s?item=%s&qty=1&delete=True" %(reverse("cart"),self.id)

def product_post_save_receiver(sender,instance,created,*args,**kwargs):
	product = instance
	variation = product.variation_set.count()

	if variation == 0:
		new_var = Variation()
		new_var.title = "Default"
		new_var.product = product
		new_var.price = product.price
		new_var.save()

post_save.connect(product_post_save_receiver,sender=Product)

def image_upload_to(instance,filename):
	title = instance.product.title
	slug = slugify(title)
	return 'product/%s/%s' %(slug,filename)

class ProductImages(models.Model):
	product = models.ForeignKey(Product)
	image = models.ImageField(upload_to=image_upload_to)

	def __str__(self):
		return self.product.title

class Category(models.Model):
	title = models.CharField(max_length=120,unique=True)
	slug = models.SlugField(unique=True)
	description = models.TextField(null=True,blank=True)
	active = models.BooleanField(default=True)
	timestamp = models.DateTimeField(auto_now_add=True,auto_now=False)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("category_detail",kwargs={"slug": self.slug})

def image_upload_to_featured(instance, filename):
	title = instance.product.title
	slug = slugify(title)
	basename, file_extension = filename.split(".")
	new_filename = "%s-%s.%s" %(slug, instance.id, file_extension)
	return "products/%s/featured/%s" %(slug, new_filename)

class ProductFeatured(models.Model):
	product = models.ForeignKey(Product)
	image = models.ImageField(upload_to=image_upload_to_featured)
	title = models.CharField(max_length=120, null=True, blank=True)
	text = models.CharField(max_length=220, null=True, blank=True)
	text_right = models.BooleanField(default=False)
	text_css_color = models.CharField(max_length=6, null=True, blank=True)
	show_price = models.BooleanField(default=False)
	make_image_background = models.BooleanField(default=False)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.product.title
