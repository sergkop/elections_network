# -*- coding:utf-8 -*-
from .forms import MessageForm

def message_form(request):
    return {'message_form': MessageForm(request)}
