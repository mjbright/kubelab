#FROM leandatascience/jupyterlab-ds:latest
FROM mjbright/kubelab:1.15.0

ENV MAIN_PATH=/usr/local/bin/jupyterkubelab
ENV LIBS_PATH=${MAIN_PATH}/libs
ENV CONFIG_PATH=${MAIN_PATH}/config
ENV NOTEBOOK_PATH=${MAIN_PATH}/notebooks

EXPOSE 8888

CMD cd ${MAIN_PATH} && sh config/run_jupyter.sh
