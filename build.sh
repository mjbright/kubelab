#!/bin/bash

PROMPTS=1

## -- Functions: -----------------------------------------------------------------

kube1p15() {
    VERSION=1.15.11
    BUILD_ARGS="--build-arg KUBECTL_V=$VERSION
    --build-arg HELM_V=v3.1.2 --build-arg KUBECTX_V=0.8.0 --build-arg KUBEBOX_V=v0.7.0
    --build-arg DOCKER_CE_V=19.03.8 --build-arg DOCKER_MACHINE_V=0.16.1 --build-arg DOCKER_COMPOSE_V=1.24.1"
}

kube1p16() {
    VERSION=1.16.8
    BUILD_ARGS="--build-arg KUBECTL_V=$VERSION
    --build-arg HELM_V=v3.1.2 --build-arg KUBECTX_V=0.8.0 --build-arg KUBEBOX_V=v0.7.0
    --build-arg DOCKER_CE_V=19.03.8 --build-arg DOCKER_MACHINE_V=0.16.1 --build-arg DOCKER_COMPOSE_V=1.24.1"
}

kube1p17() {
    VERSION=1.17.4
    BUILD_ARGS="--build-arg KUBECTL_V=$VERSION
    --build-arg HELM_V=v3.1.2 --build-arg KUBECTX_V=0.8.0 --build-arg KUBEBOX_V=v0.7.0
    --build-arg DOCKER_CE_V=19.03.8 --build-arg DOCKER_MACHINE_V=0.16.1 --build-arg DOCKER_COMPOSE_V=1.24.1"
}


kube1p18() {
    VERSION=1.18.0
    BUILD_ARGS="--build-arg KUBECTL_V=$VERSION
    --build-arg HELM_V=v3.1.2 --build-arg KUBECTX_V=0.8.0 --build-arg KUBEBOX_V=v0.7.0
    --build-arg DOCKER_CE_V=19.03.8 --build-arg DOCKER_MACHINE_V=0.16.1 --build-arg DOCKER_COMPOSE_V=1.24.1"
}



LATEST_KUBECTL_V=$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)

# Function: press <prompt>
# Prompt user to press <return> to continue
# Exit if the user enters q or Q
#
press()
{
    [ ! -z "$1" ] && echo "$*"
    [ $PROMPTS -eq 0 ] && return 0
    echo "Press <return> to continue"

    read _DUMMY
    [ "$_DUMMY" = "s" ] && return 1
    [ "$_DUMMY" = "S" ] && return 1
    [ "$_DUMMY" = "q" ] && exit 0
    [ "$_DUMMY" = "Q" ] && exit 0

    return 0
}

RUN() {
    CMD="$*"
    press "About to run command 
-- $CMD" || { echo "Skipping ... "; return 1; }

    $CMD
}

build_kubelab() {
    RUN docker build -f Dockerfile.kubelab $BUILD_ARGS -t mjbright/kubelab:$VERSION . &&
        RUN docker login &&
        RUN docker push mjbright/kubelab:$VERSION
}

## -- Args: ----------------------------------------------------------------------

[ "$1" = "-np" ] && PROMPTS=0

## -- Main: ----------------------------------------------------------------------
#RUN docker build -t mjbright/skippbox-jupyter .
kube1p15 && build_kubelab &&
    kube1p16 && build_kubelab &&
    kube1p17 && build_kubelab  &&
    kube1p18 && build_kubelab  &&
    RUN docker tag  mjbright/kubelab:$VERSION mjbright/kubelab:latest &&
    RUN docker push mjbright/kubelab:latest

## echo; echo  "-- ./REDEPLOY.sh -a"
## ./REDEPLOY.sh -a

#echo
#RUN ./REDEPLOY.sh -a

