#!/usr/bin/python2.7

'''
Local devel environment for Spark under XUbuntu 14.10

TODO: many installations follow the same pattern, this could be abstracted
'''

from fabric.api import local, task, lcd, env, abort, warn_only
import os

_install_root = "/opt"
_bashrc = os.path.join(os.environ["HOME"], ".bashrc")

_default_spark_version = "1.3.1"
_default_hadoop_version = "2.4.0"

# Store here string messages to show at the end of the execution
env.final_msgs = []

###################
# Utils
###################
def create_public_dir(dir_path, override=False):
    '''
    Creates a directory dir_path with 777 permissions
    NOTE: Local execution
    '''
    if override: 
        local("sudo rm -rf " + dir_path)
    local("sudo mkdir -p " + dir_path)
    local("sudo chmod -R 777 " + dir_path)

def download_and_uncompress(url, archive_type='tgz'):
    '''
    Downloads and uncompresses the tgz file at url, in the current directory
    NOTE: Local execution

    :param archive_type: "tgz" or "zip"
    :returns: the name of the file as returned by os.path.basename
    '''
    file_name = os.path.basename(url)
    local("wget " +  url)
    if archive_type=='tgz':
        local("tar xzf " + file_name)
    elif archive_type == 'zip':
        local("unzip " + file_name)
    else:
        abort("unknown archive_type: " + archive_type)
    return file_name

def get_child_name_with_prefix(dir_prefix): 
    '''
    NOTE: Local execution

    :retuns: the name of the child directory of the current directory 
    '''
    with warn_only(): 
        dir_name = local("ls -d */ | grep ^" + dir_prefix, capture = True)
        if dir_name.failed:
            # try with a less strict pattern
            dir_name = local("ls -d */ | grep " + dir_prefix, capture = True)
        dir_name = dir_name[:-1]
    return dir_name

def append_to_bashrc(line):
   '''
   Appends line to ~/.bashrc. Note line is not quoted, and echo will be used for this, so quote accordingly to use or avoid variable expansion as required
   NOTE: Local execution
   '''
   local("echo {line} >> ".format(line=line) + _bashrc)

def print_title(title):
    print title
    print '-' * len(title)

def add_final_msg(msg):
    env.final_msgs.append(msg)

def print_final_msgs():
    print '_' * 20
    print 
    print os.linesep.join(env.final_msgs)

def get_service_dir(service_name):
    '''
    :returns: the absolute path of the root directory of the installation of the service with name service_name
    NOTE: Local execution
    '''
    service_root = os.path.join(_install_root, service_name)
    with lcd(service_root):
        service_dir = get_child_name_with_prefix(service_name)
    return os.path.join(service_root, service_dir)

def install_simple_service(service_name, service_archive_url, archive_type='tgz'):
    '''
    Performs a simple installation of a service by just creating a new folder name service_name at _install_root, downloading the archive file at service_archive_url and uncompressing it. 
    This can be used as a first method, to later modify the configuration of the service, or adding entries to bashrc, for example
    NOTE: Local execution

   :param archive_type: "tgz" or "zip"
   :returns: a dictionary with the entries: 
        - service_path: path to the directory where the service is installed, so <service_path>/bin is usually the path with the binaries. 
        - service_root: absolute path to the root of the service installation. If is usually the parent of <service_path> but without the version info
    '''
    service_root = os.path.join(_install_root, service_name)
    create_public_dir(service_root)
    with lcd(service_root):
        archive_file = download_and_uncompress(service_archive_url, archive_type=archive_type)
        service_dir = get_child_name_with_prefix(service_name)
        local("sudo rm -f " + archive_file)
    service_abs_dir = os.path.join(service_root, service_dir)
    return { "service_path" : service_abs_dir , 
             "service_root" : service_root}

######################################
# Tasks local services operation
######################################
@task
def kafka_local_consumer(topic):
    '''
    Launches the Kafka consumer console

    NOTE: Local execution
    '''
    service_abs_dir = get_service_dir("kafka")
    local(os.path.join(service_abs_dir, "bin", "kafka-console-consumer.sh") + " --zookeeper localhost:2181 --topic {topic} --from-beginning".format(topic = topic))

