from django.conf.urls import url
from . import views

urlpatterns = [
    url('^payment/(?P<order_id>\d+)/$', views.PayUrlView.as_view()),
    url('^payment/status/$', views.OrderStatusView.as_view()),
]
