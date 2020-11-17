# Admin-console-web + Server-contact-trace
Manage web administrator console for the Covid relief - Contact trace app

docker build . -t name:tag

docker run -p 80:80 name

docker run -v /Users/andresreyes/Documents/UFM/Admin-console-web/app:/home -p 80:80 name

chmod 770 run.sh

docker compose-up

# Definición del Proyecto

## ¿Qué es Contact Tracing? 

En el ámbito de la salud pública, la Contact Tracing (localización de contactos) es el proceso de identificación de las personas que pueden haber estado en contacto con una persona infectada ("contactos") y la posterior recopilación de más información sobre esos contactos. Mediante el rastreo de los contactos de las personas infectadas, las pruebas de infección, el aislamiento o el tratamiento de las personas infectadas y el rastreo de sus contactos a su vez, la salud pública tiene por objeto reducir las infecciones en la población.

![ContactTracing](https://imgl.krone.at/scaled/2135491/va84b69/full.jpg)

## Pasos para hacer Contact Tracing

1. Una persona es identificada con una enfermedad y se reporta a una autoridad pública de salud o alguna entidad centralizada (e.g. un servidor).
2. Se analizan las interacciones de esta persona y los “contactos” con los que estuvo.
3. Se notifica a los “contactos” sobre el infectado en un margen establecido de tiempo (e.g. 15 días).
4. Se procede a recomendar una cuarentena a los conectados. 

## Galería de Imágenes del Servidor de Contact Tracing

![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s1.png)
![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s2.png)
![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s3.png)
![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s4.png)



# Admin-console-web + Server-contact-trace
Manage web administrator console for the Covid relief - Contact trace app

docker build . -t name:tag

docker run -p 80:80 name

docker run -v /Users/andresreyes/Documents/UFM/Admin-console-web/app:/home -p 80:80 name

chmod 770 run.sh

docker compose-up

docker-compose up --build --force-recreate

docker image prune -a

docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)
