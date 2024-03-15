from .models import Server

def servers(request):
    return {'servers': Server.objects.all().order_by('hostname')}