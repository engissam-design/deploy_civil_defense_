.\venv\Scripts\activate
python manage.py migrate     
python manage.py makemigrations  
 python manage.py runserver

ددددد\
git push -u origin main 
Radis path:
wesbist inside this folder

redis-server
redis-cli ping

run with socket
install reqiermints
daphne mapproject.asgi:application

for Auto Reload
watchfiles "daphne mapproject.asgi:application"


al> .\venv\Scripts\python.exe -m daphne -b 0.0.0.0 -p 8000 mapproject.asgi:application

path:
PS D:\civilDefense_website-main\civilDefense_website-main\civilDefense_website-main>

cd civilDefense_website-main

http://172.16.16.200:8002/

 daphne -b 0.0.0.0 -p 8002 mapproject.asgi:application

  .\venv\Scripts\activate




web config
<?xml version="1.0" encoding="utf-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="DaphneProxy" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://127.0.0.1:8000/{R:1}" />
                </rule>
            </rules>
        </rewrite>
    </system.webServer>
</configuration>

