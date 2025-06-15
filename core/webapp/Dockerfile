FROM sbrov3/xxx_base:1.0d

USER root

# adding source files
COPY . /webapp/

WORKDIR /webapp

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]