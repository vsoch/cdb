# Container Database (cdb)

This is the Python support tool for [containerdb](https://github.com/vsoch/containerdb)
to support generation of [data containers](https://github.com/singularityhub/data-container).
Python is more friendly to generating arbitrary data structures, and is popular among the
data science community, so I chose it for metadata generation instead of using GoLang.

[![PyPI version](https://badge.fury.io/py/cdb.svg)](https://badge.fury.io/py/cdb)


Generation works as follows:

 1. The library will take as input some data folder
 2. The user defines a function to parse each file and generate a dataset, or a default function is used
 3. A GoLang template is generated to be compiled along with [containerdb](https://github.com/vsoch/containerdb) to generate a container entrypoint and in-memory database.

## Docker Usage

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

This is very simple usage, but the idea is powerful! We can interact with the dataset
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
and will be soon.

**under development**

## TODO
 - add build prefix
 - ensure cdb installed from pip

## License

 * Free software: MPL 2.0 License
