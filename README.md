# rpmtools

Этот репозиторий содержит скрипты/шаблоны, упрощающие создание rpm

Поддерживаемые технологии:

* Django
* Torando
* Scrapy
* Backbone
* Yii

### Django

Under construction

### Tornado

Under construction

### Scrapy

##### Сборка

1. Создать в корне проекта файл package.json. Указать name, version, yumDependencies (массив), yumBuildDependencies (массив)
2. Дополнить requirements.txt зависимостью "supervisor==3.1.3"
3. Запустить из корня проекта ./rpmbuild/scrapy/build.sh
4. После установки пакета в конфиге по-умолчанию /etc/<имя проекта>/supervisord.conf необходимо указать имя scrapy-проекта для запуска

##### Инструментарий

1. Системный сервис, который запускает по кругу scrapy
2. Скрипт /usr/bin/<имя проекта>, который доступен в $PATH для быстрого запуска всех спайдеров указанного scrapy-проекта


### Backbone

Under construction

### Yii

Under construction