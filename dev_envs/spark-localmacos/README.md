# Spark Local Development Environment for Mac OS X 10.9.5

Based on native execution of Spark, and Docker containers for other services

## Basic devel tools

 * Git: in order to avoid installing XCode, download from [here](http://git-scm.com/download/mac), and use [open anyway](http://stackoverflow.com/questions/19551298/app-cant-be-opened-because-it-is-from-an-unidentified-developer) to install from an `unindentified developer`. This way git is installed at `/usr/local/git/`, but it is not in the `PATH`. To do this first we activate the per user `bashrc` by adding the following line to `~/.profile` (creating that file if it doesn't exists, `vim` seems to be installed BTW)

```bash
source ~/.bashrc
```

then we add git to the PATH by adding the following code to ~/.bashrc (creating that file if it doesn't exists)

```bash
export PATH=/usr/local/git/bin/:${PATH}
```
