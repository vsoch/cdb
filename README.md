# Container Database (cdb)

This is the Python support tool for [containerdb](https://github.com/vsoch/containerdb)
to support generation of [data containers](https://github.com/singularityhub/data-container).
Python is more friendly to generating arbitrary data structures, and is popular among the
data science community, so I chose it for metadata generation instead of using GoLang.

[![PyPI version](https://badge.fury.io/py/cdb.svg)](https://badge.fury.io/py/cdb)

> Have your data and use it too!

![assets/img/logo/logo.png](assets/img/logo/logo.png)

For documentation and full examples see [vsoch.github.io/cdb](https://vsoch.github.io/cdb). These
examples are also available in the [examples](examples) folder.

## Getting Started

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
perform the multistage-build using a simple [Dockerfile](https://github.com/vsoch/cdb/tree/master/examples/docker-simple/Dockerfile) along with the data folder. The [Dockerfile](Dockerfile) in the base of the repository also is a good example.

## Usage

### Docker Usage

The intended usage is via Docker, so you don't need to worry about installation of
Python, GoLang, and multistage builds to basically:

 1. Generate a db.go template
 2. Compile it
 3. Add to scratch with data as data container entrypoint.

Thus, to run the dummy example here using the [Dockerfile](Dockerfile):

```bash
$ docker build -t data-container .
```

We then have a simple way to do the following:

**metadata**

If we just run the container, we get a listing of all metadata alongside the key.

```bash
$ docker run entrypoint 
/data/avocado.txt {"size": 9, "sha256": "327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4"}
/data/tomato.txt {"size": 8, "sha256": "3b7721618a86990a3a90f9fa5744d15812954fba6bb21ebf5b5b66ad78cf5816"}
```

**list** 

We can also just list data files with `-ls`

```bash
$ docker run entrypoint -ls
/data/avocado.txt
/data/tomato.txt
```

**orderby**

Or we can list ordered by one of the metadata items:

```bash
$ docker run entrypoint -metric size
Order by size
/data/tomato.txt: {"size": 8, "sha256": "3b7721618a86990a3a90f9fa5744d15812954fba6bb21ebf5b5b66ad78cf5816"}
/data/avocado.txt: {"size": 9, "sha256": "327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4"}
```

**search**

Or search for a specific metric based on value.

```bash
$ docker run entrypoint -metric size -search 8
/data/tomato.txt 8

$ docker run entrypoint -metric sha256 -search 8
/data/avocado.txt 327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4
/data/tomato.txt 3b7721618a86990a3a90f9fa5744d15812954fba6bb21ebf5b5b66ad78cf5816
```

**get**

Or we can get a particular file metadata by it's name:

```bash
$ docker run entrypoint -get /data/avocado.txt
/data/avocado.txt {"size": 9, "sha256": "327bf8231c9572ecdfdc53473319699e7b8e6a98adf0f383ff6be5b46094aba4"}
```

or a partial match:

```bash
$ docker run entrypoint -get /data/
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
other container. This is very simple usage, but the idea is powerful! We can interact with the dataset
and search it without needing an operating system. It follows that we can develop
customized data-containers based on the format / organization of the data inside 
(e.g., a data-container that knows how to expose inputs, outputs, etc.)


## Python Usage

The above doesn't require you to install the Container Database (cdb) metadata
generator, however if you want to (to develop or otherwise interact) you
can do the following. First, install cdb from pypi or a local repository:

```bash
$ pip install cdb
```
or

```bash
git clone git@github.com:vsoch/cdb
cd cdb
pip install -e .
```

### Command Line 

The next step is to generate the goLang file to compile.
You'll next want to change directory to somewhere you have a dataset folder.
For example, in [tests](tests) we have a dummy "data" folder.

```bash
cd tests/
```

We might then run `cdb generate` to create a binary for our container, targeting
the [tests/data](tests/data) folder:

```bash
$ cdb generate data --out db.go
```

The db.go file is then in the present working directory. You can either
build it during a multistage build as is done in the [Dockerfile](Dockerfile),
or do it locally with your own GoLang install and then add to the container.
For example, to compile:

```bash
go get github.com/vsoch/containerdb && \
GOOS=linux GOARCH=amd64 go build -ldflags="-w -s" -o /db -i /db.go
```

And then a very basic Dockerfile would need to add the data at the path specified,
and the compiled entrypoint.

```bash
FROM scratch
WORKDIR /data
COPY data/ .
COPY db /db
CMD ["/db"]
```

A more useful entrypoint will be developed soon! This is just a very
basic start to the library.

### Python

You can run the same generation functions interactively with Python.

```python
from cdb.main import ContainerDatabase
db = ContainerDatabase(path="data")
# <cdb.main.ContainerDatabase at 0x7fcaa9cb8950>
```

View that there is a files generator at `db.files`

```python
db.files
<generator object recursive_find at 0x7fcaaa4ae950>
```


And then generate! If you don't provide an output file, a string will be returned.
Otherwise, the output file name is returned.

```python
output = db.generate(output="db.go", force=True)
```

Currently, functions for parsing metadata are named in [cdb/functions.py](cdb/functions.py),
however you can also define a custom import path. This has not yet been tested 
and will be soon. We will also be added more real world examples soon.

## License

 * Free software: MPL 2.0 License
