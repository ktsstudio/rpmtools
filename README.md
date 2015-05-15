### rpmtools

Этот репозиторий содержит скрипты/шаблоны, упрощающие создание rpm для Django-based проекта.

## Как использовать

Внутри корневой директории проекта:

```bash
git submodule add git@gitlab.tech-mail.ru:d.rubtsov/rpmtools.git
touch BUILD_INFO
```

Поменяйте содержимое файла BUILD_INFO на соответствующее вашему проекту, например:

```
2.1.33
technopark
New Technopark
python mysql libjpeg syslog
python rpm-build redhat-rpm-config mysql-devel libjpeg-devel
application
```

1 строка - версия
2 - название проекта (будет использоваться буквально для всего - название директорий и т.д)
3 - описание проекта
4 - секция спеки `Requires`
5 - секция спеки `BuildRequires`
6 - имя Django проекта (имя дериктории с settings.py)

в `settings.py` нужно дописать:

```python
if 'collectstatic' in sys.argv:
    STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(DISK_ROOT)), 'collected_static')
```

где DISK_ROOT - корень вашего проекта (папка, которая содержит templates, application...)

Далее нужно в корневую директорию положить `default.conf` - файлик для ConfigParser с дефолтными настройками проекта

Если нужно можно в `settings.py` прописать определение текущей версии

```
try:
    with open(os.path.join(DISK_ROOT, 'BUILD_INFO'), 'r') as f:
        VERSION = ('v' + f.readlines()[0]).strip()
except:
    VERSION = 'v1'
```

И также нужно прописать в `settings.py`

```python
if 'test' in sys.argv or 'jenkins' in sys.argv:

    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
    SOUTH_TESTS_MIGRATE = False
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt': "%d/%b/%Y %H:%M:%S"
            },
        },
    }
```


Также нужно настроить сборку проекта в jenkins:

* поставить галочку `Recursively update submodules`
* execute shell 1:

```bash
rm -rf /var/lib/jenkins/rpmbuild/RPMS/x86_64/technopark*
cd rpmtools
./build_rpm.sh
export RSYNC_PASSWORD=1xgJGRLK3Ybw1v0
cd /var/lib/jenkins/rpmbuild/RPMS/x86_64
rsync technopark* rsync://jenkins@tp-infra1.tech-mail.ru/projects_repos
```




