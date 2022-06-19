# praktikum_new_diplom
Адрес http://51.250.104.158/
Логин msOleg@yandex.ru
Пароль lavka123        

## Запуск проекта на удаленном сервере

1. Скопируйте в корень домашней папки на удаленном сервере следующие файлы и директории
- `./docs/*`
- `./frontend/*`
- `./infra/docker-compose.yml`
- `./infra/nginx.config`
- `./infra/.env`

2. Отредактируйте файл .env в корне домашней папки на удаленном сервере, заполните по образцу
из файла .env

3. Установите docker согласно руководству на официальном сайте

4. Запустите проект командой 
```bash
docker-compose up -d --build
```
5. Внутри контейнера создать мигрции, создать суперпользователя, собрать статику, загрузть тэги и игредиенты
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
docker-compose exec web python manage.py add_tags
docker-compose exec web python manage.py add_ingredients
```
