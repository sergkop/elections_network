from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

register = template.Library()

# TODO: add optional hint (title) and class to tell tipsy to show a tip
@register.inclusion_tag('elements/button.html')
def button(icon, title, id=None, link='', center='center'):
    """ link is either a url, starting with http:// or https://, or the name of a view """
    if link!='' and not link.startswith('http://') and not link.startswith('https://') and not link.startswith('mailto:'):
        link = reverse(link)

    external = link.startswith('http') if link else False

    return {'icon': icon, 'title': title, 'id': id, 'link': link,
            'external': external, 'center': center!=''}

@register.tag(name="tabs")
def tabs_tag(parser, token):
    args = token.split_contents()
    if len(args) % 3 != 2:
        raise template.TemplateSyntaxError("Incorrect number of arguments")
    return TabsNode(*args[1:])

class TabsNode(template.Node):
    def __init__(self, *args):
        """
        args is a sequence of 'id', 'active_url', 'param_name', 'param_value' and tripples (title, url, include_path) (a 1-dimensional list).
        All urls must either start with '#' or be urls (starting with '/' or view name).
        param_name and param_value serve to pass extra parameter to the view (
        """
        self.args = [template.Variable(arg) for arg in args]

    def render(self, context):
        self.args = [arg.resolve(context) for arg in self.args]
        id = self.args[0]
        active_url = self.args[1]
        param_name = self.args[2]
        param_value = self.args[3]
        args = self.args[4:]

        tabs = []
        num = len(args) / 3
        for i in range(num):
            url = args[3*i+1]
            if url[0]!='#' and url[0]!='/':
                context_dict = context.dicts[0] # a hack to extract context dict from RequestContext
                kwargs = {}
                if param_name in context_dict:
                    kwargs[param_name] = param_value
                url = reverse(url, kwargs=kwargs)

            tabs.append({
                'title': args[3*i],
                'url': url,
                'path': args[3*i+2],
                'active': active_url==args[3*i+1],
            })

        tabs_content = []
        if any(tab['url'].startswith('#') for tab in tabs):
            for tab in tabs:
                tabs_content.append({
                    'id': tab['url'][1:],
                    'path': tab['path'],
                    'active': tab['active'],
                })
        else:
            active_tab = filter(lambda tab: tab['active'], tabs)[0]
            tabs_content.append({
                'id': 'main_tab',
                'path': active_tab['path'],
                'active': True,
            })

        context.update({'id': id, 'tabs': tabs, 'tabs_content': tabs_content})
        return render_to_string('elements/tabs.html', context)
