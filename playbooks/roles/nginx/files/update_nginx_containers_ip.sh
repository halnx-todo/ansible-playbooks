#!/bin/bash
#
# this script updates nginx configuration with correct container IP address in upstreams
# 
#
#

NGINX_SITE_ENABLED="/opt/data/nginx/conf/sites-enabled"


for NGINX_CONF in $(ls ${NGINX_SITE_ENABLED}); do
  NGINX_CONF_PATH="${NGINX_SITE_ENABLED}/${NGINX_CONF}";
  echo "for ${NGINX_CONF}"
  for DOCKER_ID in $(docker ps -a -q); do
    # debug 
    #docker inspect ${DOCKER_ID} --format '{{.Name}} {{.State.Running}} {{.ID}} {{ .NetworkSettings.IPAddress }}:{{ range $contPort, $hostPorts := .NetworkSettings.Ports }}{{$contPort}}{{end}}';
    #

    D_CONT_NAME=$(docker inspect ${DOCKER_ID} --format '{{.Name}}');
    D_CONT_IS_RUNNING=$(docker inspect ${DOCKER_ID} --format '{{.State.Running}}');
    D_CONT_IP=$(docker inspect ${DOCKER_ID} --format '{{ .NetworkSettings.IPAddress }}');
    D_CONT_NB_PORTS_USER=$(docker inspect ${DOCKER_ID} --format json | jq '.[]?.NetworkSettings.Ports|length')
    D_CONT_PORTS=$(docker inspect ${DOCKER_ID} --format '{{ range $contPort, $hostPorts := .NetworkSettings.Ports }}{{$contPort}}{{end}}');

    if [[ ${D_CONT_NB_PORTS_USER} != 1 ]]; then
      # port is formated XXXX/tcp ie 8080/tcp so ${D_CONT_PORTS%/*} will only keep before /
      # convention expect only one open tcp port
      echo " ${D_CONT_NAME} with ${DOCKER_ID} has ${D_CONT_NB_PORTS_USER} port(s) ${D_CONT_PORTS}";
      continue;
    fi

    if [[ ${D_CONT_IS_RUNNING} = 'true' ]]; then
      echo " ${D_CONT_NAME} with ${DOCKER_ID} is running ";
      NGINX_CONT_ID=$(grep "${DOCKER_ID}" ${NGINX_CONF_PATH});

      if [[ ${NGINX_CONT_ID} != "" ]]; then
        echo "${NGINX_CONF_PATH} updated";
        sed -i -E "s@.*server ([0-9]{1,3}.[0-9]{1,3}.[0-9\]{1,3}.[0-9]{1,3}):[0-9].*@\        server ${D_CONT_IP}:${D_CONT_PORTS%/*} max_fails=0; # ${DOCKER_ID} on $(hostname) at $(date -Iseconds)@g" ${NGINX_CONF_PATH};
      fi

    else
      echo " ${D_CONT_NAME} with ${DOCKER_ID} is not running ";
    fi
  done
done
