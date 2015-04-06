#!/bin/bash

ZK_START_SCRIPT="/opt/zookeeper/zookeeper*/bin/zkServer.sh"
KAFKA_ROOT="/opt/kafka/kafka*"
# Confluent 1.0 schema registry is compatible with Kafka 0.8.1.1
CONFLUENT_ROOT="/opt/confluent/confluent*"

function start_kafka {
    echo "Starting Kafka"
    $KAFKA_ROOT/bin/kafka-server-start.sh $KAFKA_ROOT/config/server.properties &> /dev/null &

    echo "Starting Kafka schema registry"
    $CONFLUENT_ROOT/bin/schema-registry-start $CONFLUENT_ROOT/etc/schema-registry/schema-registry.properties &> /dev/null &
}

function start_zoookeeper {
    echo "Starting Zookeeper"
    $ZK_START_SCRIPT start
}

function start {
    start_zoookeeper
    start_kafka
}

function set_kafka_broker_pid {
    unset kafka_broker_pid
    kafka_broker_pid=$(ps ax | grep -i 'kafka\.Kafka' | grep java | grep -v grep | awk '{print $1}')
}

function stop_kafka {
    echo "Stopping Kafka schema registry"
    $CONFLUENT_ROOT/bin/schema-registry-stop

    echo "Stopping Kafka"
    $KAFKA_ROOT/bin/kafka-server-stop.sh
    sleep 1
    set_kafka_broker_pid
    if [ ! -z $kafka_broker_pid ]
    then 
        echo "Kafka is still running, trying with TERM"
        kill -TERM $kafka_broker_pid
    fi 
    sleep 1
    set_kafka_broker_pid
    if [ ! -z $kafka_broker_pid ]
    then 
        echo "Kafka is still running, trying with KILL"
        kill -KILL $kafka_broker_pid
    fi 
}

function stop_zookeeper {
    echo "Stopping Zookeeper"
    $ZK_START_SCRIPT stop
}

function stop {
    stop_kafka
    stop_zookeeper
}

function print_usage {
    # echo $"Usage: $0 {start|stop|restart|status}"
    echo $"Usage: $0 {start|stop|restart}"
}

################
# Main 
################
case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  # TODO
  # status)
  #   get_status
  #   ;;
  restart)
    stop
    start
    ;;
  *)
    print_usage
    # Do not exit so this script can be used as a lib too
    # EXIT_CODE=2
esac

# Do not exit so this script can be used as a lib too
# exit $EXIT_CODE