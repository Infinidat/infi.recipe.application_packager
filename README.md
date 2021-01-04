Overview
========

At Infinidat, we write products in Python, and not just a bunch of scripts.
We want our products to be isolated from global Python installations and `site-packages`.

The solution we came with is as follows:

* Bundle the interpreter itself in the application, along with all the dependencies.
* If there are binary dependencies, compile it when building the application package

This is our buildout recipe for creating the platform-specific packages.

This recipe, along with our isolated python builds, provides the following features:
* building operating systems packages for Python projects:
** `RPM` packages on RedHat-based linux distributions
** `DEB` packages on Debian-based linux distributions, altough we test it only on Ubuntu
** `MSI` packages for Windows, starting from Windows NT 5.0
* creating single-file, statically-linked, portable, executables for console scripts
* building a static library of the interpreter along with all the 3rd-party dependcies


What deployment solution should I use
-------------------------------------

If you need to build a shared library but want to write it in Python, then you can pack the Python code as a static library and link you shared library with it.

If you need to a sinlge standalone, no-installation-required executable then use the executable recipe.

if you need a full Python interpreter, or access to package resources, then you should pack your Python project in an OS package.



Using this recipe
-----------------

In order create an application with proper packaging, you'll need more than just this recipe.

* Obtain `projector` from https://github.com/Infinidat/infi.projector
* Create a project using projector, build the development environment using the isolated python option.
* Add `company` attribute to the `project` section in your `buildout.cfg`.
* Run `projector devenv pack`; this will build all the sections in `buildout.cfg` that either of the recipes of this module.
** the default recipe: `infi.recipe.application_packager`, will build the OS package depending on the operating system.
** instead, you can explicitly define one of the following recipes:
*** `infi.recipe.application_packager.deb`
*** `infi.recipe.application_packager.msi`
*** `infi.recipe.application_packager.rpm`

At the end, OS packages will be available under the `parts` directory, and single-file executables and static libraries will be placed under `dist`.

To debug exceptions, add 'pdb = true' to the recipe. The results are stored under the follwing directories:
* `parts`. stores the deb, msi and rpm intermediate files and final packages
* `build/Python-<x.y.z>`. the Python source
* `build/static`. this this where we copy to all the static libraries from the isolated python that will link the static python with
* `build/dependencies`. this is where all the dependencies are being built

### Recipe configuration options

Under the `pack` recipe in your `buildout.cfg`, you can define the following options:

