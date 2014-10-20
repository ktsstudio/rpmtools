### rpm-tools

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
corpse
CORP.MAIL.RU
python mysql mysql-server libjpeg syslog
python rpm-build redhat-rpm-config mysql-devel libjpeg-devel
```

1 строка - версия
2 - название проекта (будет использоваться буквально для всего - название директорий и т.д)
3 - описание проекта
4 - секция спеки `Requires`
5 - секция спеки `BuildRequires`

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
if [ ! -d env ]; then
    virtualenv --distribute --python=/usr/bin/python2.6 env
    env/bin/pip install distribute --upgrade
    env/bin/pip install -r requirements.txt --upgrade
    virtualenv --relocatable env
else
    source env/bin/activate
    pip install distribute --upgrade
    pip install -r requirements.txt --upgrade
fi
find ./ -name "*.pyc" -delete
```

* execute shell 2

```bash
if $DEPLOY ; then
  cd rpm-tools
  ./build_rpm.sh
  RESULT=$(ls -1t $(find ${HOME}/rpmbuild/RPMS/ -name "*.rpm") | head -n 1)
  rsync -P --password-file=/var/lib/jenkins/repo.key $RESULT sys.jenkins@pkg.corp.mail.ru::c6-intdev-x86_64
  echo "c6-intdev-x64" | nc pkg.corp.mail.ru 12222
fi
```



