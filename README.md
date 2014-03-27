Overview
========

At Infinidat, we write products in Python, and not just a bunch of scripts.
We want our products to be isolated from global Python installations and `site-packages`.

The solution we came with is as follows:

* Bundle the interpreter itself in the application, along with all the dependencies.
* If there are binary dependencies, compile it when building the application package

This is our buildout recipe for creating the platform-specific packages.

The currently supported packages/platforms, are:

* `RPM` on RedHat/CentOS
* `DEB` on Ubuntu
* `MSI` on Windows
* executable: one, big, statically-linked executable per entry point
* shared library: one, big, shared library


Using this recipe
-----------------

In order create an application with proper packaging, you'll need more than just this recipe.

* Obtain `projector` from https://github.com/Infinidat/infi.projector
* Create a project using projector, build the development environment using the isolated python option.
* Add `company` attribute to the `project` section in your `buildout.cfg`.
* Run `projector devenv pack`. Depending on the platform you're running, it'll generate a proper package under the `parts` directory.


### Recipe configuration options

Under the `pack` recipe in your `buildout.cfg`, you can define the following options:

| Key                                   | Applied to  | Default value                                        | Description                                                              |
| ------------------------------------- | ----------- | --------------------------------------------------   | ------------------------------------------------------------------------ |
| dependent-scripts                     | everything  | false                                                |                                                                          |
| eggs                                  | everything  | \<project name>                                      |                                                                          |
| scripts                               | everything  | \<empty list>                                        |                                                                          |
| gui-scripts                           | everything  | \<empty list>                                        |                                                                          |
| minimal-packages                      | everything  |                                                      | Adds code to the entry point wrapper that tries to use less packages     |
| shortcuts-icon                        | everything  | None                                                 | Icon file in EXE binary format to be used as icon for shortcuts          |
| shrink-cache-dist                     | everything  | true                                                 | delete sources from .cache/dist that are under the install-requires tree |
| deb-dependencies                      | deb         |                                                      | List of debian packages to be required prior installing your package     |
| rpm-dependencies                      | rpm         |                                                      | List of redhat packages to be required prior installing your package     |
| sign-executables-and-msi              | msi         | false                                                | Digitally signed the MSI using Authenticode certificate                  |
| pfx-file                              | msi         | ~/.authenticode/certificate.pfx                      | Absolute location of the certificate file                                |
| pfx-password-file                     | msi         | ~/.authenticode/certificate-password.txt             | Absolute locaton for the private txt of the certificate                  |
| timestamp-url                         | msi         | http://timestamp.verisign.com/scripts/timstamp.dll   | Timestamp server                                                         |
| require-administrative-privileges     | msi         | false                                                |                                                                          |
| require-administrative-privileges-gui | msi         | false                                                |                                                                          |
| install-on-windows-server-2012-r2     | msi         | true                                                 |                                                                          |
| install-on-windows-server-2012        | msi         | true                                                 |                                                                          |
| install-on-windows-server-2008-r2     | msi         | true                                                 |                                                                          |
| install-on-windows-server-2008        | msi         | true                                                 |                                                                          |
| install-on-windows-server-2003        | msi         | false                                                |                                                                          |
| install-on-windows-8                  | msi         | false                                                |                                                                          |
| install-on-windows-7                  | msi         | false                                                |                                                                          |
| install-on-windows-vista              | msi         | false                                                |                                                                          |
| install-on-windows-xp                 | msi         | false                                                |                                                                          |
| add-remove-programs-icon              | msi         | None                                                 | ICO file to use in the add/remove program applet                         |
| msi-banner-nmp                        | msi         | None                                                 | Top banner                                                               |
| msi-dialog-bmp                        | msi         | None                                                 | Background bitmap used on the welcome and completion dialogs             |
| startmenu-shortcuts                   | msi         | []                                                   | ['shortcut_name' = 'executable_name', ...]                               |
| python-source-url                     | exe/lib     | ftp://python.infinidat.com/archives/Python-2.7.6.tgz | tgz archive for Python

Using the installers
--------------------

The basic flow of the installer is as follows:

* Copy all the files to the target directory. The target directory is either `/opt/<company>/<product name>` or `%ProgramFiles%\<company>\<product name>
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


Checking out the code
=====================

Run the following:

    easy_install -U infi.projector
    projector devenv build
