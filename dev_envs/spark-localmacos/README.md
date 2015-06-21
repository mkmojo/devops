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

 * **Docker**: install `boot2docker` for MacOS following the [official instructions](https://docs.docker.com/installation/mac/)

    - note after `boot2docker init` we have to run `eval "$(boot2docker shellinit)"` before any other command, in other to have `DOCKER_HOST` and other variables regarding the VirtualBox instance that is actually running the Docker server 

* **Eclipse**: using Eclipse Kepler for Java
    - follow [this instructions](https://wiki.eclipse.org/Updating_eclipse.ini_on_MacOS) to access `eclipse.ini` (note `Eclipse.app` is seen as a directory from the terminal), to set `-Xmx1500m` for the Scala plugin
    - Use [open anyway](http://stackoverflow.com/questions/19551298/app-cant-be-opened-because-it-is-from-an-unidentified-developer) to install from an `unindentified developer`
- Install the ScalaIDE plugin from version 3.0.3 for Scala 2.10.4 (for Spark) in the update site listed [here](http://scala-ide.org/download/prev-stable.html)
