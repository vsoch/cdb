FROM bitnami/minideb:stretch as generator
# docker build -t data-container .
ENV PATH /opt/conda/bin:${PATH}
ENV LANG C.UTF-8
RUN /bin/bash -c "install_packages wget git ca-certificates && \
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh"

# TODO this should install from pip
COPY . /tmp/repo
WORKDIR /tmp/repo
RUN pip install .[all]

WORKDIR /data
COPY ./tests/data .
RUN cdb generate /data --out /db.go

FROM golang:1.13-alpine3.10 as builder
COPY --from=generator /db.go /db.go
COPY --from=generator /data /data

# Dependencies
RUN apk add git && \
    go get github.com/vsoch/containerdb && \
    GOOS=linux GOARCH=amd64 go build -ldflags="-w -s" -o /db -i /db.go

FROM scratch
LABEL MAINTAINER @vsoch
COPY --from=builder /data /data
COPY --from=builder /db /db

CMD ["/db"]
