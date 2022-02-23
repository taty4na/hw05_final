from http import HTTPStatus

from django.shortcuts import render

# Саид, хотела исправить, но pytest пишет ошибку:
# FAILED tests/test_homework.py::TestCustomErrorPages::test_custom_404
# AssertionError: Убедитесь, что для несуществующих адресов страниц,
# сервер возвращает код 404. assert 200 == 404
#
# def page_not_found(request, exception):
#     return render(
#         request,
#         'core/404.html',
#         {'path': request.path},
#         HTTPStatus.NOT_FOUND
#     )


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'core/500.html', HTTPStatus.INTERNAL_SERVER_ERROR)


def permission_denied(request, exception):
    return render(request, 'core/403.html', HTTPStatus.FORBIDDEN)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')
