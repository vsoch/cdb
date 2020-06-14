---
layout: post
title:  "Singularity simple database example"
date: 2020-06-13 15:00:46
author: "@vsoch"
categories:
- Tutorial
---


In this example, we will start with a basic folder of [data](https://github.com/vsoch/cdb/tree/master/examples/docker-simple/data) and generate a data container for it. Singularity
is especially powerful here because our container will be read only, meaning that we know for sure
it won't be changed as long as we maintain the same file.

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

### The Singularity Recipe

Let's break the Singularity recipe down into it's components. This first section will install
the `cdb` software, add the data, and generate a GoLang script to compile, which will generate an in-memory database.

```
Bootstrap: docker
From: bitnami/minideb:stretch
Stage: generator

# sudo singularity build data-container Singularity

%setup
    mkdir -p ${SINGULARITY_ROOTFS}/data

%files
  ./data /data

%post
export PATH=/opt/conda/bin:${PATH}
export LANG=C.UTF-8
/bin/bash -c "install_packages wget git ca-certificates && \
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh"

pip install cdb==0.0.1
cdb generate /data --out /entrypoint.go
```

Next we want to build that file, `entrypoint.go`, and also carry the data forward:

```
Bootstrap: docker
From: golang:1.13-alpine3.10
Stage: builder

%files from generator
    /entrypoint.go /entrypoint.go
    /data /data

%post
apk add git && \
    go get github.com/vsoch/containerdb && \
    GOOS=linux GOARCH=amd64 go build -ldflags="-w -s" -o /entrypoint -i /entrypoint.go
```

Finally, we want to add just the executable and data to a scratch container 
(meaning it doesn't have an operating system)

```
%files from builder
    /entrypoint /entrypoint
    /data /data
```

We will then interact with the `/entrypoint` binary. Notice that we could
also a little hack at the end - if we add a `%runscript` then
it's going to try and interact with some `/bin/sh` and spit out an error.
So instead, we could just create the entrypoint executable to be `/bin/sh`!

```
%setup
    mkdir -p ${SINGULARITY_ROOTFS}/bin

%files from builder
    /entrypoint /entrypoint
    /data /data
```

I chose to not do this, because I don't mind running singularity exec instead.
I think we would also need a way to pass the arguments to /bin/sh (I haven't tested this yet, care to try it out?)
Also note that you need a fairly [recent version](https://github.com/hpcng/singularity-userdocs/pull/328/files) of Singularity to have support for scratch. And that's it!  Take a look at the entire [Singularity recipe](https://github.com/vsoch/cdb/tree/master/examples/singularity-simple/Singularity) if you are interested.

### Building

Let's build it!

```bash
$ sudo singularity build data-container Singularity
```

We then have a simple way to do the following:

### Interaction with the single container

**metadata**

If we just run the container, we get a listing of all metadata alongside the key.
I'm not sure how to silence the warnings, I'm sure there is a way

```bash
$ singularity exec data-container /entrypoint
WARNING: passwd file doesn't exist in container, not updating
WARNING: group file doesn't exist in container, not updating
/data/avocado.txt {"size": 9, "sha256": "327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4"}
/data/tomato.txt {"size": 8, "sha256": "3b7721618a86990a3a90f9fa5744d15812954fba6bb21ebf5b5b66ad78cf5816"}
```

**list** 

We can also just list data files with `-ls`

```bash
$ singularity exec data-container /entrypoint -ls
WARNING: passwd file doesn't exist in container, not updating
WARNING: group file doesn't exist in container, not updating
/data/avocado.txt
/data/tomato.txt
```

**orderby**

Or we can list ordered by one of the metadata items:

```bash
$ singularity exec data-container /entrypoint -metric size
WARNING: passwd file doesn't exist in container, not updating
WARNING: group file doesn't exist in container, not updating
Order by size
/data/tomato.txt: {"size": 8, "sha256": "3b7721618a86990a3a90f9fa5744d15812954fba6bb21ebf5b5b66ad78cf5816"}
/data/avocado.txt: {"size": 9, "sha256": "327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4"}
```

**search**

Or search for a specific metric based on value.

```bash
$ singularity exec data-container /entrypoint -metric size -search 8
WARNING: passwd file doesn't exist in container, not updating
WARNING: group file doesn't exist in container, not updating
/data/tomato.txt 8


$ singularity exec data-container /entrypoint -metric sha256 -search 8
WARNING: passwd file doesn't exist in container, not updating
WARNING: group file doesn't exist in container, not updating
/data/avocado.txt 327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4
/data/tomato.txt 3b7721618a86990a3a90f9fa5744d15812954fba6bb21ebf5b5b66ad78cf5816
```

**get**

Or we can get a particular file metadata by it's name:

```bash
$ singularity exec data-container /entrypoint -get /data/avocado.txt
/data/avocado.txt {"size": 9, "sha256": "327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4"}
```

or a partial match:

```bash
$ singularity exec data-container /entrypoint -get /data/avocado.txt -get /data/
/data/avocado.txt {"size": 9, "sha256": "327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4"}
/data/tomato.txt {"size": 8, "sha256": "3b7721618a86990a3a90f9fa5744d15812954fba6bb21ebf5b5b66ad78cf5816"}
```

**start**

The start command is intended to keep the container running, if we are using
it with an orchestrator.

```bash
$ singularity exec data-container /entrypoint -get /data/avocado.txt -start
```

### Orchestration

We haven't created the singularity-compose recipes yet, likely we would need
to have a custom `%startscript` to not use /bin/sh but instead to target
the entrypoint. Please take a shot or suggest ideas!

### Overview

This is very simple example of building a small data container to query and
show metadata for two files. Although this example is simple, the idea is powerful because we 
are able to keep data and interact with it without needing an operating system.
Combined with other metadata or data organizational standards, this could be
a really cool approach to develop data containers optimized to interact
with a particular file structure or workflow. How will that work in particular?
It's really up to you! The `cdb` software can take custom functions
for generation of metadata and templates for generating the GoLang script
to compile, so the possibilities are very open.

Please [contribute](https://github.com/vsoch/cdb) to the effort! I'll be slowly
adding examples as I create them.
