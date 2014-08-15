FROM phusion/baseimage:0.9.12

# environment variables
ENV DEBIAN_FRONTEND noninteractive

# pull package metadata
RUN apt-get update

# get pip for python packages later (pyconfd)
# consider adding python-gevent so that pip doesn't have to later
RUN apt-get install -y python python-setuptools python-pip python-dev

# install supervisord
RUN apt-get install -y supervisor
RUN sed -i 's/^\(\[supervisord\]\)$/\1\nnodaemon=true/' /etc/supervisor/supervisord.conf

# install consul
RUN apt-get install -y unzip
ADD https://dl.bintray.com/mitchellh/consul/0.3.1_linux_amd64.zip /tmp/consul.zip
RUN cd /usr/local/sbin && unzip /tmp/consul.zip

# install consulate (for python/pyconfd/consul reasons)
RUN pip install requests
RUN apt-get install -y git
RUN git clone https://github.com/gmr/consulate.git /tmp/consulate
RUN cd /tmp/consulate && python setup.py install

# install pyconfd
RUN pip install pyconfd==0.0.7

# install haproxy
RUN apt-get install -y haproxy

# cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# install ssh public keys
ADD ./ssh /tmp/ssh
RUN /bin/bash -c "cat /tmp/ssh/*.pub >> /root/.ssh/authorized_keys && rm -fr /tmp/ssh"

# make a place to put consul config
RUN mkdir -p /etc/consul/conf.d/

# also include supervisord config
ADD ./etc/supervisor/conf.d/pyconfd.conf /etc/supervisor/conf.d/
ADD ./etc/supervisor/conf.d/consul.conf /etc/supervisor/conf.d/
ADD ./etc/supervisor/conf.d/haproxy.conf /etc/supervisor/conf.d/

# include default haproxy config that doesn't suck (needs "listen" line)
ADD ./etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg

# boot up supervisord on startup
ADD ./etc/my_init.d/01_supervisord.sh /etc/my_init.d/
RUN chmod o+x /etc/my_init.d/01_supervisord.sh

# always join consul cluster
ADD ./etc/supervisor/conf.d/consuljoin.conf /etc/supervisor/conf.d/
ADD ./consuljoin.sh /
RUN chmod o+x /consuljoin.sh

# also include pyconfd config
ADD ./etc/pyconfd /etc/pyconfd

# for supervisor logging
# TODO: figure out logging, syslog, etc. for multiple nodes.
RUN mkdir -p /data/log/supervisor/

# why this workdir?
WORKDIR /etc/supervisor/conf.d

# baseimage-docker init system
# consider using --quiet
CMD ["/sbin/my_init"]

# open up some ports
# consul rpc 8400, http 8500, dns 8600, lan 8301, wlan 8302
EXPOSE 8400 8500 8600/udp
