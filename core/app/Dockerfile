FROM sbrov3/xxx_base:1.0d

USER root

# adding source files
COPY . /app/
 
COPY cmd.sh /cmd.sh
RUN chmod 755 /cmd.sh

WORKDIR /app

EXPOSE 8000

ENTRYPOINT []

CMD "/cmd.sh"