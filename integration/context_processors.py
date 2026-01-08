from .models import ApplicationConfiguration

def flow_configs(request):
    if request.user.is_authenticated:
        configs = ApplicationConfiguration.objects.filter(flow_ai=True)
        return {
            'flow_configs': configs,
            'flow_configs_count': configs.count()
        }
    return {}
