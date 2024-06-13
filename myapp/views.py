from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Post

def post_list(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 20)  # 한 페이지에 20개씩
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 페이지 번호 10개씩 그룹화
    current_page = page_obj.number
    start_index = (current_page - 1) // 10 * 10
    end_index = start_index + 10
    page_numbers = list(paginator.page_range)[start_index:end_index]

    return render(request, 'post_list.html', {
        'page_obj': page_obj,
        'page_numbers': page_numbers
    })
