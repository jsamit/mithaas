from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.http import Http404

class StaffRequiredMixins(object):
	@classmethod
	def as_view(self,*args,**kwargs):
		view = super(StaffRequiredMixins,self).as_view(*args,**kwargs)
		# return login_required(view)
		return login_required(view)

	# @method_decorator(login_required)
	@method_decorator(login_required)
	def dispatch(self,request,*args,**kwargs):
		if request.user.is_staff:
			return super(StaffRequiredMixins,self).dispatch(request,*args,**kwargs)
		else:
			raise Http404

class LoginRequiredMixins(object):
	@classmethod
	def as_view(self,*args,**kwargs):
		view = super(LoginRequiredMixins,self).as_view(*args,**kwargs)
		return login_required(view)

	@method_decorator(login_required)
	def dispatch(self,request,*args,**kwargs):
		return super(LoginRequiredMixins,self).dispatch(request,*args,**kwargs)
