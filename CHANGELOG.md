5.1.2
* Golang: возможность указать ldflags для go build
* Golang: возможность указать путь до package.json файла

5.1.1
* All: имя и суффикс имени из командной строки

5.1.0
* Simple: имя и суффикс имени из командной строки

5.0.0
* Golang: добавлена поддержка сборки проектов на golang

4.1.0
* Yii: поддержка composer, миграция функционала из Python

4.0.0
* Django, Tornado -> Python

3.6.9
* Django, Tornado: замена в versionsuffix - на _
* Django: фикс указания пути до питона (--python в пути до virtualenv)

3.6.8
* Django: version suffix

3.6.7
* Yii: чистим twig кеш

3.6.6
* Yii: yarn, если существует

3.6.5
* Simple: excluded files

3.6.4
* Simple: yarn, если существует, и поддержка нескольких команд

3.6.3
* Tornado: excluded files удаляются после выполнения всех команд

3.6.2
* Tornado: вместо npm используется yarn, если он есть в системе

3.6.1
* Tornado: commands, можно задать несколько доп. команд, которые будут выполнены в процессе сборки

3.6.0
* Все: сделан common.sh. В нем функции, которые выполняются для всех build.sh
* Все: поправлен meta.py, чтоб print работал в python 3
* Все: небольшой рефакторинг переменных, кода
* Tornado: manage.py можно вызывать из любого места в системе через manage.sh. Если manage.sh есть в корне проекта, он не заменяется manage.sh из rpmtools 

3.5.5

* Все: делается export переменной FULLVERSION со значением полной версии пакета

3.5.4

* Django, Tornado: при обновлении пакета удаляются все pyc-файлы

3.5.3

* Tornado: выполнение кастомной команды после сборки

3.5.1, 3.5.2

* Django: fix разбора аргументов

3.5.0

* Django: кастомные init.d скрипты
* Django: опциональное отключение init.d скрипта для celerycam
* Django: опциональное отключение автомиграций


3.4.2

* Django, Tornado: обновление setuptools и pip перед установкой

3.4.1

* Django, Tornado: скачивание BuildRequires в build.sh

3.4.0

* Yii: доп. команда сборки

3.3.6

* Tornado: лимиты в systemd

3.3.5

* Simple: возможность задавать grunt-таск из package.json

3.3.1-3.3.4

* Tornado: фиксинг systemd сценария

3.3.0

* Tornado: изменена структура конфигов по-умолчанию для supervisor. Теперь существует папка /etc/%{name}/programs, в
которой либо дефолтный конфиг простого приложения, либо конфиги из build/programs. /etc/%{name}/supervisor.conf инклюдит 
конфиги из /etc/%{name}/programs
* Tornado: поддержка Centos 7 (systemd)
* Tornado: пусть до virtualenv и его ключи можно задавать из build/package.json

3.2.0

* Simple: выполнение кастомной команды после сборки
* Yii: кеширование node_modules, bower_components

3.1, 3.1.1, 3.1.2

* Simple, Tornado: добавлена поддержка versionsuffix

3.0.1

* NodeJS: исправления в init.d скриптах

3.0.0

* NodeJS: новая технология

2.1.1, 2.1.2

* Django: исправлен init.d скрипт для новой celery

2.1.0

* Django: кеширование virtualenv, node_modules

2.0.0

* Ведение CHANGELOG
* Обновление README.md
* Tornado: замена BUILD_INFO на package.json
* Tornado: кеширование virtualenv
* Tornado: grunt-сборка клиентской части (при наличии)
* Tornado: возможность исключать файлы из пакета

1.2.5

* Tornado: использование глобального супервизора. Удаление добавленного в версии 1.1.0 функционала, который больше не нужен
* Tornado: по-умолчанию для всех воркеров один путь до файла логов

1.2.4

* Simple: не учитывается версия в package.json и bower.json при кешировании

1.2.3

* Simple: не кешировать bower_components, если их не удалось найти

1.2.2

* Simple: убран verbose при npm install

1.2.1

* Simple: не учитываем успех сохранения в кеш

1.2.0

* Simple: Кеширование bower_components и node_modules
 
1.1.0

* Tornado: можно указать путь до супервизора
* Simple: backbone переименован в simple из-за широты использования

1.0.0

* Начало
