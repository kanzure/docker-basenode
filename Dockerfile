FROM phusion/baseimage:0.9.12

# environment variables
ENV DEBIAN_FRONTEND noninteractive

# pull package metadata
RUN apt-get update

# install supervisord
RUN apt-get install -y supervisor
RUN sed -i 's/^\(\[supervisord\]\)$/\1\nnodaemon=true/' /etc/supervisor/supervisord.conf

# install consul
RUN apt-get install -y unzip
ADD https://dl.bintray.com/mitchellh/consul/0.3.1_linux_amd64.zip /tmp/consul.zip
RUN cd /usr/local/sbin && unzip /tmp/consul.zip

# install confd
ADD https://github.com/kelseyhightower/confd/releases/download/v0.4.1/confd-0.4.1-linux-amd64 /usr/local/bin/confd
RUN chmod +x /usr/local/bin/confd

# install haproxy
RUN apt-get install -y haproxy

# cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# also include supervisord config
ADD ./etc/supervisor/conf.d/confd.conf /etc/supervisor/conf.d/
ADD ./etc/supervisor/conf.d/consul.conf /etc/supervisor/conf.d/
ADD ./etc/supervisor/conf.d/haproxy.conf /etc/supervisor/conf.d/

# also include confd config
ADD ./etc/confd /etc/confd

# include default haproxy config that doesn't suck (needs "listen" line)
ADD ./etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg

# boot up supervisord on startup
ADD ./etc/my_init.d/01_supervisord.sh /etc/my_init.d/
RUN chmod o+x /etc/my_init.d/01_supervisord.sh

# for supervisor logging
# TODO: figure out logging, syslog, etc. for multiple nodes.
RUN mkdir -p /data/log/supervisor/

# why this workdir?
WORKDIR /etc/supervisor/conf.d

# baseimage-docker init system
# consider using --quiet
CMD ["/sbin/my_init"]

# open up some ports
# TODO: what are each of these for?
EXPOSE 8400 8500 8600/udp