@task
def kafka_local_producer(topic):
    '''
    Launches the Kafka producer console

    NOTE: Local execution
    '''
    service_abs_dir = get_service_dir("kafka")
    local(os.path.join(service_abs_dir, "bin", "kafka-console-producer.sh") + " --broker-list localhost:9092 --topic " + topic)

@task 
def kafka_create_topic(topic):
    '''
    Creates a Kafka topic with the kafka script
    '''
    service_abs_dir = get_service_dir("kafka")
    local(os.path.join(service_abs_dir, "bin", "kafka-topics.sh") + " --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic " + topic)

@task
def kafka_local_avro_consumer(topic):
    '''
    Launches the Kafka avro consumer console

    NOTE: Local execution
    '''
    service_abs_dir = get_service_dir("confluent")
    local(os.path.join(service_abs_dir, "bin", "kafka-avro-console-consumer") + " --zookeeper localhost:2181 --topic {topic} --from-beginning ".format(topic = topic))


@task
def kafka_local_producer(topic, schema):
    '''
    Launches the Kafka avro producer console

    Example: 
        fab kafka_local_producer:topic=test-avro,schema='{"type":"record"\,"name":"myrecord"\,"fields":[{"name":"f1"\,"type":"string"}]}'

    NOTE: Local execution
    '''
    print "example line:", '{"f1":"value"}'
    service_abs_dir = get_service_dir("confluent")
    local(os.path.join(service_abs_dir, "bin", "kafka-avro-console-producer") + " --broker-list localhost:9092 --topic {topic}  --property value.schema='{schema}'".format(topic = topic, schema = schema))

@task
def start_zeppelin():
    '''
    Starts Apache Zeppelin locally
    '''
    with lcd(_zeppelin_bin_path):
        local("zeppelin-daemon.sh start")

@task
def stop_zeppelin():
    '''
    Stops Apache Zeppelin locally
    '''
    with lcd(_zeppelin_bin_path):
        local("zeppelin-daemon.sh stop")

###################
# Tasks install 
###################
_maven3_url = "ftp://mirror.reverse.net/pub/apache/maven/maven-3/3.3.1/binaries/apache-maven-3.3.1-bin.tar.gz"
@task
def install_maven3(): 
    '''
    Installs maven 3
    NOTE: Local execution
    See: https://happilyblogging.wordpress.com/2011/12/13/installing-maven-on-ubuntu-10-10/
    '''
    print_title("Installing maven 3")
    _maven_root = os.path.join(_install_root, "maven3")
    create_public_dir(_maven_root)
    with lcd(_maven_root):
        mvn_tgz_file = download_and_uncompress(_maven3_url)
        mvn_dir = get_child_name_with_prefix("apache-maven-3")
        mvn_full_path = os.path.join(_maven_root, mvn_dir)
        append_to_bashrc("'export M2_HOME={mvn_full_path}'".format(mvn_full_path=mvn_full_path))
        append_to_bashrc("'export M2=$M2_HOME/bin'")
        append_to_bashrc("'PATH=$M2:$PATH'")
        local("sudo rm -f " + mvn_tgz_file)

_java_url = "http://download.oracle.com/otn-pub/java/jdk/7u75-b13/jdk-7u75-linux-x64.tar.gz"
@task
def install_java7():
    '''
    Installs the JDK for Java 7 from Oracle Corporation
    NOTE: Local execution
    NOTE: use the ideas of http://blog.kdecherf.com/2012/04/12/oracle-i-download-your-jdk-by-eating-magic-cookies/ for an automatic install
    '''
    print_title("Installing Oracle's JDK for Java 7")
    _java_root = os.path.join(_install_root, "java7")
    create_public_dir(_java_root)
    with lcd(_java_root):
        local('wget --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie;" ' + _java_url)
        java_tgz_file = os.path.basename(_java_url)
        local("tar xzf " + java_tgz_file)
        java_dir = get_child_name_with_prefix("jdk1.7")
        java_full_path = os.path.join(_java_root, java_dir)
        java_binary = os.path.join(java_full_path, "bin", "java")
        append_to_bashrc("'# Java 7 Oracle JDK'")
        append_to_bashrc("'export JAVA_ORACLE={java_full_path}'".format(java_full_path=java_full_path))
        append_to_bashrc("'export JAVA_HOME=$JAVA_ORACLE'")
        append_to_bashrc("'PATH=${JAVA_ORACLE}/bin:$PATH'")
        local("echo sudo update-alternatives --install /usr/bin/java java {java_binary} 1".format(java_binary=java_binary))
        local("echo sudo update-alternatives --set java {java_binary}".format(java_binary=java_binary))
        local("sudo rm -f " + java_tgz_file)

