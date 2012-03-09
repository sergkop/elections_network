# -*- coding:utf-8 -*-
import cookielib
from random import choice
import urllib2

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect

import bleach
from uni_form.helper import FormHelper
from uni_form.layout import Submit

def form_helper(action_name, button_name):
    """ Shortcut to generate django-uniform helper """
    helper = FormHelper()
    helper.form_action = action_name
    helper.form_method = 'POST'
    helper.add_input(Submit('', button_name, css_class='ui-button ui-state-default'))
    return helper

def authenticated_redirect(view_name):
    """ Decorator for views which redirects to a given view if user is authenticated """
    def view_decorator(view):
        def new_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                return redirect(view_name)
            return view(request, *args, **kwargs)
        return new_view

    return view_decorator

def cache_function(key, timeout):
    def decorator(func):
        def new_func(*args, **kwargs):
            res = cache.get(key)
            if res:
                return res

            res = func(*args, **kwargs)
            cache.set(key, res, timeout)
            return res

        return new_func

    return decorator

# TODO: cache html only
def cache_view(key, timeout, only_anonym=True):
    def decorator(func):
        def new_func(request, *args, **kwargs):
            if (only_anonym and not request.user.is_authenticated()) or not only_anonym:
                res = cache.get(key)
                if res:
                    return res

                res = func(request, *args, **kwargs)
                cache.set(key, res, timeout)
            else:
                res = func(request, *args, **kwargs)

            return res

        return new_func

    return decorator

def clean_html(html):
    """ Clean html fields edited by tinymce """
    tags = ['a', 'address', 'b', 'big', 'br', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 
                'ol', 'p', 'pre', 's', 'span', 'strike', 'strong', 'sub', 'sup', 'u', 'ul']

    attributes = ['align', 'alt', 'border', 'class', 'dir', 'data', 'height', 'href', 'id', 'lang', 'longdesc', 'media', 'multiple',
                'nowrap', 'rel', 'rev', 'span', 'src', 'style', 'target', 'title', 'type', 'valign', 'vspace', 'width']

    styles = ['text-decoration', 'font-size', 'font-family', 'text-align', 'padding-left', 'color', 'background-color', ]
    return bleach.clean(html, tags=tags, attributes=attributes, styles=styles, strip=True)

def ajaxize(form):
    if form.is_valid():
        return HttpResponse(u'ok')
    else:
        errorstr = []
        for fieldname, errorlist in form.errors.items():
            fielderror = u''
            if fieldname in form.fields and form.fields[fieldname].label:
                fielderror += u'%s: ' % form.fields[fieldname].label
            fielderror += u', '.join(errorlist)
            errorstr.append(fielderror)
        errorstr = u'; '.join(errorstr)
        return HttpResponse(errorstr)

USER_AGENTS = [
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.5) Gecko/20091114 Gentoo Firefox/3.5.5',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.0',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729)',
    'Opera/9.62 (Windows NT 6.0; U; en) Presto/2.1.1',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3',
]

def read_url(url, encoding='windows-1251'):
    """ Set encoding=None to skip decoding """
    #print url
    proxy_handler = urllib2.ProxyHandler()
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(proxy_handler, urllib2.HTTPCookieProcessor(cj))
    request = urllib2.Request(url, headers={'User-Agent': choice(USER_AGENTS)})
    try:
        data = opener.open(request).read()
        if encoding:
            data = data.decode('windows-1251')
        return data
    except urllib2.URLError, e:
        raise e
        return ''
