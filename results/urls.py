from django.urls import path

from .views import ResultDetailView, ResultListCreateView

urlpatterns = [
    path("", ResultListCreateView.as_view(), name="results"),
    path("<int:pk>/", ResultDetailView.as_view(), name="result-detail"),
]
