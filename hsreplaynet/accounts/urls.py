from django.conf.urls import url
from django.views.generic import TemplateView
from .views import ClaimAccountView, DeleteAccountView


urlpatterns = [
	url(r"^$", TemplateView.as_view(template_name="account/edit.html"), name="account_edit"),
	url(r"^claim/(?P<id>[\w-]+)/$", ClaimAccountView.as_view(), name="account_claim"),
	url(r"^delete/$", DeleteAccountView.as_view(), name="account_delete"),
]
