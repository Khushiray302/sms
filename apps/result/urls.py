from django.urls import path

from .views import ResultListView, create_result, edit_results, PrintResultView 

urlpatterns = [
    path("create/", create_result, name="create-result"),
    path("edit-results/", edit_results, name="edit-results"),
    path("view/all", ResultListView.as_view(), name="view-results"),
    
    path('results/print/', PrintResultView.as_view(), name='print_results'),

]
