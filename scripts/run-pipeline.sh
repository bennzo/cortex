#!/bin/bash

set -e
DOCKER_PREFIX="advsysdsgn_beno"
PYTHON_IMAGE="${DOCKER_PREFIX}_python_image"
PYTHON_CONTAINER="${DOCKER_PREFIX}_python"
DB_CONTAINER="${DOCKER_PREFIX}_db"
MQ_CONTAINER="${DOCKER_PREFIX}_mq"

function build_docker() {
  if [[ "$(docker images -q ${PYTHON_IMAGE} 2> /dev/null)" == "" ]]; then
    echo "Docker image for cortex components does not exist."
    read -p "Would you like to build it now? [y/n]" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      docker build --tag ${PYTHON_IMAGE} .
    else
      echo "Aborting deployment..."
      exit 1
    fi
  fi
}

function run_pipeline() {
  echo "Deploying full pipeline..."
  build_docker

  # Deploying database and message queue
  deploy_db
  deploy_mq

  echo "Waiting 10 seconds before deploying other components"
  sleep 10

  # Deploying parsers
  for parser in "pose" "feelings" "image_color" "image_depth"; do
    deploy_component "parsers" $parser
  done

  # Deploying rest of components
  for comp in "saver" "server" "api" "gui"; do
    deploy_component $comp
  done

  echo "Pipeline deployment finished successfully."
}

function deploy_db() {
  docker run -d -p 27017:27017 --name ${DB_CONTAINER} mongo:latest
  echo ">> Database set up and running! <<"
}

function deploy_mq() {
  docker run -d -p 5672:5672 --name ${MQ_CONTAINER} rabbitmq:latest
  echo ">> MessageQueue set up and running! <<"
}


function deploy_component() {
  build_docker
  comp=$1
  subcomp=$2

  case "$comp" in

  "server" ) cmd="python -u -m cortex.server run-server -h '127.0.0.1' -p 8000 'rabbitmq://127.0.0.1:5672/'";;
  "parsers" ) cmd="python -m cortex.parsers run-parser ${subcomp} 'rabbitmq://127.0.0.1:5672/'"; subcomp="_${subcomp}";;
  "saver" ) cmd="python -m cortex.saver run-saver 'mongodb://127.0.0.1:27017' 'rabbitmq://127.0.0.1:5672/'";;
  "api" ) cmd="python -m cortex.api run-server -h '127.0.0.1' -p 5000 -d 'mongodb://127.0.0.1:27017'";;
  "gui" ) cmd="python -m cortex.gui run-server -h '127.0.0.1' -p 8080 -H '127.0.0.1' -P 5000";;
  "*" ) echo "Unknown component. Exiting."; exit 1;;

  esac

  cont_name=${DOCKER_PREFIX}_${comp}${subcomp}
  mount="type=bind,source="$(pwd)"/data,target=/usr/cortex/data"
  dockerrun="docker run -dit
                        --network host
                        -e PYTHONUNBUFFERED=0
                        --mount ${mount}
                        --name ${cont_name}
                        advsysdsgn_beno_python_image
                        ${cmd}"
  echo $dockerrun
  eval $dockerrun
  echo $?
  echo ">> ${comp}${subcomp} set up and running! <<"
}

function component_menu() {
  prompt="Which component would you like to deploy:"
  options=("database" "message queue" "server" "api" "gui" "saver" "parsers")

  parser_prompt="Please choose a parser:"
  parsers=("pose" "feelings" "image_color" "image_depth")

  PS3="$prompt "
  select opt in "${options[@]}" "Exit"; do

      case "$REPLY" in

      1 ) deploy_db; break;;
      2 ) deploy_mq; break;;
      [3-6] ) deploy_component "$opt"; break;;
      7 )
          PS3="$parser_prompt "
          select parser in "${parsers[@]}" "Exit"; do
              case "$REPLY" in

              [1-4] ) deploy_component "$opt" "$parser"; break;;

              $(( ${#parsers[@]}+1 )) ) echo "Goodbye!"; break ;;
              *) echo "Invalid option. Try another one."; continue;;

              esac
          done; break;;

      $(( ${#options[@]}+1 )) ) echo "Goodbye!"; break;;
      *) echo "Invalid option. Try another one."; continue;;

      esac
      return "$REPLY"

  done
}

function clean_containers() {
  echo "The following docker containers will be removed:"
  docker ps --filter name=advsysdsgn_beno --format '{{.Names}}'
  read -p "Would you like to proceed? [y/n]" -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker ps --filter name=advsysdsgn_beno -aq | xargs docker stop | xargs docker rm
  else
    echo "Aborting removal..."
    exit 1
  fi
}

function clean_image() {
  echo "The following docker image will be removed:"
  echo "advsysdsgn_beno_python_image:latest"
  read -p "Would you like to proceed? [y/n]" -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker image rm --force advsysdsgn_beno_python_image:latest
  else
    echo "Aborting removal..."
    exit 1
  fi
}

function main_menu() {
  title="Hello Madame/Sir, how would you like to set up the hivemind?"
  prompt="Pick an option:"
  options=("Run Full Pipeline" "Run Single Component" "Clean related docker containers" "Remove related python docker image")

  echo "$title"
  PS3="$prompt "
  select opt in "${options[@]}" "Exit"; do

      case "$REPLY" in

      1 ) run_pipeline; break;;
      2 ) component_menu; break;;
      3 ) clean_containers; break;;
      4 ) clean_image; break;;

      $(( ${#options[@]}+1 )) ) echo "Goodbye!"; break;;
      *) echo "Invalid option. Try another one."; continue;;

      esac

  done
}

main_menu