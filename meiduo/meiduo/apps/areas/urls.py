from rest_framework.routers import DefaultRouter

from areas import views

urlpatterns = [

]

router = DefaultRouter()
router.register(r'areas', views.AreasViewSet, base_name='areas')
urlpatterns += router.urls
