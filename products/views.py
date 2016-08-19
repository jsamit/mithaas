import random
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models import Q
from django.contrib import messages
from django.http import Http404

from .models import Product,Variation,Category
from .forms import VariationInventoryFormSet
from .mixins import StaffRequiredMixins

class CategoryListView(ListView):
	model = Category
	queryset = Category.objects.all()
	template_name = 'products/product_list.html'

class CategoryDetailView(DetailView):
	model =  Category

	def get_context_data(self,*args,**kwargs):
		context = super(CategoryDetailView,self).get_context_data(*args,**kwargs)
		obj = self.get_object()
		product_set = obj.product_set.all()
		default_set = obj.default_category.all()

		products = (product_set | default_set).distinct()
		context["products"] = products
		return context


class VariationListView(StaffRequiredMixins,ListView):
	model = Variation
	queryset = Variation.objects.all()

	def get_context_data(self,*args,**kwargs):
		context = super(VariationListView,self).get_context_data(*args,**kwargs)
		context['formset'] = VariationInventoryFormSet(queryset=self.get_queryset())
		return context

	def get_queryset(self,*args,**kwargs):
		product_pk = self.kwargs.get("pk")

		if product_pk:
			product = get_object_or_404(Product,pk=product_pk)
			queryset = Variation.objects.filter(product=product)
		return queryset

	def post(self,request,*args,**kwargs):
		formset = VariationInventoryFormSet(request.POST)
		if formset.is_valid():
			formset.save(commit=False)
			for form in formset:
				new_item = form.save(commit=False)
				if new_item.title:
					product_pk =self.kwargs.get("pk")
					product = get_object_or_404(Product,pk=product_pk)
					new_item.product = product
					new_item.save()
			messages.success(request,"Your inventory has been updates!")		
			return redirect("product_list")
		raise Http404

class ProductDetailView(DetailView):
	model = Product

	def get_context_data(self, *args, **kwargs):
		context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
		instance = self.get_object()
		context["related"] = Product.objects.get_related(instance)
		return context

class ProductListView(ListView):
	model = Product

	def get_context_data(self,*args,**kwargs):
		context = super(ProductListView,self).get_context_data(*args,**kwargs)
		return context

	def get_queryset(self,*args,**kwargs):
		qs = super(ProductListView,self).get_queryset(*args,**kwargs)
		query = self.request.GET.get("q")
		if query:
			qs = self.model.objects.filter(
				Q(title__icontains=query) |
				Q(description__icontains=query)
				)
			try:
				qs2 = self.model.objects.filter(
					Q(price=query) |
					Q(description__icontains=query)	
					)
				qs = (qs | qs2).distinct()
			except:
				pass
		return qs


