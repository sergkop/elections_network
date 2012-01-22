# coding=utf8
from random import choice

from django.core.management.base import BaseCommand

# [(name, username)]
male_names = (
    (u'Сергей', 'sergey'),
    (u'Андрей', 'andrey'),
    (u'Борис', 'boris'),
    (u'Влад', 'vlad'),
    (u'Геннадий', 'gennady'),
    (u'Георгий', 'georgiy'),
    (u'Михаил', 'mikhail'),
    (u'Александр', 'alexandr'),
    (u'Павел', 'pavel'),
    (u'Николай', 'nikolay'),
    (u'Владимир', 'vladimir'),
)

male_surnames = (
    u'Антонов',
    u'Крылов',
    u'Иванов',
    u'Петров',
    u'Сидоров',
    u'Козлов',
    u'Смирнов',
    u'Кузнецов',
    u'Попов',
    u'Соколов',
    u'Лебедев',
    u'Новиков',
    u'Морозов',
)

# [(name, username)]
female_names = (
    (u'Анна', 'anna'),
    (u'Светлана', 'sveta'),
    (u'Ольга', 'olga'),
    (u'Екатерина', 'katya'),
    (u'Мария', 'masha'),
    (u'Карина', 'karina'),
    (u'Вера', 'vera'),
    (u'Надежда', 'nadezhda'),
    (u'Любовь', 'lubov'),
    (u'Татьяна', 'tatyana'),
    (u'Наталья', 'natasha'),
    (u'Елена', 'lena'),
)

female_surnames = (
    u'Королева',
    u'Попова',
    u'Волкова',
    u'Соловьева',
    u'Васильева',
    u'Зайцева',
    u'Павлова',
    u'Голубева',
    u'Виноградова',
    u'Богданова',
    u'Воробьева',
    u'Федорова',
    u'Беляева',
)

# [(name, url)]
links = [
    (u'Гражданин Наблюдатель', 'http://nabludatel.org'),
    (u'Голос', 'http://golos.org/'),
    (u'Карта Нарушений', 'http://www.kartanarusheniy.ru/'),
    (u'RuElect', 'http://ruelect.com/ru'),
    (u'Яблоко', 'http://www.yabloko.ru/'),
    (u'Интерактивная инструкция наблюдателю', 'http://obuchenie.golos.org/nabludatel/'),
    (u'Список хороших ресурсов для наблюдателя', 'http://navalny.livejournal.com/641950.html'),
    (u'Инструкция как стать наблюдателем на выборах', 'http://rus-vubor.livejournal.com/3721.html'),
    (u'Федеральный закон о выборах президента', 'http://cikrf.ru/law/federal_law/zakon_19.html'),
    (u'Видео-инструкция наблюдателю', 'http://www.youtube.com/watch?v=Yd9YwFhVuk4'),
    (u'Тактика УИК по удалению наблюдателей', 'https://www.facebook.com/groups/203223386429654/doc/205815932837066/'),
    (u'Разъяснение о фото- и видеосъемке', 'https://docs.google.com/open?id=0Bw5NZ3CVfkt9ZWNkNDFjMGEtMWIyNy00ODkyLWJhMGQtODRiNTc4MmEyZTBm'),
    (u'Отчет наблюдателя', 'http://cifidiol.livejournal.com/1600.html'),
    (u'Сбор подписей за принятие понятного и эффективного избирательного кодекса', 'http://kodeks.golos.org'),
    (u'Портал, позволяющий быстро составить жалобы и заявления по нарушениям', 'http://kuda-komu.net'),
    (u'Статистический анализ результатов выборов', 'http://www.gazeta.ru/science/2011/12/10_a_3922390.shtml'),
    (u'Статистический анализ по результатам Петербурга', 'http://www.mr7.ru/news/politics/story_48190.html'),
    (u'Лига Избирателей', 'http://ligaizbirateley.ru/'),
    (u'Митинг 4 февраля', 'http://www.facebook.com/events/212286018856867/'),
    (u'Электронная демократия', 'http://www.facebook.com/groups/ns.fred/'),
]

class Command(BaseCommand):
    help = "Loads data for testing - users, links, participations, etc."

    def handle(self, *args, **options):
        #from geography.models import Location
        from django.contrib.auth.models import User
        from links.models import 
        #from users.models import *

        # Create users
        for i in xrange(300):
            is_male = choice([True, False])
            if is_male:
                first_name, username = choice(male_names)
                last_name = choice(male_surnames)
            else:
                first_name, username = choice(female_names)
                last_name = choice(female_surnames)

            alphabet = 'abcdefghijklmnopqrstvuwz'
            while True:
                postfix = '_' + choice(alphabet) + choice(['_', '']) + choice(alphabet)

                try:
                    user = User.objects.create(username=username+postfix, first_name=first_name, last_name=last_name)
                except:
                    continue
                else:
                    profile = user.get_profile()
                    profile.about = u"Этот пользователь создан в тестовых целях и не является настоящим человеком"
                    profile.save()
                    break


            # Creare links
            links
                

