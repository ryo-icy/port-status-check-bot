FROM centos:centos7

ARG UID=1000
RUN useradd -m -u ${UID} docker

RUN yum install -y python3

RUN localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG="ja_JP.UTF-8" \
    LANGUAGE="ja_JP:ja" \
    LC_ALL="ja_JP.UTF-8"

RUN mkdir /script
COPY script/ /script

USER ${UID}

WORKDIR /script

RUN pip3 install --user -r requirements.txt

CMD python3 discordbot.py