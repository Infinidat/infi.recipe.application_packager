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

Using this recipe
-----------------

In order create an application with proper packaging, you'll need more than just this recipe.

* Obtain `projector` from https://github.com/Infinidat/infi.projector
* Create a project using projector, build the development environment using the isolated python option.
* Add `company` attribute to the `project` section in your `buildout.cfg`.
* Run `projector devenv pack`. Depending on the platform you're running, it'll generate a proper package under the `parts` directory.


### Recipe configuration options

Under the `pack` recipe in your `buildout.cfg`, you can define the following options:

| Key                                   | Default value                                      | Description                                                              |
| ---------------------------------     | -------------------------------------------------- | ------------------------------------------------------------------------ |
| dependent-scripts                     | false                                              |                                                                          |
| eggs                                  | \<project name>                                    |                                                                          |
| scripts                               | \<empty list>                                      |                                                                          |
| gui-scripts                           | \<empty list>                                      |                                                                          |
| minimal-packages                      |                                                    | Adds code to the entry point wrapper that tries to use less packages     |
| deb-dependencies                      |                                                    | List of debian packages to be required prior installing your package     |
| rpm-dependencies                      |                                                    | List of redhat packages to be required prior installing your package     |
| sign-executables-and-msi              | false                                              | Digitally signed the MSI using Authenticode certificate                  |
| pfx-file                              | ~/.authenticode/certificate.pfx                    | Absolute location of the certificate file                                |
| pfx-password-file                     | ~/.authenticode/certificate-password.txt           | Absolute locaton for the private txt of the certificate                  |
| timestamp-url                         | http://timestamp.verisign.com/scripts/timstamp.dll | Timestamp server                                                         |
| require-administrative-privileges     | false                                              |                                                                          |
| require-administrative-privileges-gui | false                                              |                                                                          |
| install-on-windows-server-2012-r2     | true                                               |                                                                          |
| install-on-windows-server-2012        | true                                               |                                                                          |
| install-on-windows-server-2008-r2     | true                                               |                                                                          |
| install-on-windows-server-2008        | true                                               |                                                                          |
| install-on-windows-server-2003        | false                                              |                                                                          |
| install-on-windows-8                  | false                                              |                                                                          |
| install-on-windows-7                  | false                                              |                                                                          |
| install-on-windows-vista              | false                                              |                                                                          |
| install-on-windows-xp                 | false                                              |                                                                          |
| add-remove-programs-icon              | None                                               | ICO file to use in the add/remove program applet                         |
| msi-banner-nmp                        | None                                               | Top banner                                                               |
| msi-dialog-bmp                        | None                                               | Background bitmap used on the welcome and completion dialogs             |
| startmenu-shortcuts                   | []                                                 | ['shortcut_name' = 'executable_name', ...]                               |
| shortcuts-icon                        | None                                               | Icon file in EXE binary format to be used as icon for shortcuts          |
| shrink-cache-dist                     | true                                               | delete sources from .cache/dist that are under the install-requires tree |

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