| Key                                   | Applied to                                | Default value                                                | Description                                                              |
| ------------------------------------- | ----------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------ |
| pdb                                   | deb, msi, rpm                             | false                                                        | enter pdb if exception is raise for post mortem                          |
| dependent-scripts                     | deb, msi, rpm                             | false                                                        |                                                                          |
| eggs                                  | deb, msi, rpm                             | \<project name>                                              |                                                                          |
| scripts                               | deb, msi, rpm                             | \<empty list>                                                |                                                                          |
| gui-scripts                           | deb, msi, rpm                             | \<empty list>                                                |                                                                          |
| minimal-packages                      | deb, msi, rpm                             |                                                              | Adds code to the entry point wrapper that tries to use less packages     |
| shortcuts-icon                        | msi                                       | ~/.msi-ui/icon.exe                                           | Icon file in EXE binary format to be used as icon for shortcuts          |
| shrink-cache-dist                     | deb, msi, rpm                             | true                                                         | delete sources from .cache/dist that are under the install-requires tree |
| deb-dependencies                      | deb                                       |                                                              | List of debian packages to be required prior installing your package     |
| sign-executables-and-msi              | msi                                       | false                                                        | Digitally signed the MSI using Authenticode certificate                  |
| pfx-file                              | msi                                       | ~/.authenticode/certificate.pfx                              | Absolute location of the certificate file                                |
| pfx-password-file                     | msi                                       | ~/.authenticode/certificate-password.txt                     | Absolute locaton for the private txt of the certificate                  |
| timestamp-url                         | msi                                       | http://timestamp.digicert.com/scripts/timstamp.dll           | Timestamp server                                                         |
| require-administrative-privileges     | msi                                       | false                                                        |                                                                          |
| require-administrative-privileges-gui | msi                                       | false                                                        |                                                                          |
| install-on-windows-server-2016        | msi                                       | true                                                         |                                                                          |
| install-on-windows-server-2012-r2     | msi                                       | true                                                         |                                                                          |
| install-on-windows-server-2012        | msi                                       | true                                                         |                                                                          |
| install-on-windows-server-2008-r2     | msi                                       | true                                                         |                                                                          |
| install-on-windows-server-2008        | msi                                       | true                                                         |                                                                          |
| install-on-windows-server-2003        | msi                                       | false                                                        |                                                                          |
| install-on-windows-10                 | msi                                       | false                                                        |                                                                          |
| install-on-windows-8                  | msi                                       | false                                                        |                                                                          |
| install-on-windows-8.1                | msi                                       | false                                                        |                                                                          |
| install-on-windows-7                  | msi                                       | false                                                        |                                                                          |
| install-on-windows-vista              | msi                                       | false                                                        |                                                                          |
| install-on-windows-xp                 | msi                                       | false                                                        |                                                                          |
| add-remove-programs-icon              | msi                                       | ~/.msi-ui/icon.ico                                           | ICO file to use in the add/remove program applet                         |
| msi-banner-bmp                        | msi                                       | ~/.msi-ui/WixUIBanner.bmp                                    | Top banner                                                               |
| msi-dialog-bmp                        | msi                                       | ~/.msi-ui/WixUIDialog.bmp                                    | Background bitmap used on the welcome and completion dialogs             |
| startmenu-shortcuts                   | msi                                       | []                                                           | ['shortcut_name' = 'executable_name', ...]                               |
| rpm-dependencies                      | rpm                                       |                                                              | List of redhat packages to be required prior installing your package     |
| python-source-url                     | executable, static_library                | ftp://python.infinidat.com/python/sources/Python-2.7.6.tgz   | tgz archive for Python                                                   |
| LINKFLAGS                             | executable, static_library                |                                                              | extra flags to pass (as a string) to pystick                             |
| CC                                    | executable, static_library                |                                                              | extra flags to pass (as a string) to pystick                             |
| CXX                                   | executable, static_library                |                                                              | extra flags to pass (as a string) to pystick                             |
| PATH                                  | executable, static_library                |                                                              | extra flags to pass (as a string) to pystick                             |
| LD_LIBRARY_PATH                       | executable, static_library                |                                                              | extra flags to pass (as a string) to pystick                             |
| LIBRARY_PATH                          | executable, static_library                |                                                              | extra flags to pass (as a string) to pystick                             |
| LIBS                                  | executable, static_library                |                                                              | extra flags to pass (as a string) to pystick                             |
| always-build                          | executable, static_library                |                                                              | always build from scratch, even when artifacts exist on disk             |
| exclude-eggs                          | executable, static_library                | []                                                           | eggs not to include in the build                                         |
| existing-installdir                   | msi                                       | None                                                         | path to registry value to look for installation directory                |
| custom-installdir                     | msi                                       | None                                                         | override if want to use something other than [EXISTINGINSTALLDIR]        |
| eula-rtf                              | msi                                       | None                                                         | path to end-user license agreement RTF file                              |
| documentation-url                     | msi                                       | None                                                         | gives the user an option to launch the online docs after install         |

Using the installers
--------------------

The basic flow of the installer is as follows:

* Copy all the files to the target directory. The target directory is either `/opt/<company>/<product name>` or `%ProgramFiles%\<company>\<product name>
* Run get-pip
* Run bootstrap
* Create the executable scripts
* Run the user-defined post install script, if was defined in `buildout.cfg`

The uninstall procedure is:

* Run the user-defined pre uninstall script
* Delete all the files that were copied during the installation, and remove temporary python files
* If the installation directory is empty, delete it

### Testing installations

This module also provides Installer classes that'll help you create integration tests for your installer, and to test it out before going to production.

### Debugging installations

The buildout logs are available at:
* /var/log/ if writable, else /tmp/
* %TEMP% if exists or %SystemRoot%\Windows\Temp

The installer accept two variables:

| Name                 | Description                                                           |
| -------------------- | --------------------------------------------------------------------- |
| NO_CUSTOM_ACTIONS    | Disables scripts during install/uninstall, just creates/deletes files |
| DEBUG_CUSTOM_ACTIONS | Verbose logging                                                       |

To use these (example):

* Redhat/CentOS: `NO_CUSTOM_ACTIONS=1 rpm ....`
* Windows: `msiexec /i ... NO_CUSTOM_ACTIONS=1`

Using fixed installation directory in Windows
---------------------------------------------

In some cases, you'd want to install the product in a specific location, without giving the end-user a choice to change that.

When you set a value to `custom-installdir`, this will change the UI to jump from the welcome dialog to the verify-installation dialog.

Looking for installation directory inside the Windows Registry
--------------------------------------------------------------

If you want to install the product under a directory that's written in the registry, add the following items to the buildout recipe:

* existing-installdir: HKLM\Software\Key\SubKey\Value
* custom-insalldir: [EXISTINGINSTALLDIR]

Checking out the code
=====================

Run the following:

    easy_install -U infi.projector
    projector devenv build

Python 3 support
================
Python 3 support is experimental at this stage.