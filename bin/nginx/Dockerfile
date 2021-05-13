FROM nginx:1.20.0-alpine-perl
RUN apk add --no-cache nginx-module-perl
RUN rm /etc/nginx/conf.d/default.conf
COPY ./bin/nginx/nginx.conf /etc/nginx/nginx.conf
CMD ["/bin/sh", "-c", "exec nginx -g 'daemon off;';"]
EXPOSE 80