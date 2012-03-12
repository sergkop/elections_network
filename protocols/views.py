# -*- coding:utf-8 -*-
from random import randint

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView

from locations.models import Location
from protocols.forms import ProtocolForm
from protocols.models import AttachedFile, Protocol

try:
    import cloudfiles
    cloudfiles_conn = cloudfiles.get_connection(getattr(settings, 'CLOUDFILES_USERNAME'),
            getattr(settings, 'CLOUDFILES_KEY'))
except:
    cloudfiles_conn = None

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

        try:
            cik_protocol = Protocol.objects.from_cik().get(location=protocol.location)
        except Protocol.DoesNotExist:
            cik_protocol = None

        fields = [(Protocol._meta._name_map['p'+str(i)][0].verbose_name, getattr(protocol, 'p'+str(i)), getattr(cik_protocol, 'p'+str(i)) if cik_protocol else '-') \
                for i in range(1, 24)]

        content_type = ContentType.objects.get_for_model(Protocol)

        ctx.update({
            'protocol': protocol,
            'fields': fields,
            'files': AttachedFile.objects.filter(content_type=content_type, object_id=protocol.id),
        })
        return ctx

protocol_view = ProtocolView.as_view()

@login_required
def upload_protocol(request):
    if request.method == 'POST':
        form = ProtocolForm(request.POST, request.FILES)
        if form.is_valid():
            protocol = form.save()
            protocol.source = request.profile
            protocol.protocol_id = randint(1, 10000)
            protocol.save()

            protocols_container = cloudfiles_conn.get_container(settings.CLOUDFILES_CONTAINER)

            content_type = ContentType.objects.get_for_model(Protocol)

            for name in ('photo1', 'photo2', 'photo3', 'photo4', 'photo5'):
                if name in request.FILES:
                    filename = 'protocol_'+str(protocol.id)+'_'+name[5]
                    file_obj = protocols_container.create_object(filename)

                    # TODO: limit file size
                    # TODO: filter content types
                    upload_file = request.FILES[name]
                    file_obj.content_type = upload_file.content_type

                    file_obj.write(upload_file)

                    AttachedFile.objects.create(content_type=content_type, object_id=protocol.id,
                            internal=True, url=filename)

            message = u'Пользователь %s выложил протокол %s.\n' \
                    u'Верифицировать его можно здесь - %s.'% (
                    settings.URL_PREFIX+request.profile.get_absolute_url(),
                    settings.URL_PREFIX+protocol.get_absolute_url(),
                    settings.URL_PREFIX+'/'+settings.ADMIN_PREFIX+'/protocols/protocol/'+str(protocol.id)+'/')

            send_mail(u'[ПРОТОКОЛ] Выложен новый протокол', message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            return redirect(protocol.get_absolute_url())

        location = getattr(form, 'location', None)
    else:
        form = ProtocolForm()
        try:
            loc_id = int(request.GET.get('loc_id', ''))
        except ValueError:
            location = None
        else:
            try:
                location = Location.objects.exclude(tik=None).get(id=loc_id)
            except Location.DoesNotExist:
                location = None

    context = {'location': location, 'form': form}

    return render_to_response('protocols/upload.html',
            context_instance=RequestContext(request, context))
