import datetime
import random
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor

ACTIVATED = 'ALREADY_ACTIVATED'

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class RegistrationManager(models.Manager):
    def activate_user(self, activation_key):
        """
        Validate an activation key and activate the corresponding User if valid.

        If the key is valid and has not expired, return the User after activating.
        If the key is not valid or has expired, return ``False``.
        If the key is valid but the ``User`` is already active, return ``False``.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False

            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = ACTIVATED
                profile.save()
                return user

        return False

    @transaction.commit_on_success
    def create_inactive_user(self, username, email, password, send_email=True):
        """ Create a new, inactive User, generate a RegistrationProfile and email its activation key to the User """
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email()

        return new_user

    def create_profile(self, user):
        # The activation key is a SHA1 hash, generated from a combination of the username and a random salt
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        activation_key = sha_constructor(salt+user.username).hexdigest()
        return self.create(user=user, activation_key=activation_key)

    def delete_expired_users(self):
        """
        Remove expired instances of RegistrationProfile and their associated User's.

        It is recommended that this method be executed regularly as
        part of your routine site maintenance; this application
        provides a custom management command which will call this
        method, accessible as ``manage.py cleanupregistration``.

        Regularly clearing out accounts which have never been
        activated serves two useful purposes:

        1. It alleviates the ocasional need to reset a
           ``RegistrationProfile`` and/or re-send an activation email
           when a user does not receive or does not act upon the
           initial activation email; since the account will be
           deleted, the user will be able to simply re-register and
           receive a new activation key.

        2. It prevents the possibility of a malicious user registering
           one or more accounts and never activating them (thus
           denying the use of those usernames to anyone else); since
           those accounts will be deleted, the usernames will become
           available for use again.

        If you have a troublesome ``User`` and wish to disable their
        account while keeping it in the database, simply delete the
        associated ``RegistrationProfile``; an inactive ``User`` which
        does not have an associated ``RegistrationProfile`` will not
        be deleted.
        """
        for profile in self.all():
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_active:
                    user.delete()

class RegistrationProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    activation_key = models.CharField(max_length=40)

    objects = RegistrationManager()

    def __unicode__(self):
        return u"Registration information for %s" % self.user

    def activation_key_expired(self):
        """ Boolean showing whether this RegistrationProfile's activation key has expired """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key==ACTIVATED or \
               (self.user.date_joined+expiration_date <= datetime.datetime.now())
    activation_key_expired.boolean = True

    def send_activation_email(self):
        context = {
            'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        }
        subject = render_to_string('registration/activation_email_subject.txt', context)
        subject = ''.join(subject.splitlines()) # Email subject must not contain newlines

        message = render_to_string('registration/activation_email.txt', context)

        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
