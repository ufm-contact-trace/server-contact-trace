FROM python:3.8.5-alpine
#LABEL MAINTAINER="UFM UFM <example@d
# ENV GROUP_ID=1000 \
#     USER_ID=1000
ADD ./requirements.txt /app/
RUN pip install -r requirements.txt a
    add --no-cache --virtual .build-d
    && pip install --no-cache-dir -r
    && apk del .build-deps
ADD . /app/
# RUN pip install gunicorn
# RUN addgroup -g $GROUP_ID www
# RUN adduser -D -u $USER_ID -G www w
# USER www
EXPOSE 5000
EXPOSE 80
# CMD [ "gunicorn", "-w", "4", "--bin
CMD ["python", "app1.py", "app.py"]
