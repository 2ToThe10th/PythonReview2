# PythonReview2

It work on https://t.me/AlarmClockReviewBot

##### Для того чтобы поднять свой собственный сервис будильников нужно:

• Если у вас нет ssl сертификата, то нужно его создать, например самоподписной сертификат можно создать с помощью команды openssl

• Далее нужно установить postgresql, например с помощью команды ```sudo apt-get install postgresql``` для ubuntu

• После установки, рекомендуется создать отдельную базу данных для проекта и пользователя с ограниченными правами

• Также создайте нового бота 

• Теперь осталось только указать всю эту информацию в виде json аналогично файлу sample_config.json. 
Расположение файлов нужно указывать относительно расположения скрипта run.sh.

• Для запуска проекта запустите файл run.sh. Команда: ```./run.sh [your config file]```
