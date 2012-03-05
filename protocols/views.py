# -*- coding:utf-8 -*-
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

from protocols.models import Protocol

class ProtocolView(TemplateView):
    template_name = 'protocols/view.html'

    def get_context_data(self, **kwargs):
        ctx = super(ProtocolView, self).get_context_data(**kwargs)

        try:
            protocol_id = int(kwargs['protocol_id'])
        except ValueError:
            raise Http404(u'Неправильно указан идентификатор протокола')

        protocol = get_object_or_404(Protocol.objects.select_related(), id=protocol_id)

        fields = []
        for i in range(1, 24):
            fields.append((Protocol._meta._name_map['p'+str(i)][0].verbose_name, getattr(protocol, 'p'+str(i))))
        
        
        
        ctx.update({
            'protocol': protocol,
            'fields': fields,
        })
        return ctx

protocol_view = ProtocolView.as_view()
