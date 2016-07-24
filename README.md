# rpmtools

Этот репозиторий содержит скрипты/шаблоны, упрощающие создание rpm

Поддерживаемые технологии:

* Django
* Torando
* Scrapy
* Yii

Также существует simple-сборка, которая упаковывает в пакет 
содержимое папки public, которая находится в корне проекта. 
Перед созданием пакета выполняется:

* Запуск npm install, если имеется файл package.json,
* Запуск bower install, если имеется файл bower.json,
* grunt, если имеется файл Gruntfile.js

### Simple

В пакет попадут все файлы после сборки из папки public, которая находится в корне проекта.
После установки файлы находятся в /opt/<имя пакета>

##### Параметры

* -b --build - номер релиза. По-умолчанию текущий timestamp
* -g --grunttask - название grunt-таска, который будет запускаться в процессе сборки. По-умолчанию default

##### Сборка

1. Создать в корне проекта файл package.json. Указать name, version
2. Запустить из корня проекта ./rpmbuild/simple/build.sh

### Scrapy

После установки файлы находятся в /opt/<имя пакета>

##### Параметры

* -b --build - номер релиза. По-умолчанию текущий timestamp
* -v --virtualenv - путь до virtualenv, с которым будет произведена сборка. По-умолчанию вывод команды ```which virtualenv``` 


##### Сборка

1. Создать в корне проекта файл package.json. Указать name, version, yumDependencies (массив), yumBuildDependencies (массив)
2. Дополнить requirements.txt зависимостью "supervisor==3.1.3"
3. Запустить из корня проекта ./rpmbuild/scrapy/build.sh
4. После установки пакета в конфиге по-умолчанию /etc/<имя пакета>/supervisord.conf необходимо указать имя scrapy-проекта для запуска

##### Инструментарий

1. Системный сервис, который запускает по кругу scrapy
2. Скрипт /usr/bin/<имя проекта>, который доступен в $PATH для быстрого запуска всех спайдеров указанного scrapy-проекта

### Django

Under construction

### Tornado

После установки файлы находятся в /opt/<имя пакета>

##### Параметры

* -b --build - номер релиза. По-умолчанию текущий timestamp
* -v --virtualenv - путь до virtualenv, с которым будет произведена сборка. По-умолчанию вывод команды ```which virtualenv``` 

##### Параметры package.json

* name - имя проекта
* version - версия проекта
* description - описание проекта
* yumDependencies — зависимости
* yumBuildDependencies - зависимости сборки
* gruntCwd - переход в директорию с grunt-скриптом (опционально)
* excludeFiles — файлы, которые не нужно помещать в пакет (опционально)
* virtualenv — путь до virtualenv и ключи запуска (опционально)
 
##### Сборка

1. Создать в корне проекта папку build, в ней создать package.json. Указать name, version, yumDependencies (массив), yumBuildDependencies (массив)
2. Запустить из корня проекта ./rpmbuild/tornado/build.sh
3. После установки пакета в конфиге по-умолчанию /etc/<имя пакета>/supervisord.conf необходимо скорректировать номер процесса

### Yii

Under construction