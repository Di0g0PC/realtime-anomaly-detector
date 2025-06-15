FROM sbrov3/xxx_base:1.0d

USER root

# adding source files
COPY . /alg/

WORKDIR /alg

ENTRYPOINT []
#"-u" para unbuffered mode — ou seja, desativa o buffer de saída padrão do Python
CMD ["python3","-u","/alg/main.py"]