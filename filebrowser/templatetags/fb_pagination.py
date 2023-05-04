# coding: utf-8

from django.template import Library


register = Library()
DOT = '.'


@register.inclusion_tag('filebrowser/include/paginator.html', takes_context=True)
def pagination(context):
    page_num = context['page'].number - 1
    paginator = context['p']

    if not paginator.num_pages or paginator.num_pages == 1:
        page_range = []
    elif paginator.num_pages <= 10:
        page_range = range(paginator.num_pages)
    else:
        ON_EACH_SIDE = 3
        ON_ENDS = 2
        page_range = []
        if page_num > (ON_EACH_SIDE + ON_ENDS):
            page_range.extend(range(0, ON_EACH_SIDE - 1))
            page_range.append(DOT)
            page_range.extend(range(page_num - ON_EACH_SIDE, page_num + 1))
        else:
            page_range.extend(range(0, page_num + 1))
        if page_num < (paginator.num_pages - ON_EACH_SIDE - ON_ENDS - 1):
            page_range.extend(range(page_num + 1, page_num + ON_EACH_SIDE + 1))
            page_range.append(DOT)
            page_range.extend(range(paginator.num_pages - ON_ENDS, paginator.num_pages))
        else:
            page_range.extend(range(page_num + 1, paginator.num_pages))

    return {
        'page_range': page_range,
        'page_num': page_num,
        'filelisting': context['filelisting'],
        'query': context['query'],
    }
