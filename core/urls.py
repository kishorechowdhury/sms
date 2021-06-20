from django.urls import path
from django.views.generic import RedirectView

from .views import dashboard, UserCreate, ProjectCreate, ProjectMemberCreate, TicketCreate, project_detail, delete_ticket, update_ticket_status

app_name = 'core'

urlpatterns = [
    path('', RedirectView.as_view(url='dashboard/')),
    path('dashboard/', dashboard, name='dashboard'),
]

urlpatterns += [
    path('user/create/', UserCreate, name='user-create'),
]

urlpatterns += [
    path('project/create/', ProjectCreate.as_view(), name='project-create'),
    path('projectmember/create/', ProjectMemberCreate.as_view(), name='projectmember-create'),
    path('ticket/create/', TicketCreate.as_view(), name='ticket-create'),
    path('project/<int:pk>', project_detail, name='project-detail'),
    path('ticket/<str:pk>/delete', delete_ticket, name='ticket-delete'),
    path('ticket/<str:pk>/update-status', update_ticket_status, name='ticket-update-status'),
]