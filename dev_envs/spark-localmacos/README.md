# Spark Local Development Environment for Mac OS X 10.9.5

Based on native execution of Spark, and Docker containers for other services

## Basic devel tools

 * **Git**: in order to avoid installing XCode, download from [here](http://git-scm.com/download/mac), and use [open anyway](http://stackoverflow.com/questions/19551298/app-cant-be-opened-because-it-is-from-an-unidentified-developer) to install from an `unindentified developer`. This way git is installed at `/usr/local/git/`, but it is not in the `PATH`. To do this first we activate the per user `bashrc` by adding the following line to `~/.profile` (creating that file if it doesn't exists, `vim` seems to be installed BTW)

```bash
source ~/.bashrc
```

then we add git to the PATH by adding the following code to ~/.bashrc (creating that file if it doesn't exists)

```bash
export PATH=/usr/local/git/bin/:${PATH}
```

 * **Docker**: install `boot2docker` for MacOS following the [official instructions](https://docs.docker.com/installation/mac/). See [Docker cheatshee](https://github.com/juanrh/juanrh.github.io/wiki/Docker-cheatsheet) for details and workarounds for the bugs in the MacOS version of Docker

* **Eclipse**: using Eclipse Kepler for Java
    - follow [this instructions](https://wiki.eclipse.org/Updating_eclipse.ini_on_MacOS) to access `eclipse.ini` (note `Eclipse.app` is seen as a directory from the terminal), to set `-Xmx1500m` for the Scala plugin
    - Use [open anyway](http://stackoverflow.com/questions/19551298/app-cant-be-opened-because-it-is-from-an-unidentified-developer) to install from an `unindentified developer`
    - Install the ScalaIDE plugin from version 3.0.3 for Scala 2.10.4 (for Spark) in the update site listed [here](http://scala-ide.org/download/prev-stable.html)

* **sbt**: install as follows: download `sbt-launch.jar` from [here](https://repo.typesafe.com/typesafe/ivy-releases/org.scala-sbt/sbt-launch/0.13.8/sbt-launch.jar?_ga=1.141836786.1544579142.1428429429) and copy it to `~/Sistemas/sbt/sbt-launch.jar`, and then run

```bash
echo 'Installing sbt'
cd ~/Sistemas/sbt
touch sbt
chmod +x sbt
echo 'SBT_OPTS="-Xms512M -Xmx1536M -Xss1M -XX:+CMSClassUnloadingEnabled -XX:MaxPermSize=256M"' >> sbt
echo 'java $SBT_OPTS -jar `dirname $0`/sbt-launch.jar "$@"' >> sbt
echo 'Adding sbt to PATH'
echo '' >>  ~/.bashrc
echo 'export PATH=${PATH}:${HOME}/Sistemas/sbt' >>  ~/.bashrc
echo 'Configuring globally sbt plugin for Eclipse (see https://github.com/typesafehub/sbteclipse/wiki/Installing-sbteclipse)'
_sbt_global_plugin_file=${HOME}/.sbt/0.13/plugins/plugins.sbt
mkdir -p $(dirname $_sbt_global_plugin_file)
touch $_sbt_global_plugin_file
echo '' >> $_sbt_global_plugin_file
echo  'addSbtPlugin("com.typesafe.sbteclipse" % "sbteclipse-plugin" % "2.5.0")' >> $_sbt_global_plugin_file  
```
