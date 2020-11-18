FROM python:3.8.5-alpine

#LABEL MAINTAINER="UFM UFM <example@domain.com>"

# ENV GROUP_ID=1000 \
#     USER_ID=1000

WORKDIR /app/

ADD ./requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/
# RUN pip install gunicorn

# RUN addgroup -g $GROUP_ID www
# RUN adduser -D -u $USER_ID -G www www -s /bin/sh

# USER www

EXPOSE 8383

# CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "wsgi"]

CMD ["python", "-u", "app3.py"]
# CMD [""]
