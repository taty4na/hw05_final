from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    now = timezone.now().year
    return {'year': now}
