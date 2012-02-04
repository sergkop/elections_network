from django import template
from django.core.urlresolvers import reverse

register = template.Library()

# TODO: add optional description (to show with tipsy)
@register.inclusion_tag('elements/button.html')
def button(icon, title, id=None, link='', center='center'):
    """ link is either a url, starting with http:// or https://, or the name of a view """
    if link!='' and not link.startswith('http://') and not link.startswith('https://') and not link.startswith('mailto:'):
        link = reverse(link)

    external = link.startswith('http') if link else False

    return {'icon': icon, 'title': title, 'id': id, 'link': link,
            'external': external, 'center': center!=''}
