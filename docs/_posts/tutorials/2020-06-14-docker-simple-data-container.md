---
layout: post
title:  "Docker simple database example"
date: 2020-06-13 16:00:46
author: "@vsoch"
categories:
- News
---


In this example, we will start with a basic folder of [data](https://github.com/vsoch/cdb/tree/master/examples/docker-simple/data) and generate a data container for it.

### What is a Data Container?

A data container is generally an operating-system-less container that is optimized
to provide data, either for query/search, or binding for analysis. The qualities of
the data container should be:

 1. It can be mounted to containers with operating systems to run analysis
 2. It can be interacted with on it's own to search metadata about the data
 3. It should not have an operating system.


### How do we generate one?

The generation is fairly simple! It comes down to a three step multistage build:

 1. **Step 1** We install [cdb](https://github.com/vsoch/cdb) to generate a GoLang template for an [in-memory database](https://github.com/vsoch/containerdb) for our data) 
 2. **Step 2** We compile the binary into an entrypoint
 3. **Step 3** We add the data and the binary entrypoint to a scratch container (no operating system).

And then we interact with it! This tutorial will show you the basic steps to
perform the multistage-build using a simple [Dockerfile](https://github.com/vsoch/cdb/tree/master/examples/docker-simple/Dockerfile) along with the data folder.

### The Dockerfile

Let's break the dockerfile down into it's components. This first section will install
the `cdb` software, add the data, and generate a GoLang script to compile, which will generate an in-memory database.

```
FROM bitnami/minideb:stretch as generator
# docker build -t data-container .
ENV PATH /opt/conda/bin:${PATH}
ENV LANG C.UTF-8
RUN /bin/bash -c "install_packages wget git ca-certificates && \
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh"

# install cdb (update version if needed)
RUN pip install cdb==0.0.1

# Add the data to /data (you can change this)
WORKDIR /data
COPY ./data .
RUN cdb generate /data --out /entrypoint.go
```

Next we want to build that file, `entrypoint.go`, and also carry the data forward:

```
FROM golang:1.13-alpine3.10 as builder
COPY --from=generator /entrypoint.go /entrypoint.go
COPY --from=generator /data /data

# Dependencies
RUN apk add git && \
    go get github.com/vsoch/containerdb && \
    GOOS=linux GOARCH=amd64 go build -ldflags="-w -s" -o /entrypoint -i /entrypoint.go
```

Finally, we want to add just the executable and data to a scratch container 
(meaning it doesn't have an operating system)

```
FROM scratch
LABEL MAINTAINER @vsoch
COPY --from=builder /data /data
COPY --from=builder /entrypoint /entrypoint

ENTRYPOINT ["/entrypoint"]
```

And that's it!  Take a look at the entire [Dockerfile](https://github.com/vsoch/cdb/tree/master/examples/docker-simple/Dockerfile) if you are interested.

### Building

Let's build it!

```bash
$ docker build -t data-container .
```

We then have a simple way to do the following:

### Interaction with the single container

**metadata**

If we just run the container, we get a listing of all metadata alongside the key.

```bash
$ docker run data-container
/data/avocado.txt {"size": 9, "sha256": "327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4"}
/data/tomato.txt {"size": 8, "sha256": "3b7721618a86990a3a90f9fa5744d15812954fba6bb21ebf5b5b66ad78cf5816"}
```

**list** 

We can also just list data files with `-ls`

```bash
$ docker run data-container -ls
/data/avocado.txt
/data/tomato.txt
```

**orderby**

Or we can list ordered by one of the metadata items:

```bash
$ docker run data-container -metric size
Order by size
/data/tomato.txt: {"size": 8, "sha256": "3b7721618a86990a3a90f9fa5744d15812954fba6bb21ebf5b5b66ad78cf5816"}
/data/avocado.txt: {"size": 9, "sha256": "327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4"}
```

**search**

Or search for a specific metric based on value.

```bash
$ docker run data-container -metric size -search 8
/data/tomato.txt 8

$ docker run entrypoint -metric sha256 -search 8
/data/avocado.txt 327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4
/data/tomato.txt 3b7721618a86990a3a90f9fa5744d15812954fba6bb21ebf5b5b66ad78cf5816
```

**get**

Or we can get a particular file metadata by it's name:

```bash
$ docker run data-container -get /data/avocado.txt
/data/avocado.txt {"size": 9, "sha256": "327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4"}
```

or a partial match:

```bash
$ docker run data-container -get /data/
/data/avocado.txt {"size": 9, "sha256": "327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4"}
/data/tomato.txt {"size": 8, "sha256": "3b7721618a86990a3a90f9fa5744d15812954fba6bb21ebf5b5b66ad78cf5816"}
```

**start**

The start command is intended to keep the container running, if we are using
it with an orchestrator.

```bash
$ docker run data-container -start
```

### Orchestration

It's more likely that you'll want to interact with files in the container via
some analysis, or more generally, another container. Let's put together
a quick `docker-compose.yml` to do exactly that.

```
version: "3"
services:
  base:
    restart: always
    image: busybox
    entrypoint: ["tail", "-f", "/dev/null"]
    volumes:
      - data-volume:/data

  data:
    restart: always
    image: data-container
    command: ["-start"]
    volumes:
      - data-volume:/data

volumes:
  data-volume:
```

Notice that the command for the data-container to start is `-start`, which
is important to keep it running. After building our `data-container`, we can then bring these containers up:


```bash
$ docker-compose up -d
Starting docker-simple_base_1   ... done
Recreating docker-simple_data_1 ... done
```
```bash
$ docker-compose ps
        Name                Command         State   Ports
---------------------------------------------------------
docker-simple_base_1   tail -f /dev/null    Up           
docker-simple_data_1   /entrypoint -start   Up           
```

We can then shell inside and see our data!

```bash
$ docker exec -it docker-simple_base_1 sh
/ # ls /data/
avocado.txt  tomato.txt
```

The metadata is still available for query by interacting with the data-container
entrypoint:

```bash
$ docker exec docker-simple_data_1 /entrypoint -ls
/data/avocado.txt
/data/tomato.txt
```

Depending on your use case, you could easily make this available inside the
other container.

### Overview

This is very simple example of building a small data container to query and
show metadata for two files, and then bind that data to another orchestration
setup. Although this example is simple, the idea is powerful because we 
are able to keep data and interact with it without needing an operating system.
Combined with other metadata or data organizational standards, this could be
a really cool approach to develop data containers optimized to interact
with a particular file structure or workflow. How will that work in particular?
It's really up to you! The `cdb` software can take custom functions
for generation of metadata and templates for generating the GoLang script
to compile, so the possibilities are very open.

Please [contribute](https://github.com/vsoch/cdb) to the effort! I'll be slowly
adding examples as I create them.