_zookeeper_url = "http://ftp.cixug.es/apache/zookeeper/stable/zookeeper-3.4.6.tar.gz"
@task 
def install_zookeeper(): 
    '''
    Installs a single machine zookeeper cluster for local execution

    In http://docs.hortonworks.com/HDPDocuments/HDP2/HDP-2.1.2-Win/bk_releasenotes_HDP-Win/content/ch_relnotes-hdp-2.1.1-product.html we can see HDP 2.1 uses zookeeper 3.4.5. I have only managed to find zookeeper 3.4-6 at http://zookeeper.apache.org/releases.html#download, marked as the stable version of zookeeper. 
    This code is based on the quickstart guide at http://zookeeper.apache.org/doc/r3.4.5/zookeeperStarted.html#sc_InstallingSingleMode
    '''
    print_title("Installing Zookeeper in local mode")
    zk_root = os.path.join(_install_root, "zookeeper")
    create_public_dir(zk_root)
    create_public_dir("/var/lib/zookeeper")
    with lcd(zk_root):
        zk_tgz_file = download_and_uncompress(_zookeeper_url)
        zk_dir = get_child_name_with_prefix("zookeeper")
        zk_conf_file = os.path.join(zk_dir, "conf", "zoo.cfg")
        local("echo 'tickTime=2000' >> " + zk_conf_file)
        local("echo 'dataDir=/var/lib/zookeeper' >> " + zk_conf_file)
        local("echo 'clientPort=2181' >> " + zk_conf_file)
        local("sudo rm -f " + zk_tgz_file)
    zk_dir_abs = os.path.join(zk_root, zk_dir)
    add_final_msg("Start Zookeeper with " + os.path.join(zk_dir_abs, "bin", "zkServer.sh") + " start") 
    add_final_msg("Test the Zookeeper installation with " + os.path.join(zk_dir_abs, "bin", "zkCli.sh") + ", executing 'ls /'")

kafka_url = "http://apache.rediris.es/kafka/0.8.1.1/kafka_2.10-0.8.1.1.tgz"
@task 
def install_kafka():
    '''
    Installs a single machine Kafka cluster for local execution

    Using kafka_2.10_0.8.1, as that is the dependence used currently by Spark
    Following http://kafka.apache.org/documentation.html#quickstart
    '''
    print_title("Installing Kafka in local mode")
    service_root = os.path.join(_install_root, "kafka")
    create_public_dir(service_root)
    with lcd(service_root):
        tgz_file = download_and_uncompress(kafka_url)
        service_dir = get_child_name_with_prefix("kafka")
        local("sudo rm -f " + tgz_file)
    service_abs_dir = os.path.join(service_root, service_dir)
    add_final_msg("Start Kafka (with Zookeeper already started) with " + os.path.join(service_abs_dir, "bin", "kafka-server-start.sh") + " " +  os.path.join(service_abs_dir, "config", "server.properties"))    
    add_final_msg("  - create a Kafka topic 'test' with " + os.path.join(service_abs_dir, "bin", "kafka-topics.sh") + " --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic test")
    add_final_msg("  - get a list of all the Kafka topics with " + os.path.join(service_abs_dir, "bin", "kafka-topics.sh") + " --list --zookeeper localhost:2181") 
    add_final_msg("  - consume messages from the Kafka topic 'test' with " + os.path.join(service_abs_dir, "bin", "kafka-console-consumer.sh") + " --zookeeper localhost:2181 --topic test --from-beginning")
    add_final_msg("  - produce messages for the Kafka topic 'test' with " + os.path.join(service_abs_dir, "bin", "kafka-console-producer.sh") + " --broker-list localhost:9092 --topic test ")
    add_final_msg("Kafka logs are stored at /tmp/kafka-logs")
    print_final_msgs() # FIXME delete

