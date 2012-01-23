#import os.path
#import site
import sys
#sys.path.prepend(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#import imp
try:
    #imp.find_module('settings') # Assumed to be in the same directory.
    import settings
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)


# load virtualenv if set
#if settings.VIRTUALENV:
    #site.addsitedir(settings.VIRTUALENV)

if __name__ == "__main__":
    from django.core.management import execute_manager
    execute_manager(settings)
