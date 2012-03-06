# -*- coding:utf-8 -*-
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

from protocols.models import Protocol

class ProtocolView(TemplateView):
    template_name = 'protocols/view.html'

    # TODO: mark red the fields which do not coincide
    # TODO: if protocol is coming from CIK, don't show two columns
    def get_context_data(self, **kwargs):
        ctx = super(ProtocolView, self).get_context_data(**kwargs)

        try:
            protocol_id = int(kwargs['protocol_id'])
        except ValueError:
            raise Http404(u'Неправильно указан идентификатор протокола')

        protocol = get_object_or_404(Protocol.objects.select_related(), id=protocol_id)
        cik_protocol = Protocol.objects.cik_protocol(protocol.location)
        fields = [(Protocol._meta._name_map['p'+str(i)][0].verbose_name, getattr(protocol, 'p'+str(i)), getattr(cik_protocol, 'p'+str(i)) if cik_protocol else '-') \
                for i in range(1, 24)]

        ctx.update({
            'protocol': protocol,
            'fields': fields,
        })
        return ctx

protocol_view = ProtocolView.as_view()
