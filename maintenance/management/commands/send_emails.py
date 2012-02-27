# -*- coding:utf-8 -*-
from time import sleep

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

MESSAGE = u"""Добрый день%s!

Проект Гражданский Контроль начинает серию из 5 акций – по одной в день – за неделю, предшествующую
президентским выборам.

Наша первая акция «Пригласи друзей» стартует в сегодня, 27 февраля.

В чем суть? Обеспечить «полный комплект» гражданского контроля на каждой УИК в стране.
В нашем понимании, это –  5 избирателей, 3 наблюдателя, 1 юрист и 1 представитель СМИ,
зарегистрированные на grakon.org.

Что мы хотим от вас? Найдите ваш УИК (http://grakon.org/find_uik) и посмотрите,
кто там уже зарегистрировался. Если в формуле 5+3+1+1 кого-то не хватает, то:

  - пригласите друзей, которые обладают навыками юриста или имеют возможность быть представителями СМИ;

  - обратитесь в организации типа «Гражданин Наблюдатель», «Росвыборы», «Голос» и другие,
    чтобы они сообщили вам, кто будет наблюдателем на вашем участке.
    Попробуйте связаться с этими людьми и пригласите зарегистрироваться.
    Таким образом, вы будете видеть, целиком ли охвачен ваш УИК.

Подробности акции можно прочитать на сайте - http://grakon.org/campaign

Кроме того, мы полностью обновили дизайн сайта и добавили поиск участников по регионам.
Также мы значительно улучшили внешний вид карты и планируем ввести множество
новых функций в ближайшие дни.

Благодарим за проявление вашей гражданской позиции,

команда Гракона."""

class Command(BaseCommand):
    help = "Send emails to all activated users."

    def handle(self, *args, **options):
        from loginza.models import UserMap
        inactive_ids = UserMap.objects.filter(verified=False).values_list('user', flat=True)
        active_users = User.objects.exclude(email='').filter(is_active=True) \
                .exclude(id__in=inactive_ids)

        for user in active_users:
            profile = user.get_profile()
            if profile.first_name:
                name = ', %s %s' % (profile.first_name, profile.last_name)
            else:
                name = ''

            message = MESSAGE % name

            sleep(0.1)
            send_mail(u'Акция Гракона "Собери команду на своем УИКе"', message, 'admin@grakon.org',
                    [user.email], fail_silently=False)
