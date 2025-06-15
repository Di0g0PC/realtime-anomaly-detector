### syntax = docker/dockerfile:1.5
FROM python:3.12.9-bullseye

# Debian
#todos os comandos são executados como root (adminstrador dentro do container)
USER root 


RUN python -m ensurepip --upgrade \
    && pip install --upgrade pip \
    && python -m pip install --upgrade setuptools \
    && apt-get update \
    && apt-get install -y iputils-ping software-properties-common ca-certificates curl wget unzip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

#RUN curl -fsSL https://pkgs.tailscale.com/stable/debian/bullseye.noarmor.gpg  >/usr/share/keyrings/tailscale-archive-keyring.gpg 
#RUN curl -fsSL https://pkgs.tailscale.com/stable/debian/bullseye.tailscale-keyring.list  >/etc/apt/sources.list.d/tailscale.list
#RUN apt-get update
#RUN apt-get install -y tailscale

        
COPY requirements.txt /requirements.txt
RUN pip install --no-cache -r /requirements.txt