spark_url = "http://ftp.cixug.es/apache/spark/spark-1.3.1/spark-1.3.1-bin-hadoop2.4.tgz"
@task
def install_spark(override = True):
    '''
    Installs the spark REPL and job submit CLI

    NOTE: Local execution
    '''
    print_title("Installing Spark in local mode")
    service_root = os.path.join(_install_root, "spark")
    create_public_dir(service_root, override=override)
    with lcd(service_root):
        tgz_file = download_and_uncompress(spark_url)
        service_dir = get_child_name_with_prefix("spark")
        local("sudo rm -f " + tgz_file)
    service_abs_dir = os.path.join(service_root, service_dir)
    append_to_bashrc("'# Spark'")
    append_to_bashrc("'export SPARK_HOME={path}'".format(path=service_abs_dir))
    append_to_bashrc("'PATH=${SPARK_HOME}/bin:$PATH'")

_confluent_quickstart_url = "http://packages.confluent.io/archive/1.0/confluent-1.0-2.10.4.zip"
@task
def install_confluent_quickstart(): 
    '''
    Installs locally the confluent_quickstart following http://confluent.io/docs/current/quickstart.html

    This might well replace the Kafka and / or zookeeper installation, but for now I prefer depending as less as possible from particular distributions. Also Spark KafkaUtils work only with a particular version of Kafka
    '''
    print_title("Installing Confluent Quickstart in local mode")
    install_simple_service("confluent", _confluent_quickstart_url, archive_type='zip')

_sbt_url = "https://repo.typesafe.com/typesafe/ivy-releases/org.scala-sbt/sbt-launch/0.13.8/sbt-launch.jar?_ga=1.141836786.1544579142.1428429429"
@task
def install_sbt():
    '''
    Installs sbt

    NOTE: Local execution
    '''
    program_root = os.path.join(_install_root, "sbt", "bin")
    create_public_dir(program_root)
    with lcd(program_root):
        local("wget " + _sbt_url)
        sbt_original_jar = local("ls | grep ^sbt-launch.jar" , capture = True)
        local("mv " + sbt_original_jar + " sbt-launch.jar")
        local("touch sbt")
        local("chmod +x sbt")
        local('''echo 'SBT_OPTS="-Xms512M -Xmx1536M -Xss1M -XX:+CMSClassUnloadingEnabled -XX:MaxPermSize=256M"' >> sbt''')
        local('''echo 'java $SBT_OPTS -jar `dirname $0`/sbt-launch.jar "$@"' >> sbt''')

_sbt_global_plugin_file = os.path.join(os.environ["HOME"], ".sbt", "0.13", "plugins", "plugins.sbt")
@task
def install_sbt_eclipse_plugin(): 
    '''
    Installs globally the sbt plugin for eclipse in the local machine, following https://github.com/typesafehub/sbteclipse/wiki/Installing-sbteclipse
    '''
    local("mkdir -p " + os.path.dirname(_sbt_global_plugin_file))
    local("touch " + _sbt_global_plugin_file)
    # note blank lines between settings are required
    local("echo '' >> " + _sbt_global_plugin_file)
    local('''echo  'addSbtPlugin("com.typesafe.sbteclipse" % "sbteclipse-plugin" % "2.5.0")'  >> ''' + _sbt_global_plugin_file)

_zeppelin_root = os.path.join(_install_root, "zeppelin")
_zeppelin_url = "https://github.com/apache/incubator-zeppelin/archive/master.zip"
_zeppelin_bin_path = os.path.join(_zeppelin_root, "incubator-zeppelin-master", "bin")
@task
def install_apache_zeppelin(spark_version = _default_spark_version, hadoop_version = _default_hadoop_version):
    '''
    Installs Apache Zeppelin locally

    Following https://zeppelin.incubator.apache.org/docs/install/install.html
    '''
    _zeppelin_path = install_simple_service("zeppelin", _zeppelin_url, "zip")["service_path"]
    with lcd(_zeppelin_path):
        local("mvn install -DskipTests -Dspark.version={spark_version}  -Dhadoop.version={hadoop_version}".format(spark_version=spark_version, hadoop_version=hadoop_version))

@task
def install_devenv():
    '''
    Install the development environment
    '''
    print "Installing the development environment"
    install_maven3()
    install_java7()
    install_zookeeper()
    install_kafka()
    install_spark()
    install_confluent_quickstart()
    install_sbt()
    install_sbt_eclipse_plugin()

    add_final_msg("use setup_local_services.sh to start and stop the local versions of the services")
    add_final_msg("source ~/.bashrc or open a new terminarl to refresh the PATH and other environment variables")
    print_final_msgs()