import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.generic import detail
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy

from .models import Project, ProjectMember, Ticket
from .utils import log_action, get_profile, get_user_permissions
from .forms import TicketStatusForm


@login_required
def dashboard(request):
    projects = Project.objects.raw(f"SELECT id, name FROM core_project WHERE id IN(SELECT project_id FROM core_projectmember WHERE user_id={request.user.id})")
    btn_choices = ('primary','success','info', 'warning', 'secondary', 'danger', 'dark')
    page_heading = 'Dashboard' if request.GET.get('p') is None else 'My Projects'
    permissions = get_user_permissions(request.user)
    context = {
        'profile': get_profile(request.user.id),
        'projects': projects,
        'btn_choices': btn_choices,
        'permissions': permissions,
        'page_heading': page_heading,
    }
    if 'core.can_mark_working' in permissions:
        template = 'core/dashboard2.html'
        context['tickets'] = Ticket.objects.select_related('user', 'project').filter(user=request.user.id)
    else:
        template = 'core/dashboard.html'
    return render(request, template, context)


@login_required
@permission_required('auth.add_user', raise_exception=True)
def UserCreate(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            log_action(request.user.id, message=f'Add user. Username: {request.POST.get("username")}')
            return HttpResponseRedirect(reverse('core:user-create'))            
        else:
            messages.error(request, 'Account creation failed')
    else:
        f = UserCreationForm()
    context = {
        'profile': get_profile(request.user.id),
        'form': f,
        'permissions': get_user_permissions(request.user)
    }
    return render(request, 'core/user-register.html', context)


class ProjectCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'core.add_project'
    raise_exception = True
    model = Project
    fields = '__all__'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            super().form_valid(form)
            #log action
            log_action(request.user.id, message=f'Add project. Project: {self.object.name}')
            #add member association
            pm = ProjectMember(project=self.object, user=request.user)
            pm.save()
            messages.success(request, 'Project created successfully')            
        else:
            messages.error(request, 'Project creation failed')
        return HttpResponseRedirect(reverse('core:project-create'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_profile(self.request.user.id)
        context['permissions'] = get_user_permissions(self.request.user)
        return context


class ProjectMemberCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'core.add_projectmember'
    raise_exception = True
    model = ProjectMember
    fields = '__all__'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            super().form_valid(form)
            #log action
            log_action(request.user.id, message=f'Add project member. Project: {self.object.project}, User: {self.object.user}')
            messages.success(request, 'Add project member success')            
        else:
            messages.error(request, form.errors)
        return HttpResponseRedirect(reverse('core:projectmember-create'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_profile(self.request.user.id)
        context['permissions'] = get_user_permissions(self.request.user)
        return context


class TicketCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'core.add_ticket'
    raise_exception = True
    model = Ticket
    fields = ['id', 'project', 'user', 'details']

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            super().form_valid(form)
            #log action
            log_action(request.user.id, message=f'Add ticket. Project: {self.object.project}, User: {self.object.user}')
            messages.success(request, 'Add ticket success')
        else:
            messages.error(request, form.errors)
        return HttpResponseRedirect(reverse('core:ticket-create'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_profile(self.request.user.id)
        context['permissions'] = get_user_permissions(self.request.user)
        return context


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    members = ProjectMember.objects.raw(f"SELECT id, username, first_name, last_name FROM auth_user WHERE id IN(SELECT user_id FROM core_projectmember WHERE project_id={pk})")
    tickets = Ticket.objects.select_related('user', 'project').filter(project=pk)
    expired = project.end_date < datetime.date.today() and project.status != 'c'
    context = {
        'profile': get_profile(request.user.id),
        'project': project,
        'permissions': get_user_permissions(request.user),
        'expired': expired,
        'members': members,
        'tickets': tickets
    }    
    return render(request, 'core/project-detail.html', context)


@login_required
@permission_required('core.delete_ticket', raise_exception=True)
def delete_ticket(request, pk):
    object = get_object_or_404(Ticket, pk=pk)
    
    if request.method =="POST":
        redirect = request.POST.get('redirect_to')
        #log action
        log_action(request.user.id, message=f'Delete ticket. Project: {object.project},  User: {object.user}, Ticket: {object.id}')
        object.delete()
        return HttpResponseRedirect(redirect)

    context = {
        'profile': get_profile(request.user.id),
        'permissions': get_user_permissions(request.user),
        'redirect_url': request.META.get('HTTP_REFERER')
    }
    return render(request, "core/ticket_delete.html", context)


@login_required
@permission_required('core.can_mark_complete', raise_exception=True)
def update_ticket_status(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method =="POST":
        ticket.status = request.POST['status']
        ticket.save()
    return HttpResponseRedirect(request.POST['redirect_to'])


@login_required
@permission_required('core.can_mark_working', raise_exception=True)
def update_ticket_status(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method =="POST":
        project = Project.objects.get(id=ticket.project.id)
        project.status = request.POST['status']
        project.save()

        ticket.status = request.POST['status']
        ticket.save()
    return HttpResponseRedirect(request.POST['redirect_to'])