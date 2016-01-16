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