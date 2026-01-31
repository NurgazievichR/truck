from django.shortcuts import render, get_object_or_404
from .models import Page, Advantage, Contact


def index(request):
    """Главная страница"""
    advantages = Advantage.objects.filter(is_active=True).order_by('order')
    return render(request, 'main/index.html', {
        'advantages': advantages
    })


def page_detail(request, slug):
    """Детальная страница (О компании, Как мы работаем)"""
    page = get_object_or_404(Page, slug=slug, is_published=True)
    return render(request, 'main/page_detail.html', {
        'page': page
    })


def about(request):
    """Страница О компании"""
    return page_detail(request, 'about')


def how_we_work(request):
    """Страница Как мы работаем"""
    return page_detail(request, 'how-we-work')


def advantages(request):
    """Страница Преимущества компании"""
    advantages_list = Advantage.objects.filter(is_active=True).order_by('order')
    return render(request, 'main/advantages.html', {
        'advantages': advantages_list
    })


def contacts(request):
    """Страница Контакты"""
    contact_list = Contact.objects.filter(is_active=True).order_by('order')
    return render(request, 'main/contacts.html', {
        'contacts': contact_list
    })
