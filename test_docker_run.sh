
CMD="$*"

#docker run --rm --name jk -p 9999:8888 mjbright/jupyterkubelab:1.18.0
docker run -it --rm --name jk -p 9999:8888 mjbright/jupyterkubelab:1.15.11 $CMD


