from django.conf.urls import url

from carts import views

urlpatterns = [
    url('^cart/$', views.CartView.as_view()),
    url('^cart/selection/$', views.CartSelectAllView.as_view()),
]