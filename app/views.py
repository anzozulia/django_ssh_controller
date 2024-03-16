from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, FormView, CreateView, UpdateView, DeleteView

from .forms import LoginForm, ServerForm, ServerSettingsForm, AlertSettingsForm, SettingsForm
from .models import Server, AlertSettings, Settings
from .scheduler import check_server


class Login(LoginView):
    form_class = LoginForm
    template_name = 'login.html'


def dashboard(request):
    context = {
        'servers': Server.objects.all().order_by('hostname'),
    }
    return render(request, 'dashboard.html', context)


def server_inspect(request, pk):
    context = {
        'server': Server.objects.get(pk=pk),
        'alerts': AlertSettings.objects.filter(server=pk).order_by('type', 'metric'),
    }
    return render(request, 'server.html', context)


class ServerCreateView(CreateView):
    template_name = 'create_server.html'
    form_class = ServerForm
    model = Server

    def get_success_url(self):
        return reverse('app:dashboard')

    def form_valid(self, form):
        server = form.save()
        for alert in AlertSettings.objects.filter(server__isnull=True):
            alert.pk = None
            alert.server = server
            alert.save()
            check_server(server)
        return super().form_valid(form)
    

class ServerSettingsView(UpdateView):
    template_name = 'server_settings.html'
    form_class = ServerSettingsForm
    model = Server

    def get_initial(self):
        initial = super().get_initial()
        initial['ssh_key'] = None
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['server'] = self.object
        return context

    def get_success_url(self):
        return reverse('app:server_inspect', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        instance = form.instance

        for field in form.fields:
            if field in form.cleaned_data:
                if form.cleaned_data[field]:
                    if field == 'ssh_key':
                        ssh_key_file = form.cleaned_data[field]
                        instance.ssh_key.save(ssh_key_file.name, ssh_key_file)
                    else:
                        setattr(instance, field, form.cleaned_data[field])

        instance.save()
        return super().form_valid(form)
    
    
def delete_server(request, pk):
    Server.objects.filter(pk=pk).delete()
    return redirect('app:dashboard')


def delete_alert(request):
    AlertSettings.objects.filter(pk=request.POST.get('pk')).delete()
    return HttpResponse('!')


def server_switch(request, pk):
    Server.objects.filter(pk=pk).update(active=request.POST.get('server_active') == 'true')
    return HttpResponse('ok')   


class AlertSettingsCreateView(CreateView):
    template_name = 'create_alert_setting.html'
    form_class = AlertSettingsForm
    model = AlertSettings

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        server_pk = self.kwargs['server_pk']
        if server_pk != 0:
            server = get_object_or_404(Server, pk=server_pk)
            form.fields['server'].initial = server
            context['server'] = get_object_or_404(Server, pk=server_pk)
        return super().get_context_data(**context)

    def get_success_url(self):
        server_pk = self.kwargs['server_pk']
        if server_pk != 0:
            return reverse('app:server_inspect', kwargs={'pk': self.kwargs['server_pk']})
        else:
            return reverse('app:settings')
    

class SettingsView(UpdateView):
    template_name = 'settings.html'
    form_class = SettingsForm
    model = Settings
    
    def get_object(self, queryset=None):
        return Settings.load()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alerts'] = AlertSettings.objects.filter(server__isnull=True).order_by('type', 'metric')
        return context

    def get_success_url(self):
        return reverse('app:settings')