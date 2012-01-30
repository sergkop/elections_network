# coding=utf8
from random import choice
import sys

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

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

def print_progress(i, count):
    """ Show progress message updating in-place """
    if i < count-1:
        sys.stdout.write("\r%(percent)2.1f%%" % {'percent': 100*float(i)/count})
        sys.stdout.flush()
    else:
        sys.stdout.write("\r")
        sys.stdout.flush()

class Command(BaseCommand):
    help = "Loads data for testing - users, links, participations, etc."

    def handle(self, *args, **options):
        from django.contrib.auth.models import User
        from links.models import Link
        from locations.models import Location
        from users.models import Contact, Participation

        users_db = []
        USER_COUNT = 300
        print "creating users"
        # Create users
        for i in xrange(USER_COUNT):
            print_progress(i, USER_COUNT)
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
                except IntegrityError:
                    continue
                else:
                    users_db.append(user)
                    profile = user.get_profile()
                    profile.about = u"Этот пользователь создан в тестовых целях и не является настоящим человеком"
                    profile.save()
                    break

        print "creating links"
        locations_db = list(Location.objects.all())
        for i in range(len(locations_db)):
            print_progress(i, len(locations_db))
            for j in range(choice([1, 2, 3, 4, 5])):
                user = choice(users_db)
                link_data = choice(links)
                try:
                    Link.objects.create(location=locations_db[i], user=user, name=link_data[0], url=link_data[1])
                except IntegrityError:
                    continue

        print "creating contacts"
        for i in range(USER_COUNT):
            print_progress(i, USER_COUNT)
            Participation.objects.create(location=choice(locations_db), user=users_db[i], type='voter')
            for i in range(choice([1, 2, 3, 4, 5])):
                contact = choice(users_db)
                if contact != user:
                    try:
                        Contact.objects.create(user=users_db[i], contact=contact)
                    except IntegrityError:
                        continue

        # Add superuser as a contact to a few users
        for superuser in User.objects.filter(is_superuser=True):
            for i in range(3):
                try:
                    Contact.objects.create(user=choice(users_db), contact=superuser)
                except IntegrityError:
                    pass

            if not superuser.first_name and not superuser.last_name:
                superuser.first_name = superuser.username
