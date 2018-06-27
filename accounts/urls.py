from django.conf.urls import url, include
from .views import Register, activate

urlpatterns = [
    url(r'^register$', Register.as_view(), name='register'),  # 注册
    url(r'^activate/(?P<activate_key>\w+)$', activate, name='activate'),  # 激活
]