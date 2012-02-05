from uni_form.helper import FormHelper
from uni_form.layout import Submit

def form_helper(action_name, button_name):
    """ Shortcut to generate django-uniform helper """
    helper = FormHelper()
    helper.form_action = action_name
    helper.form_method = 'POST'
    helper.add_input(Submit('', button_name))
    return helper
