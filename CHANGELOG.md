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
