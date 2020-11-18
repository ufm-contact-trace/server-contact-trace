# Definición del Proyecto

## ¿Qué es Contact Tracing? 

En el ámbito de la salud pública, la Contact Tracing (localización de contactos) es el proceso de identificación de las personas que pueden haber estado en contacto con una persona infectada ("contactos") y la posterior recopilación de más información sobre esos contactos. Mediante el rastreo de los contactos de las personas infectadas, las pruebas de infección, el aislamiento o el tratamiento de las personas infectadas y el rastreo de sus contactos a su vez, la salud pública tiene por objeto reducir las infecciones en la población.

![ContactTracing](https://imgl.krone.at/scaled/2135491/va84b69/full.jpg)

## Pasos para hacer Contact Tracing

1. Una persona es identificada con una enfermedad y se reporta a una autoridad pública de salud o alguna entidad centralizada (e.g. un servidor).
2. Se analizan las interacciones de esta persona y los “contactos” con los que estuvo.
3. Se notifica a los “contactos” sobre el infectado en un margen establecido de tiempo (e.g. 15 días).
4. Se procede a recomendar una cuarentena a los conectados. 

# Infraestructura de la solución

## Detalle de las tecnologías implementadas en la solución

### Aplicación móvil para dispositivos Android

Esta aplicación utiliza la tecnología de Google Nearby Api para encontrar personas con la aplicación instalada y que estén cerca de nosotros. Este módulo de trazabilidad está implementado en una app independiente y dentro de Covid Relief.

1. [Covid Relief Aplicación Móvil](https://github.com/Covid-relief/Covid-relief-app)

2. [Aplicación independiente de Contact Trace](https://github.com/Covid-relief/Contact-trace-app)

<img src="https://github.com/Covid-relief/server-contact-trace/blob/master/images/s12.png" width="300" />
<img src="https://github.com/Covid-relief/server-contact-trace/blob/master/images/s11.png" width="300" />


### Servicios en la nube para notificar y analizar contactos

Este servidor posee rutas para enviar los contactos y guardarlos en una base de datos NoSQL, en donde se almacenan estrucutras de datos filtradas por usuario y por día, esta opción se realiza automáticamente en la app cada 15 minutos y si existen más de 10 contactos para enviar. 

Al momento de que una persona resulte infectada, se tiene la opción de enviar los contactos que se tienen al momento, y el servidor extraerá de la base de datos la información de 14 días atrás. Esta data se analizará para identificar a qué personas notificar.

### Galería de Imágenes del Servidor de Contact Tracing

![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s1.png)
![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s2.png)
![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s3.png)
![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s4.png)

### Notificación enviada por el servidor

<img src="https://github.com/Covid-relief/server-contact-trace/blob/master/images/s5.png" width="300" />

## Resumen de la infraestructura en un mapa
![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s9.jpeg)
# Resumen de estrategias NoSQL

## Contenedores

Se tienen los diferentes servicios en contenedores aislados para que sea una infraestructura "serverless". Esto permite escalabilidad y autonomía por cada uno de los contenedores, y se puede cambiar su cantidad dependiendo de la necesidad de uso. 

![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s7.png)

## MongoDB

Se utilizó Mongo DB para guardar la información de los contactos. Se tiene una estructura que permite tener un documento por persona por día. Este documento contiene un atributo del tipo arreglo en el cual se listan todos los contactos encontrados con su respectivo timestamp. Es importante mencionar que esta lista contiene únicamente la información encriptada necesaria para poder identificar qué contacto es a la hora de notificar. Se seleccionó esta herramiento por su versatilidad a la hora de guardar la información y tienen optimizaciones de búsqueda.

![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s6.png)

## Redis Publisher - Subscriber 

Se tienen dos canales de comunicación, uno para que el contenedor receptor de información notifique al contenedor que analiza que vaya a buscar la información del usuario. El segundo canal sirve para que el contenedor que analiza avise al tercer contenedor, quien es el encargado de enviar correos. Se seleccionó esta herramienta porque su servicio Publisher Subscriber se acoplaba fácilmente a los contenedores y teníamos experiencia utilizándola.

![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s14.svg) 

## Redis Diccionario Key - Value

Sirve para guardar la información de las personas y permite que haya confidencialidad. Sabemos que los contactos que se almacenan en los dispositivos están encriptados, gracias a este diccionario podemos obtener el correo de la persona asociado a un hash. Se seleccionó esta herramienta aprovechando que ya teníamos redis corriendo entre los contenedores.

![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s13.svg) 


## JSON SQLite 

La data es almacenada en el dispositvo móvil hasta antes de enviarse al servidor. Por lo tanto, esta herramienta se seleccionó para almacenar la data de los contactos en el formato requerido por el servidor a la hora de enviarse. 

![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s8.png)

## Firebase CloudStore - RealTimeDatabase

Para inicio de sesión y control de registro de usuarios. Ya que se tiene el módulo corriendo dentro de Covid Relief, utilizamos los servicios de Firebase para el manejo de nuestro usuarios y le UID se manda en los jsons y se almacenan en Mongo DB.

![ContactTracing](https://github.com/Covid-relief/server-contact-trace/blob/master/images/s15.png) 


# Correr: Admin-console-web + Server-contact-trace

## URL del servidor corriendo en una instancia de cómputo de AWS 

http://ec2-18-216-89-33.us-east-2.compute.amazonaws.com

## Manage web administrator console for the Covid relief - Contact trace app
```console
docker build . -t name:tag
```

```console
docker run -p 80:80 name
```

```console
docker run -v /Users/andresreyes/Documents/UFM/Admin-console-web/app:/home -p 80:80 name
```

```console
chmod 770 run.sh
```

```console
docker compose-up
```

```console
docker-compose up --build --force-recreate
```

```console
docker image prune -a
```

```console
docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)
```