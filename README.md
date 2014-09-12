**docker-basenode** is a docker container that provides some basic service discovery benefits. The container is based on [phusion/baseimage](https://github.com/phusion/baseimage-docker) and includes [supervisor](https://github.com/supervisor/supervisor), [pyconfd](https://github.com/kanzure/pyconfd) similar to [confd](https://github.com/kelseyhightower/confd), [haproxy](https://github.com/haproxy/haproxy) and [consul](https://github.com/hashicorp/consul).

# Service Discovery

Application containers using this container as a parent should route all outgoing HTTP/TCP requests through localhost on some port. The port is defined in the haproxy configuration in the basenode container. Every container in the cluster has the same haproxy configuration. The haproxy configuration is updated every 5 seconds by pyconfd, which retrieves information from consul running on the local container. Changes in the data received from consul will cause pyconfd to generate a new haproxy config file and then to trigger a graceful reload of haproxy. Previous connections through haproxy will be maintained as haproxy goes online with the new configuration. Future connections through haproxy will then be load balanced to one of the services that consul indicates the presence of (by IP address).

The haproxy configuration in /etc/haproxy/haproxy.cfg is just some default configuration that is immediately discarded when pyconfd generates its own version of the configuration file. So the vast majority of the time any edits to haproxy configuration should happen in the pyconfd template in /etc/pyconfd/templates/ instead. Also, this template is using [jinja2](http://jinja.pocoo.org/) and any new variables can be inserted by modifying the python script under pyconfd's etc directory. They are just python plugins, so nothing special going on there.

The default haproxy config template under /etc/pyconfd/templates is based on a few containers that were being experimented with, but may not be present in your cluster, so feel free to remove those examples.

Eventually it would be nice if consul had event hooks so that pyconfd didn't have to poll forever on a loop.

# fig

The consuljoin.sh script assumes that the container has been launched through fig. Every container in the cluster needs to be told to connect to at least one consul server, the IP address of which is something fig provides through the environment variable mentioned in the consuljoin.sh script. Note that the consul server is provided by a container that is a derivative of this container, but the files are not in this repository. (Bug kanzure if this second repository hasn't been pushed yet.) The main difference between the consulserver container and this basenode container is that there's an additional param passed into consul (maybe it's --bootstrap-expect 1) and haproxy/pyconfd are both disabled since there's no reason to have them active in that container anyway.

Here's an example for fig users of a container providing an "nginx" service that connects to a consulserver container:

``` yaml
consulserver:
    build: consul-server/

    expose:
        # consul RPC
        - "8400"

        # consul HTTP
        - "8500"

        # consul DNS (UDP not TCP)
        - "8600"

nginx:
    build: nginx/
    ports:
        - "8080:8080"
    links:
        - consulserver
        - ui:ui
        - api:api
```

# security?

Follow the security guidelines from [phusion/baseimage](https://github.com/phusion/baseimage-docker). Additionally, there are new concerns introduced in this repository. Perhaps the most relevant is that someone has left their public key in the ssh/ folder, which will give them access if they ever have a connection to the containers. There are other security concerns that are not listed here, such as consul (HTTPS is an option) and pyconfd which has not been reviewed for weaknesses. Actually, assume everything here hasn't been reviewed for security weaknesses. There-- now I have impunity, right?

# usage

Here is how you do things.

## build

Build this container first before building any Dockerfile that has the "FROM basenode" line.

``` bash
docker build -t basenode .
```

## run

``` bash
docker run --rm=true -i -t basenode /bin/bash
```

## using

To extend from this container, build it and then in another Dockerfile write near the top:

```
FROM basenode
```

## ssh

Just grep for the IP address and then ssh into the container. Also there is a thing called nsenter?

``` bash
sudo docker ps .. something ..
```

# license

Dunno, suggest something.
