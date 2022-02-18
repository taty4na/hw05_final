from django.core.paginator import Paginator

POSTS_SOW = 10


def paginator_obj(request, objects):
    paginator = Paginator(objects, POSTS_SOW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
