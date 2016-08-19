from django.shortcuts import render,redirect,Http404
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .forms import AddressForm,UserAddressForm
from .models import UserAddress,UserCheckout,Order
from .mixins import CartOrderMixin,LoginRequiredMixins


class OrderDetail(DetailView):
	model = Order

	def dispatch(self,request,*args,**kwargs):
		try:
			user_check_id = self.request.session.get("user_checkout_id")
			user_checkout = UserCheckout.objects.get(id=user_check_id)
		except UserCheckout.DoesNotExist:
			user_checkout = UserCheckout.objects.get(user=request.user)
		except:
			user_checkout = None

		obj = self.get_object()
		if obj.user == user_checkout and user_checkout is not None:
			return super(OrderDetail,self).dispatch(request,*args,**kwargs)
		else:
			raise Http404

class OrderList(LoginRequiredMixins,ListView):
	queryset = Order.objects.all()

	def get_queryset(self):
		user_check_id = self.request.session.get("user_checkout_id")
		user_checkout = UserCheckout.objects.get(id=user_check_id)

		return super(OrderList,self).get_queryset().filter(user=user_checkout)

class AddressSelectFormView(CartOrderMixin,FormView):
	form_class = AddressForm
	template_name = 'orders/address_select.html'

	def dispatch(self,*args,**kwargs):
		b_address,s_address = self.get_addresses()

		if b_address.count() == 0:
			messages.success(self.request,"Please Add a billing Addresss")
			return redirect("add_address")
		elif s_address.count() == 0:
			messages.success(self.request,"Please Add a Shipping Addresss")
			return redirect("add_address")
		else:
			return super(AddressSelectFormView,self).dispatch(*args,**kwargs)

	def get_addresses(self):
		user_check_id = self.request.session.get("user_checkout_id")
		user = UserCheckout.objects.get(id=user_check_id)

		b_address = UserAddress.objects.filter(
			user=user,
			type='billing',
		)

		s_address = UserAddress.objects.filter(
			user=user,
			type='billing',
		)

		return b_address,s_address

	def get_form(self,*args,**kwargs):
		form = super(AddressSelectFormView,self).get_form(*args,**kwargs)
		b_address,s_address = self.get_addresses()

		form.fields["billing"].queryset = b_address
		form.fields["shipping"].queryset = s_address

		return form

	def form_valid(self,form,*args,**kwargs):
		billing_address = form.cleaned_data['billing']
		shipping_address = form.cleaned_data['shipping']

		order = self.get_order()
		order.billing_address = billing_address
		order.shipping_address = shipping_address
		order.save()		
		return super(AddressSelectFormView,self).form_valid(form,*args,**kwargs)

	def get_success_url(self,*args,**kwargs):
		return reverse("checkout")

class UserAddressCreateView(CreateView):
	form_class = UserAddressForm
	template_name = 'forms.html'
	success_url = '/checkout/address'

	def get_checkout_user(self):
		user_check_id = self.request.session.get("user_checkout_id")
		user_checkout = UserCheckout.objects.get(id=user_check_id)
		return user_checkout

	def form_valid(self,form,*args,**kwargs):
		form.instance.user = self.get_checkout_user()
		return super(UserAddressCreateView,self).form_valid(form,*args,**kwargs)
