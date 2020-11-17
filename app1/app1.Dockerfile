FROM python:3.8.5-alpine
#LABEL MAINTAINER="UFM UFM <example@d
# ENV GROUP_ID=1000 \
#     USER_ID=1000
WORKDIR /app/

ADD ./requirements.txt /app/

RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps
ADD . /app/
# RUN pip install gunicorn
# RUN addgroup -g $GROUP_ID www
# RUN adduser -D -u $USER_ID -G www w
# USER www
EXPOSE 80
# CMD [ "gunicorn", "-w", "4", "--bin
CMD ["python","-u", "app1.py"]
