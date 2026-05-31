from django.urls import path

from .views import AllResultsView, ResultDetailView, ResultListCreateView

urlpatterns = [
    path("", ResultListCreateView.as_view(), name="results"),
    path("all/", AllResultsView.as_view(), name="all-results"),
    path("<int:pk>/", ResultDetailView.as_view(), name="result-detail"),
]
