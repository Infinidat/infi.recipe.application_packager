SCONS_VARIABLE_NAMES = [
   "AR", # The static library archiver.
   "ARCHITECTURE", # Specifies the system architecture for which the package is being built. The default is the system architecture of the machine on which SCons is running. This is used to fill in the Architecture: field in an Ipkg control file, and as part of the name of a generated RPM file.
   "ARCOM", # The command line used to generate a static library from object files.
   "ARCOMSTR", # The string displayed when an object file is generated from an assembly-language source file. If this is not set, then $ARCOM (the command line) is displayed.
   "ARFLAGS", # General options passed to the static library archiver.
   "AS", # The assembler.
   "ASCOM", # The command line used to generate an object file from an assembly-language source file.
   "ASCOMSTR", # The string displayed when an object file is generated from an assembly-language source file. If this is not set, then $ASCOM (the command line) is displayed.
   "ASFLAGS", # General options passed to the assembler.
   "ASPPCOM", # The command line used to assemble an assembly-language source file into an object file after first running the file through the C preprocessor. Any options specified in the $ASFLAGS and $CPPFLAGS construction variables are included on this command line.
   "ASPPCOMSTR", # The string displayed when an object file is generated from an assembly-language source file after first running the file through the C preprocessor. If this is not set, then $ASPPCOM (the command line) is displayed.
   "ASPPFLAGS", # General options when an assembling an assembly-language source file into an object file after first running the file through the C preprocessor. The default is to use the value of $ASFLAGS.
   "BIBTEX", # The bibliography generator for the TeX formatter and typesetter and the LaTeX structured formatter and typesetter.
   "BIBTEXCOM", # The command line used to call the bibliography generator for the TeX formatter and typesetter and the LaTeX structured formatter and typesetter.
   "BIBTEXCOMSTR", # The string displayed when generating a bibliography for TeX or LaTeX. If this is not set, then $BIBTEXCOM (the command line) is displayed.
   "BIBTEXFLAGS", # General options passed to the bibliography generator for the TeX formatter and typesetter and the LaTeX structured formatter and typesetter.
   "BITKEEPER", # The BitKeeper executable.
   "BITKEEPERCOM", # The command line for fetching source files using BitKeeper.
   "BITKEEPERCOMSTR", # The string displayed when fetching a source file using BitKeeper. If this is not set, then $BITKEEPERCOM (the command line) is displayed.
   "BITKEEPERGET", # The command ($BITKEEPER) and subcommand for fetching source files using BitKeeper.
   "BITKEEPERGETFLAGS", # Options that are passed to the BitKeeper get subcommand.
   "BUILDERS", # A dictionary mapping the names of the builders available through this environment to underlying Builder objects. Builders named Alias, CFile, CXXFile, DVI, Library, Object, PDF, PostScript, and Program are available by default. If you initialize this variable when an ment is created:
   "CC", # The C compiler.
   "CCCOM", # The command line used to compile a C source file to a (static) object file. Any options specified in the $CFLAGS, $CCFLAGS and $CPPFLAGS construction variables are included on this command line.
   "CCCOMSTR", # The string displayed when a C source file is compiled to a (static) object file. If this is not set, then $CCCOM (the command line) is displayed.
   "CCFLAGS", # General options that are passed to the C and C++ compilers.
   "CCPCHFLAGS", # Options added to the compiler command line to support building with precompiled headers. The default value expands expands to the appropriate Microsoft Visual C++ command-line options when the $PCH construction variable is set.
   "CCPDBFLAGS", # Options added to the compiler command line to support storing debugging information in a Microsoft Visual C++ PDB file. The default value expands expands to appropriate Microsoft Visual C++ command-line options when the $PDB construction variable is set.", # The Visual C++ compiler option that SCons uses by default to generate PDB information is /Z7. This works correctly with parallel (-j) builds because it embeds the debug information in the intermediate object files, as opposed to sharing a single PDB file between multiple object files. This is also the only way to get debug information embedded into a static library. Using the /Zi instead may yield improved link-time performance, although parallel builds will no longer work.", # You can generate PDB files with the /Zi switch by overriding the default $CCPDBFLAGS variable as follows:
   "CCVERSION", # The version number of the C compiler. This may or may not be set, depending on the specific C compiler being used.
   "CFILESUFFIX", # The suffix for C source files. This is used by the internal CFile builder when generating C files from Lex (.l) or YACC (.y) input files. The default suffix, of course, is .c (lower case). On case-insensitive systems (like Windows), SCons also treats .C (upper case) files as C files.
   "CFLAGS", # General options that are passed to the C compiler (C only; not C++).
   "CHANGE_SPECFILE", # A hook for modifying the file that controls the packaging build (the .spec for RPM, the control for Ipkg, the .wxs for MSI). If set, the function will be called after the SCons template for the file has been written. XXX
   "CHANGED_SOURCES", # A reserved variable name that may not be set or used in a construction environment. (See "Variable Substitution," below.)
   "CHANGED_TARGETS", # A reserved variable name that may not be set or used in a construction environment. (See "Variable Substitution," below.)
   "CHANGELOG", # The name of a file containing the change log text to be included in the package. This is included as the %changelog section of the RPM .spec file.
   "CONFIGUREDIR", # The name of the directory in which Configure context test files are written. The default is .sconf_temp in the top-level directory containing the SConstruct file.
   "CONFIGURELOG", # The name of the Configure context log file. The default is config.log in the top-level directory containing the SConstruct file.
   "CPPDEFINES", # A platform independent specification of C preprocessor definitions. The definitions will be added to command lines through the automatically-generated $_CPPDEFFLAGS construction variable (see above), which is constructed according to the type of value of $CPPDEFINES:", # If $CPPDEFINES is a string, the values of the $CPPDEFPREFIX and $CPPDEFSUFFIX construction variables will be added to the beginning and end.
   "CPPDEFPREFIX", # The prefix used to specify preprocessor definitions on the C compiler command line. This will be appended to the beginning of each definition in the $CPPDEFINES construction variable when the $_CPPDEFFLAGS variable is automatically generated.
   "CPPDEFSUFFIX", # The suffix used to specify preprocessor definitions on the C compiler command line. This will be appended to the end of each definition in the $CPPDEFINES construction variable when the $_CPPDEFFLAGS variable is automatically generated.
   "CPPFLAGS", # User-specified C preprocessor options. These will be included in any command that uses the C preprocessor, including not just compilation of C and C++ source files via the $CCCOM, $SHCCCOM, $CXXCOM and $SHCXXCOM command lines, but also the $FORTRANPPCOM, $SHFORTRANPPCOM, $F77PPCOM and $SHF77PPCOM command lines used to compile a Fortran source file, and the $ASPPCOM command line used to assemble an assembly language source file, after first running each file through the C preprocessor. Note that this variable does not contain -I (or similar) include search path options that scons generates automatically from $CPPPATH. See $_CPPINCFLAGS, below, for the variable that expands to those options.
   "CPPPATH", # The list of directories that the C preprocessor will search for include directories. The C/C++ implicit dependency scanner will search these directories for include files. Don't explicitly put include directory arguments in CCFLAGS or CXXFLAGS because the result will be non-portable and the directories will not be searched by the dependency scanner. Note: directory names in CPPPATH will be looked-up relative to the SConscript directory when they are used in a command. To force scons to look-up a directory relative to the root of the source tree use #:
   "CPPSUFFIXES", # The list of suffixes of files that will be scanned for C preprocessor implicit dependencies (#include lines). The default list is: [".c", ".C", ".cxx", ".cpp", ".c++", ".cc",  ".h", ".H", ".hxx", ".hpp", ".hh",  ".F", ".fpp", ".FPP",  ".m", ".mm",  ".S", ".spp", ".SPP"]
   "CVS", # The CVS executable.
   "CVSCOFLAGS", # Options that are passed to the CVS checkout subcommand.
   "CVSCOM", # The command line used to fetch source files from a CVS repository.
   "CVSCOMSTR", # The string displayed when fetching a source file from a CVS repository. If this is not set, then $CVSCOM (the command line) is displayed.
   "CVSFLAGS", # General options that are passed to CVS. By default, this is set to -d $CVSREPOSITORY to specify from where the files must be fetched.
   "CVSREPOSITORY", # The path to the CVS repository. This is referenced in the default $CVSFLAGS value.
   "CXX", # The C++ compiler.
   "CXXCOM", # The command line used to compile a C++ source file to an object file. Any options specified in the $CXXFLAGS and $CPPFLAGS construction variables are included on this command line.
   "CXXCOMSTR", # The string displayed when a C++ source file is compiled to a (static) object file. If this is not set, then $CXXCOM (the command line) is displayed.
   "CXXFILESUFFIX", # The suffix for C++ source files. This is used by the internal CXXFile builder when generating C++ files from Lex (.ll) or YACC (.yy) input files. The default suffix is .cc. SCons also treats files with the suffixes .cpp, .cxx, .c++, and .C++ as C++ files, and files with .mm suffixes as Objective C++ files. On case-sensitive systems (Linux, UNIX, and other POSIX-alikes), SCons also treats .C (upper case) files as C++ files.
   "CXXFLAGS", # General options that are passed to the C++ compiler. By default, this includes the value of $CCFLAGS, so that setting $CCFLAGS affects both C and C++ compilation. If you want to add C++-specific flags, you must set or override the value of $CXXFLAGS.
   "CXXVERSION", # The version number of the C++ compiler. This may or may not be set, depending on the specific C++ compiler being used.
   "DESCRIPTION", # A long description of the project being packaged. This is included in the relevant section of the file that controls the packaging build.
   "DESCRIPTION_lang", # A language-specific long description for the specified lang. This is used to populate a %description -l section of an RPM .spec file.
   "DOCBOOK_DEFAULT_XSL_EPUB", # The default XSLT file for the DocbookEpub builder within the current environment, if no other XSLT gets specified via keyword.
   "DOCBOOK_DEFAULT_XSL_HTML", # The default XSLT file for the DocbookHtml builder within the current environment, if no other XSLT gets specified via keyword.
   "DOCBOOK_DEFAULT_XSL_HTMLCHUNKED", # The default XSLT file for the DocbookHtmlChunked builder within the current environment, if no other XSLT gets specified via keyword.
   "DOCBOOK_DEFAULT_XSL_HTMLHELP", # The default XSLT file for the DocbookHtmlhelp builder within the current environment, if no other XSLT gets specified via keyword.
   "DOCBOOK_DEFAULT_XSL_MAN", # The default XSLT file for the DocbookMan builder within the current environment, if no other XSLT gets specified via keyword.
   "DOCBOOK_DEFAULT_XSL_PDF", # The default XSLT file for the DocbookPdf builder within the current environment, if no other XSLT gets specified via keyword.
   "DOCBOOK_DEFAULT_XSL_SLIDESHTML", # The default XSLT file for the DocbookSlidesHtml builder within the current environment, if no other XSLT gets specified via keyword.
   "DOCBOOK_DEFAULT_XSL_SLIDESPDF", # The default XSLT file for the DocbookSlidesPdf builder within the current environment, if no other XSLT gets specified via keyword.
   "DOCBOOK_FOP", # The path to the PDF renderer fop or xep, if one of them is installed (fop gets checked first).
   "DOCBOOK_FOPCOM", # The full command-line for the PDF renderer fop or xep.
   "DOCBOOK_FOPCOMSTR", # The string displayed when a renderer like fop or xep is used to create PDF output from an XML file.
   "DOCBOOK_FOPFLAGS", # Additonal command-line flags for the PDF renderer fop or xep.
   "DOCBOOK_XMLLINT", # The path to the external executable xmllint, if it's installed. Note, that this is only used as last fallback for resolving XIncludes, if no libxml2 or lxml Python binding can be imported in the current system.
   "DOCBOOK_XMLLINTCOM", # The full command-line for the external executable xmllint.
   "DOCBOOK_XMLLINTCOMSTR", # The string displayed when xmllint is used to resolve XIncludes for a given XML file.
   "DOCBOOK_XMLLINTFLAGS", # Additonal command-line flags for the external executable xmllint.
   "DOCBOOK_XSLTPROC", # The path to the external executable xsltproc (or saxon, xalan), if one of them is installed. Note, that this is only used as last fallback for XSL transformations, if no libxml2 or lxml Python binding can be imported in the current system.
   "DOCBOOK_XSLTPROCCOM", # The full command-line for the external executable xsltproc (or saxon, xalan).
   "DOCBOOK_XSLTPROCCOMSTR", # The string displayed when xsltproc is used to transform an XML file via a given XSLT stylesheet.
   "DOCBOOK_XSLTPROCFLAGS", # Additonal command-line flags for the external executable xsltproc (or saxon, xalan).
   "DOCBOOK_XSLTPROCPARAMS", # Additonal parameters that are not intended for the XSLT processor executable, but the XSL processing itself. By default, they get appended at the end of the command line for saxon and saxon-xslt, respectively.
   "DSUFFIXES", # The list of suffixes of files that will be scanned for imported D package files. The default list is: ['.d']
   "DVIPDF", # The TeX DVI file to PDF file converter.
   "DVIPDFCOM", # The command line used to convert TeX DVI files into a PDF file.
   "DVIPDFCOMSTR", # The string displayed when a TeX DVI file is converted into a PDF file. If this is not set, then $DVIPDFCOM (the command line) is displayed.
   "DVIPDFFLAGS", # General options passed to the TeX DVI file to PDF file converter.
   "DVIPS", # The TeX DVI file to PostScript converter.
   "DVIPSFLAGS", # General options passed to the TeX DVI file to PostScript converter.
   "ENV", # A dictionary of environment variables to use when invoking commands. When $ENV is used in a command all list values will be joined using the path separator and any other non-string values will simply be coerced to a string. Note that, by default, scons does not propagate the environment in force when you execute scons to the commands used to build target files. This is so that builds will be guaranteed repeatable regardless of the environment variables set at the time scons is invoked.", # If you want to propagate your environment variables to the commands executed to build target files, you must do so explicitly:
   "ESCAPE", # A function that will be called to escape shell special characters in command lines. The function should take one argument: the command line string to escape; and should return the escaped command line.
   "F03", # The Fortran 03 compiler. You should normally set the $FORTRAN variable, which specifies the default Fortran compiler for all Fortran versions. You only need to set $F03 if you need to use a specific compiler or compiler version for Fortran 03 files.
   "F03COM", # The command line used to compile a Fortran 03 source file to an object file. You only need to set $F03COM if you need to use a specific command line for Fortran 03 files. You should normally set the $FORTRANCOM variable, which specifies the default command line for all Fortran versions.
   "F03COMSTR", # The string displayed when a Fortran 03 source file is compiled to an object file. If this is not set, then $F03COM or $FORTRANCOM (the command line) is displayed.
   "F03FILESUFFIXES", # The list of file extensions for which the F03 dialect will be used. By default, this is ['.f03']
   "F03FLAGS", # General user-specified options that are passed to the Fortran 03 compiler. Note that this variable does not contain -I (or similar) include search path options that scons generates automatically from $F03PATH. See $_F03INCFLAGS below, for the variable that expands to those options. You only need to set $F03FLAGS if you need to define specific user options for Fortran 03 files. You should normally set the $FORTRANFLAGS variable, which specifies the user-specified options passed to the default Fortran compiler for all Fortran versions.
   "F03PATH", # The list of directories that the Fortran 03 compiler will search for include directories. The implicit dependency scanner will search these directories for include files. Don't explicitly put include directory arguments in $F03FLAGS because the result will be non-portable and the directories will not be searched by the dependency scanner. Note: directory names in $F03PATH will be looked-up relative to the SConscript directory when they are used in a command. To force scons to look-up a directory relative to the root of the source tree use #: You only need to set $F03PATH if you need to define a specific include path for Fortran 03 files. You should normally set the $FORTRANPATH variable, which specifies the include path for the default Fortran compiler for all Fortran versions.
   "F03PPCOM", # The command line used to compile a Fortran 03 source file to an object file after first running the file through the C preprocessor. Any options specified in the $F03FLAGS and $CPPFLAGS construction variables are included on this command line. You only need to set $F03PPCOM if you need to use a specific C-preprocessor command line for Fortran 03 files. You should normally set the $FORTRANPPCOM variable, which specifies the default C-preprocessor command line for all Fortran versions.
   "F03PPCOMSTR", # The string displayed when a Fortran 03 source file is compiled to an object file after first running the file through the C preprocessor. If this is not set, then $F03PPCOM or $FORTRANPPCOM (the command line) is displayed.
   "F03PPFILESUFFIXES", # The list of file extensions for which the compilation + preprocessor pass for F03 dialect will be used. By default, this is empty
   "F77", # The Fortran 77 compiler. You should normally set the $FORTRAN variable, which specifies the default Fortran compiler for all Fortran versions. You only need to set $F77 if you need to use a specific compiler or compiler version for Fortran 77 files.
   "F77COM", # The command line used to compile a Fortran 77 source file to an object file. You only need to set $F77COM if you need to use a specific command line for Fortran 77 files. You should normally set the $FORTRANCOM variable, which specifies the default command line for all Fortran versions.
   "F77COMSTR", # The string displayed when a Fortran 77 source file is compiled to an object file. If this is not set, then $F77COM or $FORTRANCOM (the command line) is displayed.
   "F77FILESUFFIXES", # The list of file extensions for which the F77 dialect will be used. By default, this is ['.f77']
   "F77FLAGS", # General user-specified options that are passed to the Fortran 77 compiler. Note that this variable does not contain -I (or similar) include search path options that scons generates automatically from $F77PATH. See $_F77INCFLAGS below, for the variable that expands to those options. You only need to set $F77FLAGS if you need to define specific user options for Fortran 77 files. You should normally set the $FORTRANFLAGS variable, which specifies the user-specified options passed to the default Fortran compiler for all Fortran versions.
   "F77PATH", # The list of directories that the Fortran 77 compiler will search for include directories. The implicit dependency scanner will search these directories for include files. Don't explicitly put include directory arguments in $F77FLAGS because the result will be non-portable and the directories will not be searched by the dependency scanner. Note: directory names in $F77PATH will be looked-up relative to the SConscript directory when they are used in a command. To force scons to look-up a directory relative to the root of the source tree use #: You only need to set $F77PATH if you need to define a specific include path for Fortran 77 files. You should normally set the $FORTRANPATH variable, which specifies the include path for the default Fortran compiler for all Fortran versions.
   "F77PPCOM", # The command line used to compile a Fortran 77 source file to an object file after first running the file through the C preprocessor. Any options specified in the $F77FLAGS and $CPPFLAGS construction variables are included on this command line. You only need to set $F77PPCOM if you need to use a specific C-preprocessor command line for Fortran 77 files. You should normally set the $FORTRANPPCOM variable, which specifies the default C-preprocessor command line for all Fortran versions.
   "F77PPCOMSTR", # The string displayed when a Fortran 77 source file is compiled to an object file after first running the file through the C preprocessor. If this is not set, then $F77PPCOM or $FORTRANPPCOM (the command line) is displayed.
   "F77PPFILESUFFIXES", # The list of file extensions for which the compilation + preprocessor pass for F77 dialect will be used. By default, this is empty
   "F90", # The Fortran 90 compiler. You should normally set the $FORTRAN variable, which specifies the default Fortran compiler for all Fortran versions. You only need to set $F90 if you need to use a specific compiler or compiler version for Fortran 90 files.
   "F90COM", # The command line used to compile a Fortran 90 source file to an object file. You only need to set $F90COM if you need to use a specific command line for Fortran 90 files. You should normally set the $FORTRANCOM variable, which specifies the default command line for all Fortran versions.
   "F90COMSTR", # The string displayed when a Fortran 90 source file is compiled to an object file. If this is not set, then $F90COM or $FORTRANCOM (the command line) is displayed.
   "F90FILESUFFIXES", # The list of file extensions for which the F90 dialect will be used. By default, this is ['.f90']
   "F90FLAGS", # General user-specified options that are passed to the Fortran 90 compiler. Note that this variable does not contain -I (or similar) include search path options that scons generates automatically from $F90PATH. See $_F90INCFLAGS below, for the variable that expands to those options. You only need to set $F90FLAGS if you need to define specific user options for Fortran 90 files. You should normally set the $FORTRANFLAGS variable, which specifies the user-specified options passed to the default Fortran compiler for all Fortran versions.
   "F90PATH", # The list of directories that the Fortran 90 compiler will search for include directories. The implicit dependency scanner will search these directories for include files. Don't explicitly put include directory arguments in $F90FLAGS because the result will be non-portable and the directories will not be searched by the dependency scanner. Note: directory names in $F90PATH will be looked-up relative to the SConscript directory when they are used in a command. To force scons to look-up a directory relative to the root of the source tree use #: You only need to set $F90PATH if you need to define a specific include path for Fortran 90 files. You should normally set the $FORTRANPATH variable, which specifies the include path for the default Fortran compiler for all Fortran versions.
   "F90PPCOM", # The command line used to compile a Fortran 90 source file to an object file after first running the file through the C preprocessor. Any options specified in the $F90FLAGS and $CPPFLAGS construction variables are included on this command line. You only need to set $F90PPCOM if you need to use a specific C-preprocessor command line for Fortran 90 files. You should normally set the $FORTRANPPCOM variable, which specifies the default C-preprocessor command line for all Fortran versions.
   "F90PPCOMSTR", # The string displayed when a Fortran 90 source file is compiled after first running the file through the C preprocessor. If this is not set, then $F90PPCOM or $FORTRANPPCOM (the command line) is displayed.
   "F90PPFILESUFFIXES", # The list of file extensions for which the compilation + preprocessor pass for F90 dialect will be used. By default, this is empty
   "F95", # The Fortran 95 compiler. You should normally set the $FORTRAN variable, which specifies the default Fortran compiler for all Fortran versions. You only need to set $F95 if you need to use a specific compiler or compiler version for Fortran 95 files.
   "F95COM", # The command line used to compile a Fortran 95 source file to an object file. You only need to set $F95COM if you need to use a specific command line for Fortran 95 files. You should normally set the $FORTRANCOM variable, which specifies the default command line for all Fortran versions.
   "F95COMSTR", # The string displayed when a Fortran 95 source file is compiled to an object file. If this is not set, then $F95COM or $FORTRANCOM (the command line) is displayed.
   "F95FILESUFFIXES", # The list of file extensions for which the F95 dialect will be used. By default, this is ['.f95']
   "F95FLAGS", # General user-specified options that are passed to the Fortran 95 compiler. Note that this variable does not contain -I (or similar) include search path options that scons generates automatically from $F95PATH. See $_F95INCFLAGS below, for the variable that expands to those options. You only need to set $F95FLAGS if you need to define specific user options for Fortran 95 files. You should normally set the $FORTRANFLAGS variable, which specifies the user-specified options passed to the default Fortran compiler for all Fortran versions.
   "F95PATH", # The list of directories that the Fortran 95 compiler will search for include directories. The implicit dependency scanner will search these directories for include files. Don't explicitly put include directory arguments in $F95FLAGS because the result will be non-portable and the directories will not be searched by the dependency scanner. Note: directory names in $F95PATH will be looked-up relative to the SConscript directory when they are used in a command. To force scons to look-up a directory relative to the root of the source tree use #: You only need to set $F95PATH if you need to define a specific include path for Fortran 95 files. You should normally set the $FORTRANPATH variable, which specifies the include path for the default Fortran compiler for all Fortran versions.
   "F95PPCOM", # The command line used to compile a Fortran 95 source file to an object file after first running the file through the C preprocessor. Any options specified in the $F95FLAGS and $CPPFLAGS construction variables are included on this command line. You only need to set $F95PPCOM if you need to use a specific C-preprocessor command line for Fortran 95 files. You should normally set the $FORTRANPPCOM variable, which specifies the default C-preprocessor command line for all Fortran versions.
   "F95PPCOMSTR", # The string displayed when a Fortran 95 source file is compiled to an object file after first running the file through the C preprocessor. If this is not set, then $F95PPCOM or $FORTRANPPCOM (the command line) is displayed.
   "F95PPFILESUFFIXES", # The list of file extensions for which the compilation + preprocessor pass for F95 dialect will be used. By default, this is empty
   "FORTRAN", # The default Fortran compiler for all versions of Fortran.
   "FORTRANCOM", # The command line used to compile a Fortran source file to an object file. By default, any options specified in the $FORTRANFLAGS, $CPPFLAGS, $_CPPDEFFLAGS, $_FORTRANMODFLAG, and $_FORTRANINCFLAGS construction variables are included on this command line.
   "FORTRANCOMSTR", # The string displayed when a Fortran source file is compiled to an object file. If this is not set, then $FORTRANCOM (the command line) is displayed.
   "FORTRANFILESUFFIXES", # The list of file extensions for which the FORTRAN dialect will be used. By default, this is ['.f', '.for', '.ftn']
   "FORTRANFLAGS", # General user-specified options that are passed to the Fortran compiler. Note that this variable does not contain -I (or similar) include or module search path options that scons generates automatically from $FORTRANPATH. See $_FORTRANINCFLAGS and $_FORTRANMODFLAG, below, for the variables that expand those options.
   "FORTRANMODDIR", # Directory location where the Fortran compiler should place any module files it generates. This variable is empty, by default. Some Fortran compilers will internally append this directory in the search path for module files, as well.
   "FORTRANMODDIRPREFIX", # The prefix used to specify a module directory on the Fortran compiler command line. This will be appended to the beginning of the directory in the $FORTRANMODDIR construction variables when the $_FORTRANMODFLAG variables is automatically generated.
   "FORTRANMODDIRSUFFIX", # The suffix used to specify a module directory on the Fortran compiler command line. This will be appended to the beginning of the directory in the $FORTRANMODDIR construction variables when the $_FORTRANMODFLAG variables is automatically generated.
   "FORTRANMODPREFIX", # The module file prefix used by the Fortran compiler. SCons assumes that the Fortran compiler follows the quasi-standard naming convention for module files of module_name.mod. As a result, this variable is left empty, by default. For situations in which the compiler does not necessarily follow the normal convention, the user may use this variable. Its value will be appended to every module file name as scons attempts to resolve dependencies.
   "FORTRANMODSUFFIX", # The module file suffix used by the Fortran compiler. SCons assumes that the Fortran compiler follows the quasi-standard naming convention for module files of module_name.mod. As a result, this variable is set to ".mod", by default. For situations in which the compiler does not necessarily follow the normal convention, the user may use this variable. Its value will be appended to every module file name as scons attempts to resolve dependencies.
   "FORTRANPATH", # The list of directories that the Fortran compiler will search for include files and (for some compilers) module files. The Fortran implicit dependency scanner will search these directories for include files (but not module files since they are autogenerated and, as such, may not actually exist at the time the scan takes place). Don't explicitly put include directory arguments in FORTRANFLAGS because the result will be non-portable and the directories will not be searched by the dependency scanner. Note: directory names in FORTRANPATH will be looked-up relative to the SConscript directory when they are used in a command. To force scons to look-up a directory relative to the root of the source tree use #:
   "FORTRANPPCOM", # The command line used to compile a Fortran source file to an object file after first running the file through the C preprocessor. By default, any options specified in the $FORTRANFLAGS, $CPPFLAGS, $_CPPDEFFLAGS, $_FORTRANMODFLAG, and $_FORTRANINCFLAGS construction variables are included on this command line.
   "FORTRANPPCOMSTR", # The string displayed when a Fortran source file is compiled to an object file after first running the file through the C preprocessor. If this is not set, then $FORTRANPPCOM (the command line) is displayed.
   "FORTRANPPFILESUFFIXES", # The list of file extensions for which the compilation + preprocessor pass for FORTRAN dialect will be used. By default, this is ['.fpp', '.FPP']
   "FORTRANSUFFIXES", # The list of suffixes of files that will be scanned for Fortran implicit dependencies (INCLUDE lines and USE statements). The default list is:
   "FRAMEWORKPATH", # On Mac OS X with gcc, a list containing the paths to search for frameworks. Used by the compiler to find framework-style includes like #include <Fmwk/Header.h>. Used by the linker to find user-specified frameworks when linking (see $FRAMEWORKS). For example:
   "FRAMEWORKSFLAGS", # On Mac OS X with gcc, general user-supplied frameworks options to be added at the end of a command line building a loadable module. (This has been largely superseded by the $FRAMEWORKPATH, $FRAMEWORKPATHPREFIX, $FRAMEWORKPREFIX and $FRAMEWORKS variables described above.)
   "GS", # The Ghostscript program used, e.g. to convert PostScript to PDF files.
   "GSCOM", # The full Ghostscript command line used for the conversion process. Its default value is "$GS $GSFLAGS -sOutputFile=$TARGET $SOURCES".
   "GSCOMSTR", # The string displayed when Ghostscript is called for the conversion process. If this is not set (the default), then $GSCOM (the command line) is displayed.
   "GSFLAGS", # General options passed to the Ghostscript program, when converting PostScript to PDF files for example. Its default value is "-dNOPAUSE -dBATCH -sDEVICE=pdfwrite"
   "HOST_ARCH", # Sets the host architecture for Visual Studio compiler. If not set, default to the detected host architecture: note that this may depend on the python you are using. This variable must be passed as an argument to the Environment() constructor; setting it later has no effect.", # Valid values are the same as for $TARGET_ARCH.", # This is currently only used on Windows, but in the future it will be used on other OSes as well.", # The name of the host hardware architecture used to create the Environment. If a platform is specified when creating the Environment, then that Platform's logic will handle setting this value. This value is immutable, and should not be changed by the user after the Environment is initialized. Currently only set for Win32.
   "HOST_OS", # The name of the host operating system used to create the Environment. If a platform is specified when creating the Environment, then that Platform's logic will handle setting this value. This value is immutable, and should not be changed by the user after the Environment is initialized. Currently only set for Win32.
   "IDLSUFFIXES", # The list of suffixes of files that will be scanned for IDL implicit dependencies (#include or import lines). The default list is:
   "IMPLICIT_COMMAND_DEPENDENCIES", # Controls whether or not SCons will add implicit dependencies for the commands executed to build targets.", # By default, SCons will add to each target an implicit dependency on the command represented by the first argument on any command line it executes. The specific file for the dependency is found by searching the PATH variable in the ENV environment used to execute the command.", # If the construction variable $IMPLICIT_COMMAND_DEPENDENCIES is set to a false value (None, False, 0, etc.), then the implicit dependency will not be added to the targets built with that construction environment.
   "INCPREFIX", # The prefix used to specify an include directory on the C compiler command line. This will be appended to the beginning of each directory in the $CPPPATH and $FORTRANPATH construction variables when the $_CPPINCFLAGS and $_FORTRANINCFLAGS variables are automatically generated.
   "INCSUFFIX", # The suffix used to specify an include directory on the C compiler command line. This will be appended to the end of each directory in the $CPPPATH and $FORTRANPATH construction variables when the $_CPPINCFLAGS and $_FORTRANINCFLAGS variables are automatically generated.
   "INSTALL", # A function to be called to install a file into a destination file name. The default function copies the file into the destination (and sets the destination file's mode and permission bits to match the source file's). The function takes the following arguments:
   "INSTALLSTR", # The string displayed when a file is installed into a destination file name. The default is:
   "INTEL_C_COMPILER_VERSION", # Set by the "intelc" Tool to the major version number of the Intel C compiler selected for use.
   "JAR", # The Java archive tool.", # The Java archive tool.
   "JARCHDIR", # The directory to which the Java archive tool should change (using the -C option).", # The directory to which the Java archive tool should change (using the -C option).
   "JARCOM", # The command line used to call the Java archive tool.", # The command line used to call the Java archive tool.
   "JARCOMSTR", # The string displayed when the Java archive tool is called If this is not set, then $JARCOM (the command line) is displayed.
   "JARFLAGS", # General options passed to the Java archive tool. By default this is set to cf to create the necessary jar file.", # General options passed to the Java archive tool. By default this is set to cf to create the necessary jar file.
   "JARSUFFIX", # The suffix for Java archives: .jar by default.", # The suffix for Java archives: .jar by default.
   "JAVABOOTCLASSPATH", # Specifies the list of directories that will be added to the javac command line via the -bootclasspath option. The individual directory names will be separated by the operating system's path separate character (: on UNIX/Linux/POSIX, ; on Windows).
   "JAVAC", # The Java compiler.
   "JAVACCOM", # The command line used to compile a directory tree containing Java source files to corresponding Java class files. Any options specified in the $JAVACFLAGS construction variable are included on this command line.
   "JAVACCOMSTR", # The string displayed when compiling a directory tree of Java source files to corresponding Java class files. If this is not set, then $JAVACCOM (the command line) is displayed.
   "JAVACFLAGS", # General options that are passed to the Java compiler.
   "JAVACLASSDIR", # The directory in which Java class files may be found. This is stripped from the beginning of any Java .class file names supplied to the JavaH builder.
   "JAVACLASSPATH", # Specifies the list of directories that will be searched for Java .class file. The directories in this list will be added to the javac and javah command lines via the -classpath option. The individual directory names will be separated by the operating system's path separate character (: on UNIX/Linux/POSIX, ; on Windows).", # Note that this currently just adds the specified directory via the -classpath option. SCons does not currently search the $JAVACLASSPATH directories for dependency .class files.
   "JAVACLASSSUFFIX", # The suffix for Java class files; .class by default.
   "JAVAH", # The Java generator for C header and stub files.
   "JAVAHCOM", # The command line used to generate C header and stub files from Java classes. Any options specified in the $JAVAHFLAGS construction variable are included on this command line.
   "JAVAHCOMSTR", # The string displayed when C header and stub files are generated from Java classes. If this is not set, then $JAVAHCOM (the command line) is displayed.
   "JAVAHFLAGS", # General options passed to the C header and stub file generator for Java classes.
   "JAVASOURCEPATH", # Specifies the list of directories that will be searched for input .java file. The directories in this list will be added to the javac command line via the -sourcepath option. The individual directory names will be separated by the operating system's path separate character (: on UNIX/Linux/POSIX, ; on Windows).", # Note that this currently just adds the specified directory via the -sourcepath option. SCons does not currently search the $JAVASOURCEPATH directories for dependency .java files.
   "JAVASUFFIX", # The suffix for Java files; .java by default.
   "JAVAVERSION", # Specifies the Java version being used by the Java builder. This is not currently used to select one version of the Java compiler vs. another. Instead, you should set this to specify the version of Java supported by your javac compiler. The default is 1.4.", # This is sometimes necessary because Java 1.5 changed the file names that are created for nested anonymous inner classes, which can cause a mismatch with the files that SCons expects will be generated by the javac compiler. Setting $JAVAVERSION to 1.5 (or 1.6, as appropriate) can make SCons realize that a Java 1.5 or 1.6 build is actually up to date.
   "LATEX", # The LaTeX structured formatter and typesetter.
   "LATEXCOM", # The command line used to call the LaTeX structured formatter and typesetter.
   "LATEXCOMSTR", # The string displayed when calling the LaTeX structured formatter and typesetter. If this is not set, then $LATEXCOM (the command line) is displayed.
   "LATEXFLAGS", # General options passed to the LaTeX structured formatter and typesetter.
   "LATEXRETRIES", # The maximum number of times that LaTeX will be re-run if the .log generated by the $LATEXCOM command indicates that there are undefined references. The default is to try to resolve undefined references by re-running LaTeX up to three times.
   "LATEXSUFFIXES", # The list of suffixes of files that will be scanned for LaTeX implicit dependencies (\include or \import files). The default list is:
   "LDMODULE", # The linker for building loadable modules. By default, this is the same as $SHLINK.
   "LDMODULECOM", # The command line for building loadable modules. On Mac OS X, this uses the $LDMODULE, $LDMODULEFLAGS and $FRAMEWORKSFLAGS variables. On other systems, this is the same as $SHLINK.
   "LDMODULECOMSTR", # The string displayed when building loadable modules. If this is not set, then $LDMODULECOM (the command line) is displayed.
   "LDMODULEFLAGS", # General user options passed to the linker for building loadable modules.
   "LDMODULEPREFIX", # The prefix used for loadable module file names. On Mac OS X, this is null; on other systems, this is the same as $SHLIBPREFIX.
   "LDMODULESUFFIX", # The suffix used for loadable module file names. On Mac OS X, this is null; on other systems, this is the same as $SHLIBSUFFIX.
   "LEX", # The lexical analyzer generator.
   "LEXCOM", # The command line used to call the lexical analyzer generator to generate a source file.
   "LEXCOMSTR", # The string displayed when generating a source file using the lexical analyzer generator. If this is not set, then $LEXCOM (the command line) is displayed.
   "LEXFLAGS", # General options passed to the lexical analyzer generator.
   "LIBDIRPREFIX", # The prefix used to specify a library directory on the linker command line. This will be appended to the beginning of each directory in the $LIBPATH construction variable when the $_LIBDIRFLAGS variable is automatically generated.
   "LIBDIRSUFFIX", # The suffix used to specify a library directory on the linker command line. This will be appended to the end of each directory in the $LIBPATH construction variable when the $_LIBDIRFLAGS variable is automatically generated.
   "LIBEMITTER", # TODO
   "LIBLINKPREFIX", # The prefix used to specify a library to link on the linker command line. This will be appended to the beginning of each library in the $LIBS construction variable when the $_LIBFLAGS variable is automatically generated.
   "LIBLINKSUFFIX", # The suffix used to specify a library to link on the linker command line. This will be appended to the end of each library in the $LIBS construction variable when the $_LIBFLAGS variable is automatically generated.
   "LIBPATH", # The list of directories that will be searched for libraries. The implicit dependency scanner will search these directories for include files. Don't explicitly put include directory arguments in $LINKFLAGS or $SHLINKFLAGS because the result will be non-portable and the directories will not be searched by the dependency scanner. Note: directory names in LIBPATH will be looked-up relative to the SConscript directory when they are used in a command. To force scons to look-up a directory relative to the root of the source tree use #:
   "LIBPREFIX", # The prefix used for (static) library file names. A default value is set for each platform (posix, win32, os2, etc.), but the value is overridden by individual tools (ar, mslib, sgiar, sunar, tlib, etc.) to reflect the names of the libraries they create.
   "LIBPREFIXES", # A list of all legal prefixes for library file names. When searching for library dependencies, SCons will look for files with these prefixes, the base library name, and suffixes in the $LIBSUFFIXES list.
   # "LIBS", # A list of one or more libraries that will be linked with any executable programs created by this environment.", # The library list will be added to command lines through the automatically-generated $_LIBFLAGS construction variable, which is constructed by appending the values of the $LIBLINKPREFIX and $LIBLINKSUFFIX construction variables to the beginning and end of each filename in $LIBS. Any command lines you define that need the LIBS library list should include $_LIBFLAGS:
   "LIBSUFFIX", # The suffix used for (static) library file names. A default value is set for each platform (posix, win32, os2, etc.), but the value is overridden by individual tools (ar, mslib, sgiar, sunar, tlib, etc.) to reflect the names of the libraries they create.
   "LIBSUFFIXES", # A list of all legal suffixes for library file names. When searching for library dependencies, SCons will look for files with prefixes, in the $LIBPREFIXES list, the base library name, and these suffixes.
   "LICENSE", # The abbreviated name of the license under which this project is released (gpl, lpgl, bsd etc.). See http://www.opensource.org/licenses/alphabetical for a list of license names.
   "LINESEPARATOR", # The separator used by the Substfile and Textfile builders. This value is used between sources when constructing the target. It defaults to the current system line separator.
   "LINGUAS_FILE", # The $LINGUAS_FILE defines file(s) containing list of additional linguas to be processed by POInit, POUpdate or MOFiles builders. It also affects Translate builder. If the variable contains a string, it defines name of the list file. The $LINGUAS_FILE may be a list of file names as well. If $LINGUAS_FILE is set to True (or non-zero numeric value), the list will be read from default file named LINGUAS.
   "LINK", # The linker.
   "LINKCOM", # The command line used to link object files into an executable.
   "LINKCOMSTR", # The string displayed when object files are linked into an executable. If this is not set, then $LINKCOM (the command line) is displayed.
   "LINKFLAGS", # General user options passed to the linker. Note that this variable should not contain -l (or similar) options for linking with the libraries listed in $LIBS, nor -L (or similar) library search path options that scons generates automatically from $LIBPATH. See $_LIBFLAGS above, for the variable that expands to library-link options, and $_LIBDIRFLAGS above, for the variable that expands to library search path options.
   "M4", # The M4 macro preprocessor.
   "M4COM", # The command line used to pass files through the M4 macro preprocessor.
   "M4COMSTR", # The string displayed when a file is passed through the M4 macro preprocessor. If this is not set, then $M4COM (the command line) is displayed.
   "M4FLAGS", # General options passed to the M4 macro preprocessor.
   "MAKEINDEX", # The makeindex generator for the TeX formatter and typesetter and the LaTeX structured formatter and typesetter.
   "MAKEINDEXCOM", # The command line used to call the makeindex generator for the TeX formatter and typesetter and the LaTeX structured formatter and typesetter.
   "MAKEINDEXCOMSTR", # The string displayed when calling the makeindex generator for the TeX formatter and typesetter and the LaTeX structured formatter and typesetter. If this is not set, then $MAKEINDEXCOM (the command line) is displayed.
   "MAKEINDEXFLAGS", # General options passed to the makeindex generator for the TeX formatter and typesetter and the LaTeX structured formatter and typesetter.
   "MAXLINELENGTH", # The maximum number of characters allowed on an external command line. On Win32 systems, link lines longer than this many characters are linked via a temporary file name.
   "MIDL", # The Microsoft IDL compiler.
   "MIDLCOM", # The command line used to pass files to the Microsoft IDL compiler.
   "MIDLCOMSTR", # The string displayed when the Microsoft IDL copmiler is called. If this is not set, then $MIDLCOM (the command line) is displayed.
   "MIDLFLAGS", # General options passed to the Microsoft IDL compiler.
   "MOSUFFIX", # Suffix used for MO files (default: '.mo'). See msgfmt tool and MOFiles builder.
   "MSGFMT", # Absolute path to msgfmt(1) binary, found by Detect(). See msgfmt tool and MOFiles builder.
   "MSGFMTCOM", # Complete command line to run msgfmt(1) program. See msgfmt tool and MOFiles builder.
   "MSGFMTCOMSTR", # String to display when msgfmt(1) is invoked (default: '', which means ``print $MSGFMTCOM''). See msgfmt tool and MOFiles builder.
   "MSGFMTFLAGS", # Additional flags to msgfmt(1). See msgfmt tool and MOFiles builder.
   "MSGINIT", # Path to msginit(1) program (found via Detect()). See msginit tool and POInit builder.
   "MSGINITCOM", # Complete command line to run msginit(1) program. See msginit tool and POInit builder.
   "MSGINITCOMSTR", # String to display when msginit(1) is invoked (default: '', which means ``print $MSGINITCOM''). See msginit tool and POInit builder.
   "MSGINITFLAGS", # List of additional flags to msginit(1) (default: []). See msginit tool and POInit builder.
   "MSGMERGE", # Absolute path to msgmerge(1) binary as found by Detect(). See msgmerge tool and POUpdate builder.
   "MSGMERGECOM", # Complete command line to run msgmerge(1) command. See msgmerge tool and POUpdate builder.
   "MSGMERGECOMSTR", # String to be displayed when msgmerge(1) is invoked (default: '', which means ``print $MSGMERGECOM''). See msgmerge tool and POUpdate builder.
   "MSGMERGEFLAGS", # Additional flags to msgmerge(1) command. See msgmerge tool and POUpdate builder.
   "MSSDK_DIR", # The directory containing the Microsoft SDK (either Platform SDK or Windows SDK) to be used for compilation.
   "MSSDK_VERSION", # The version string of the Microsoft SDK (either Platform SDK or Windows SDK) to be used for compilation. Supported versions include 6.1, 6.0A, 6.0, 2003R2 and 2003R1.
   "MSVC_BATCH", # When set to any true value, specifies that SCons should batch compilation of object files when calling the Microsoft Visual C/C++ compiler. All compilations of source files from the same source directory that generate target files in a same output directory and were configured in SCons using the same construction environment will be built in a single call to the compiler. Only source files that have changed since their object files were built will be passed to each compiler invocation (via the $CHANGED_SOURCES construction variable). Any compilations where the object (target) file base name (minus the .obj) does not match the source file base name will be compiled separately.
   "MSVC_USE_SCRIPT", # Use a batch script to set up Microsoft Visual Studio compiler", # $MSVC_USE_SCRIPT overrides $MSVC_VERSION and $TARGET_ARCH. If set to the name of a Visual Studio .bat file (e.g. vcvars.bat), SCons will run that bat file and extract the relevant variables from the result (typically %INCLUDE%, %LIB%, and %PATH%). Setting MSVC_USE_SCRIPT to None bypasses the Visual Studio autodetection entirely; use this if you are running SCons in a Visual Studio cmd window and importing the shell's environment variables.
   "MSVC_VERSION", # Sets the preferred version of Microsoft Visual C/C++ to use.", # If $MSVC_VERSION is not set, SCons will (by default) select the latest version of Visual C/C++ installed on your system. If the specified version isn't installed, tool initialization will fail. This variable must be passed as an argument to the Environment() constructor; setting it later has no effect. Set it to an unexpected value (e.g. "XXX") to see the valid values on your system.
   "MSVS", # When the Microsoft Visual Studio tools are initialized, they set up this dictionary with the following keys:", # VERSION: the version of MSVS being used (can be set via $MSVS_VERSION)", # VERSIONS: the available versions of MSVS installed", # VCINSTALLDIR: installed directory of Visual C++", # VSINSTALLDIR: installed directory of Visual Studio", # FRAMEWORKDIR: installed directory of the .NET framework", # FRAMEWORKVERSIONS: list of installed versions of the .NET framework, sorted latest to oldest.", # FRAMEWORKVERSION: latest installed version of the .NET framework", # FRAMEWORKSDKDIR: installed location of the .NET SDK.", # PLATFORMSDKDIR: installed location of the Platform SDK.", # PLATFORMSDK_MODULES: dictionary of installed Platform SDK modules, where the dictionary keys are keywords for the various modules, and the values are 2-tuples where the first is the release date, and the second is the version number.", # If a value isn't set, it wasn't available in the registry.
   "MSVS_ARCH", # Sets the architecture for which the generated project(s) should build.", # The default value is x86. amd64 is also supported by SCons for some Visual Studio versions. Trying to set $MSVS_ARCH to an architecture that's not supported for a given Visual Studio version will generate an error.
   "MSVS_PROJECT_GUID", # The string placed in a generated Microsoft Visual Studio project file as the value of the ProjectGUID attribute. There is no default value. If not defined, a new GUID is generated.
   "MSVS_SCC_AUX_PATH", # The path name placed in a generated Microsoft Visual Studio project file as the value of the SccAuxPath attribute if the MSVS_SCC_PROVIDER construction variable is also set. There is no default value.
   "MSVS_SCC_CONNECTION_ROOT", # The root path of projects in your SCC workspace, i.e the path under which all project and solution files will be generated. It is used as a reference path from which the relative paths of the generated Microsoft Visual Studio project and solution files are computed. The relative project file path is placed as the value of the SccLocalPath attribute of the project file and as the values of the SccProjectFilePathRelativizedFromConnection[i] (where [i] ranges from 0 to the number of projects in the solution) attributes of the GlobalSection(SourceCodeControl) section of the Microsoft Visual Studio solution file. Similarly the relative solution file path is placed as the values of the SccLocalPath[i] (where [i] ranges from 0 to the number of projects in the solution) attributes of the GlobalSection(SourceCodeControl) section of the Microsoft Visual Studio solution file. This is used only if the MSVS_SCC_PROVIDER construction variable is also set. The default value is the current working directory.
   "MSVS_SCC_PROJECT_NAME", # The project name placed in a generated Microsoft Visual Studio project file as the value of the SccProjectName attribute if the MSVS_SCC_PROVIDER construction variable is also set. In this case the string is also placed in the SccProjectName0 attribute of the GlobalSection(SourceCodeControl) section of the Microsoft Visual Studio solution file. There is no default value.
   "MSVS_SCC_PROVIDER", # The string placed in a generated Microsoft Visual Studio project file as the value of the SccProvider attribute. The string is also placed in the SccProvider0 attribute of the GlobalSection(SourceCodeControl) section of the Microsoft Visual Studio solution file. There is no default value.
   "MSVS_VERSION", # Sets the preferred version of Microsoft Visual Studio to use.", # If $MSVS_VERSION is not set, SCons will (by default) select the latest version of Visual Studio installed on your system. So, if you have version 6 and version 7 (MSVS .NET) installed, it will prefer version 7. You can override this by specifying the MSVS_VERSION variable in the Environment initialization, setting it to the appropriate version ('6.0' or '7.0', for example). If the specified version isn't installed, tool initialization will fail.", # This is obsolete: use $MSVC_VERSION instead. If $MSVS_VERSION is set and $MSVC_VERSION is not, $MSVC_VERSION will be set automatically to $MSVS_VERSION. If both are set to different values, scons will raise an error.
   "MSVSBUILDCOM", # The build command line placed in a generated Microsoft Visual Studio project file. The default is to have Visual Studio invoke SCons with any specified build targets.
   "MSVSCLEANCOM", # The clean command line placed in a generated Microsoft Visual Studio project file. The default is to have Visual Studio invoke SCons with the -c option to remove any specified targets.
   "MSVSENCODING", # The encoding string placed in a generated Microsoft Visual Studio project file. The default is encoding Windows-1252.
   "MSVSPROJECTCOM", # The action used to generate Microsoft Visual Studio project files.
   "MSVSPROJECTSUFFIX", # The suffix used for Microsoft Visual Studio project (DSP) files. The default value is .vcproj when using Visual Studio version 7.x (.NET) or later version, and .dsp when using earlier versions of Visual Studio.
   "MSVSREBUILDCOM", # The rebuild command line placed in a generated Microsoft Visual Studio project file. The default is to have Visual Studio invoke SCons with any specified rebuild targets.
   "MSVSSCONS", # The SCons used in generated Microsoft Visual Studio project files. The default is the version of SCons being used to generate the project file.
   "MSVSSCONSCOM", # The default SCons command used in generated Microsoft Visual Studio project files.
   "MSVSSCONSCRIPT", # The sconscript file (that is, SConstruct or SConscript file) that will be invoked by Visual Studio project files (through the $MSVSSCONSCOM variable). The default is the same sconscript file that contains the call to MSVSProject to build the project file.
   "MSVSSCONSFLAGS", # The SCons flags used in generated Microsoft Visual Studio project files.
   "MSVSSOLUTIONCOM", # The action used to generate Microsoft Visual Studio solution files.
   "MSVSSOLUTIONSUFFIX", # The suffix used for Microsoft Visual Studio solution (DSW) files. The default value is .sln when using Visual Studio version 7.x (.NET), and .dsw when using earlier versions of Visual Studio.
   "MT", # The program used on Windows systems to embed manifests into DLLs and EXEs. See also $WINDOWS_EMBED_MANIFEST.
   "MTEXECOM", # The Windows command line used to embed manifests into executables. See also $MTSHLIBCOM.
   "MTFLAGS", # Flags passed to the $MT manifest embedding program (Windows only).
   "MTSHLIBCOM", # The Windows command line used to embed manifests into shared libraries (DLLs). See also $MTEXECOM.
   "MWCW_VERSION", # The version number of the MetroWerks CodeWarrior C compiler to be used.
   "MWCW_VERSIONS", # A list of installed versions of the MetroWerks CodeWarrior C compiler on this system.
   "NAME", # Specfies the name of the project to package.
   "no_import_lib", # When set to non-zero, suppresses creation of a corresponding Windows static import lib by the SharedLibrary builder when used with MinGW, Microsoft Visual Studio or Metrowerks. This also suppresses creation of an export (.exp) file when using Microsoft Visual Studio.
   "OBJPREFIX", # The prefix used for (static) object file names.
   "OBJSUFFIX", # The suffix used for (static) object file names.
   "P4", # The Perforce executable.
   "P4COM", # The command line used to fetch source files from Perforce.
   "P4COMSTR", # The string displayed when fetching a source file from Perforce. If this is not set, then $P4COM (the command line) is displayed.
   "P4FLAGS", # General options that are passed to Perforce.
   "PACKAGEROOT", # Specifies the directory where all files in resulting archive will be placed if applicable. The default value is "$NAME-$VERSION".
   "PACKAGETYPE", # Selects the package type to build. Currently these are available:", # * msi - Microsoft Installer * rpm - Redhat Package Manger * ipkg - Itsy Package Management System * tarbz2 - compressed tar * targz - compressed tar * zip - zip file * src_tarbz2 - compressed tar source * src_targz - compressed tar source * src_zip - zip file source", # This may be overridden with the "package_type" command line option.
   "PACKAGEVERSION", # The version of the package (not the underlying project). This is currently only used by the rpm packager and should reflect changes in the packaging, not the underlying project code itself.
   "PCH", # The Microsoft Visual C++ precompiled header that will be used when compiling object files. This variable is ignored by tools other than Microsoft Visual C++. When this variable is defined SCons will add options to the compiler command line to cause it to use the precompiled header, and will also set up the dependencies for the PCH file. Example:
   "PCHCOM", # The command line used by the PCH builder to generated a precompiled header.
   "PCHCOMSTR", # The string displayed when generating a precompiled header. If this is not set, then $PCHCOM (the command line) is displayed.
   "PCHPDBFLAGS", # A construction variable that, when expanded, adds the /yD flag to the command line only if the $PDB construction variable is set.
   "PCHSTOP", # This variable specifies how much of a source file is precompiled. This variable is ignored by tools other than Microsoft Visual C++, or when the PCH variable is not being used. When this variable is define it must be a string that is the name of the header that is included at the end of the precompiled portion of the source files, or the empty string if the "#pragma hrdstop" construct is being used:
   "PDB", # The Microsoft Visual C++ PDB file that will store debugging information for object files, shared libraries, and programs. This variable is ignored by tools other than Microsoft Visual C++. When this variable is defined SCons will add options to the compiler and linker command line to cause them to generate external debugging information, and will also set up the dependencies for the PDB file. Example:
   "env['PDB'] = 'hello.pdb'", # The Visual C++ compiler switch that SCons uses by default to generate PDB information is /Z7. This works correctly with parallel (-j) builds because it embeds the debug information in the intermediate object files, as opposed to sharing a single PDB file between multiple object files. This is also the only way to get debug information embedded into a static library. Using the /Zi instead may yield improved link-time performance, although parallel builds will no longer work. You can generate PDB files with the /Zi switch by overriding the default $CCPDBFLAGS variable; see the entry for that variable for specific examples.
   "PDFCOM", # A deprecated synonym for $DVIPDFCOM.
   "PDFLATEX", # The pdflatex utility.
   "PDFLATEXCOM", # The command line used to call the pdflatex utility.
   "PDFLATEXCOMSTR", # The string displayed when calling the pdflatex utility. If this is not set, then $PDFLATEXCOM (the command line) is displayed.
   "PDFLATEXFLAGS", # General options passed to the pdflatex utility.
   "PDFPREFIX", # The prefix used for PDF file names.
   "PDFSUFFIX", # The suffix used for PDF file names.
   "PDFTEX", # The pdftex utility.
   "PDFTEXCOM", # The command line used to call the pdftex utility.
   "PDFTEXCOMSTR", # The string displayed when calling the pdftex utility. If this is not set, then $PDFTEXCOM (the command line) is displayed.
   "PDFTEXFLAGS", # General options passed to the pdftex utility.
   "PKGCHK", # On Solaris systems, the package-checking program that will be used (along with $PKGINFO) to look for installed versions of the Sun PRO C++ compiler. The default is /usr/sbin/pgkchk.
   "PKGINFO", # On Solaris systems, the package information program that will be used (along with $PKGCHK) to look for installed versions of the Sun PRO C++ compiler. The default is pkginfo.
   "PLATFORM", # The name of the platform used to create the Environment. If no platform is specified when the Environment is created, scons autodetects the platform.
   "POAUTOINIT", # The $POAUTOINIT variable, if set to True (on non-zero numeric value), let the msginit tool to automatically initialize missing PO files with msginit(1). This applies to both, POInit and POUpdate builders (and others that use any of them).
   "POCREATE_ALIAS", # Common alias for all PO files created with POInit builder (default: 'po-create'). See msginit tool and POInit builder.
   "POSUFFIX", # Suffix used for PO files (default: '.po') See msginit tool and POInit builder.
   "POTDOMAIN", # The $POTDOMAIN defines default domain, used to generate POT filename as $POTDOMAIN.pot when no POT file name is provided by the user. This applies to POTUpdate, POInit and POUpdate builders (and builders, that use them, e.g. Translate). Normally (if $POTDOMAIN is not defined), the builders use messages.pot as default POT file name.
   "POTSUFFIX", # Suffix used for PO Template files (default: '.pot'). See xgettext tool and POTUpdate builder.
   "POTUPDATE_ALIAS", # Name of the common phony target for all PO Templates created with POUpdate (default: 'pot-update'). See xgettext tool and POTUpdate builder.
   "POUPDATE_ALIAS", # Common alias for all PO files being defined with POUpdate builder (default: 'po-update'). See msgmerge tool and POUpdate builder.
   "PRINT_CMD_LINE_FUNC", # A Python function used to print the command lines as they are executed (assuming command printing is not disabled by the -q or -s options or their equivalents). The function should take four arguments: s, the command being executed (a string), target, the target being built (file node, list, or string name(s)), source, the source(s) used (file node, list, or string name(s)), and env, the environment being used.", # The function must do the printing itself. The default implementation, used if this variable is not set or is None, is:
   "PROGEMITTER", # TODO
   "PROGPREFIX", # The prefix used for executable file names.
   "PROGSUFFIX", # The suffix used for executable file names.
   "PSCOM", # The command line used to convert TeX DVI files into a PostScript file.
   "PSCOMSTR", # The string displayed when a TeX DVI file is converted into a PostScript file. If this is not set, then $PSCOM (the command line) is displayed.
   "PSPREFIX", # The prefix used for PostScript file names.
   "PSSUFFIX", # The prefix used for PostScript file names.
   "QT_AUTOSCAN", # Turn off scanning for mocable files. Use the Moc Builder to explicitly specify files to run moc on.
   "QT_BINPATH", # The path where the qt binaries are installed. The default value is '$QTDIR/bin'.
   "QT_CPPPATH", # The path where the qt header files are installed. The default value is '$QTDIR/include'. Note: If you set this variable to None, the tool won't change the $CPPPATH construction variable.
   "QT_DEBUG", # Prints lots of debugging information while scanning for moc files.
   "QT_LIB", # Default value is 'qt'. You may want to set this to 'qt-mt'. Note: If you set this variable to None, the tool won't change the $LIBS variable.
   "QT_LIBPATH", # The path where the qt libraries are installed. The default value is '$QTDIR/lib'. Note: If you set this variable to None, the tool won't change the $LIBPATH construction variable.
   "QT_MOC", # Default value is '$QT_BINPATH/moc'.
   "QT_MOCCXXPREFIX", # Default value is ''. Prefix for moc output files, when source is a cxx file.
   "QT_MOCCXXSUFFIX", # Default value is '.moc'. Suffix for moc output files, when source is a cxx file.
   "QT_MOCFROMCXXCOM", # Command to generate a moc file from a cpp file.
   "QT_MOCFROMCXXCOMSTR", # The string displayed when generating a moc file from a cpp file. If this is not set, then $QT_MOCFROMCXXCOM (the command line) is displayed.
   "QT_MOCFROMCXXFLAGS", # Default value is '-i'. These flags are passed to moc, when moccing a C++ file.
   "QT_MOCFROMHCOM", # Command to generate a moc file from a header.
   "QT_MOCFROMHCOMSTR", # The string displayed when generating a moc file from a cpp file. If this is not set, then $QT_MOCFROMHCOM (the command line) is displayed.
   "QT_MOCFROMHFLAGS", # Default value is ''. These flags are passed to moc, when moccing a header file.
   "QT_MOCHPREFIX", # Default value is 'moc_'. Prefix for moc output files, when source is a header.
   "QT_MOCHSUFFIX", # Default value is '$CXXFILESUFFIX'. Suffix for moc output files, when source is a header.
   "QT_UIC", # Default value is '$QT_BINPATH/uic'.
   "QT_UICCOM", # Command to generate header files from .ui files.
   "QT_UICCOMSTR", # The string displayed when generating header files from .ui files. If this is not set, then $QT_UICCOM (the command line) is displayed.
   "QT_UICDECLFLAGS", # Default value is ''. These flags are passed to uic, when creating a a h file from a .ui file.
   "QT_UICDECLPREFIX", # Default value is ''. Prefix for uic generated header files.
   "QT_UICDECLSUFFIX", # Default value is '.h'. Suffix for uic generated header files.
   "QT_UICIMPLFLAGS", # Default value is ''. These flags are passed to uic, when creating a cxx file from a .ui file.
   "QT_UICIMPLPREFIX", # Default value is 'uic_'. Prefix for uic generated implementation files.
   "QT_UICIMPLSUFFIX", # Default value is '$CXXFILESUFFIX'. Suffix for uic generated implementation files.
   "QT_UISUFFIX", # Default value is '.ui'. Suffix of designer input files.
   "QTDIR", # The qt tool tries to take this from os.environ. It also initializes all QT_* construction variables listed below. (Note that all paths are constructed with python's os.path.join() method, but are listed here with the '/' separator for easier reading.) In addition, the construction environment variables $CPPPATH, $LIBPATH and $LIBS may be modified and the variables $PROGEMITTER, $SHLIBEMITTER and $LIBEMITTER are modified. Because the build-performance is affected when using this tool, you have to explicitly specify it at Environment creation:
   "RANLIB", # The archive indexer.
   "RANLIBCOM", # The command line used to index a static library archive.
   "RANLIBCOMSTR", # The string displayed when a static library archive is indexed. If this is not set, then $RANLIBCOM (the command line) is displayed.
   "RANLIBFLAGS", # General options passed to the archive indexer.
   "RC", # The resource compiler used to build a Microsoft Visual C++ resource file.
   "RCCOM", # The command line used to build a Microsoft Visual C++ resource file.
   "RCCOMSTR", # The string displayed when invoking the resource compiler to build a Microsoft Visual C++ resource file. If this is not set, then $RCCOM (the command line) is displayed.
   "RCFLAGS", # The flags passed to the resource compiler by the RES builder.
   "RCINCFLAGS", # An automatically-generated construction variable containing the command-line options for specifying directories to be searched by the resource compiler. The value of $RCINCFLAGS is created by appending $RCINCPREFIX and $RCINCSUFFIX to the beginning and end of each directory in $CPPPATH.
   "RCINCPREFIX", # The prefix (flag) used to specify an include directory on the resource compiler command line. This will be appended to the beginning of each directory in the $CPPPATH construction variable when the $RCINCFLAGS variable is expanded.
   "RCINCSUFFIX", # The suffix used to specify an include directory on the resource compiler command line. This will be appended to the end of each directory in the $CPPPATH construction variable when the $RCINCFLAGS variable is expanded.
   "RCS", # The RCS executable. Note that this variable is not actually used for the command to fetch source files from RCS; see the $RCS_CO construction variable, below.
   "RCS_CO", # The RCS "checkout" executable, used to fetch source files from RCS.
   "RCS_COCOM", # The command line used to fetch (checkout) source files from RCS.
   "RCS_COCOMSTR", # The string displayed when fetching a source file from RCS. If this is not set, then $RCS_COCOM (the command line) is displayed.
   "RCS_COFLAGS", # Options that are passed to the $RCS_CO command.
   "RDirs", # A function that converts a string into a list of Dir instances by searching the repositories.
   "REGSVR", # The program used on Windows systems to register a newly-built DLL library whenever the SharedLibrary builder is passed a keyword argument of register=1.
   "REGSVRCOM", # The command line used on Windows systems to register a newly-built DLL library whenever the SharedLibrary builder is passed a keyword argument of register=1.
   "REGSVRCOMSTR", # The string displayed when registering a newly-built DLL file. If this is not set, then $REGSVRCOM (the command line) is displayed.
   "REGSVRFLAGS", # Flags passed to the DLL registration program on Windows systems when a newly-built DLL library is registered. By default, this includes the /s that prevents dialog boxes from popping up and requiring user attention.
   "RMIC", # The Java RMI stub compiler.
   "RMICCOM", # The command line used to compile stub and skeleton class files from Java classes that contain RMI implementations. Any options specified in the $RMICFLAGS construction variable are included on this command line.
   "RMICCOMSTR", # The string displayed when compiling stub and skeleton class files from Java classes that contain RMI implementations. If this is not set, then $RMICCOM (the command line) is displayed.
   "RMICFLAGS", # General options passed to the Java RMI stub compiler.
   "RPATH", # A list of paths to search for shared libraries when running programs. Currently only used in the GNU (gnulink), IRIX (sgilink) and Sun (sunlink) linkers. Ignored on platforms and toolchains that don't support it. Note that the paths added to RPATH are not transformed by scons in any way: if you want an absolute path, you must make it absolute yourself.
   "RPATHPREFIX", # The prefix used to specify a directory to be searched for shared libraries when running programs. This will be appended to the beginning of each directory in the $RPATH construction variable when the $_RPATH variable is automatically generated.
   "RPATHSUFFIX", # The suffix used to specify a directory to be searched for shared libraries when running programs. This will be appended to the end of each directory in the $RPATH construction variable when the $_RPATH variable is automatically generated.
   "RPCGEN", # The RPC protocol compiler.
   "RPCGENCLIENTFLAGS", # Options passed to the RPC protocol compiler when generating client side stubs. These are in addition to any flags specified in the $RPCGENFLAGS construction variable.
   "RPCGENFLAGS", # General options passed to the RPC protocol compiler.
   "RPCGENHEADERFLAGS", # Options passed to the RPC protocol compiler when generating a header file. These are in addition to any flags specified in the $RPCGENFLAGS construction variable.
   "RPCGENSERVICEFLAGS", # Options passed to the RPC protocol compiler when generating server side stubs. These are in addition to any flags specified in the $RPCGENFLAGS construction variable.
   "RPCGENXDRFLAGS", # Options passed to the RPC protocol compiler when generating XDR routines. These are in addition to any flags specified in the $RPCGENFLAGS construction variable.
   "SCANNERS", # A list of the available implicit dependency scanners. New file scanners may be added by appending to this list, although the more flexible approach is to associate scanners with a specific Builder. See the sections "Builder Objects" and "Scanner Objects," below, for more information.
   "SCCS", # The SCCS executable.
   "SCCSCOM", # The command line used to fetch source files from SCCS.
   "SCCSCOMSTR", # The string displayed when fetching a source file from a CVS repository. If this is not set, then $SCCSCOM (the command line) is displayed.
   "SCCSFLAGS", # General options that are passed to SCCS.
   "SCCSGETFLAGS", # Options that are passed specifically to the SCCS "get" subcommand. This can be set, for example, to -e to check out editable files from SCCS.
   "SCONS_HOME", # The (optional) path to the SCons library directory, initialized from the external environment. If set, this is used to construct a shorter and more efficient search path in the $MSVSSCONS command line executed from Microsoft Visual Studio project files.
   "SHCC", # The C compiler used for generating shared-library objects.
   "SHCCCOM", # The command line used to compile a C source file to a shared-library object file. Any options specified in the $SHCFLAGS, $SHCCFLAGS and $CPPFLAGS construction variables are included on this command line.
   "SHCCCOMSTR", # The string displayed when a C source file is compiled to a shared object file. If this is not set, then $SHCCCOM (the command line) is displayed.
   "SHCCFLAGS", # Options that are passed to the C and C++ compilers to generate shared-library objects.
   "SHCFLAGS", # Options that are passed to the C compiler (only; not C++) to generate shared-library objects.
   "SHCXX", # The C++ compiler used for generating shared-library objects.
   "SHCXXCOM", # The command line used to compile a C++ source file to a shared-library object file. Any options specified in the $SHCXXFLAGS and $CPPFLAGS construction variables are included on this command line.
   "SHCXXCOMSTR", # The string displayed when a C++ source file is compiled to a shared object file. If this is not set, then $SHCXXCOM (the command line) is displayed.
   "SHCXXFLAGS", # Options that are passed to the C++ compiler to generate shared-library objects.
   "SHELL", # A string naming the shell program that will be passed to the $SPAWN function. See the $SPAWN construction variable for more information.
   "SHF03", # The Fortran 03 compiler used for generating shared-library objects. You should normally set the $SHFORTRAN variable, which specifies the default Fortran compiler for all Fortran versions. You only need to set $SHF03 if you need to use a specific compiler or compiler version for Fortran 03 files.
   "SHF03COM", # The command line used to compile a Fortran 03 source file to a shared-library object file. You only need to set $SHF03COM if you need to use a specific command line for Fortran 03 files. You should normally set the $SHFORTRANCOM variable, which specifies the default command line for all Fortran versions.
   "SHF03COMSTR", # The string displayed when a Fortran 03 source file is compiled to a shared-library object file. If this is not set, then $SHF03COM or $SHFORTRANCOM (the command line) is displayed.
   "SHF03FLAGS", # Options that are passed to the Fortran 03 compiler to generated shared-library objects. You only need to set $SHF03FLAGS if you need to define specific user options for Fortran 03 files. You should normally set the $SHFORTRANFLAGS variable, which specifies the user-specified options passed to the default Fortran compiler for all Fortran versions.
   "SHF03PPCOM", # The command line used to compile a Fortran 03 source file to a shared-library object file after first running the file through the C preprocessor. Any options specified in the $SHF03FLAGS and $CPPFLAGS construction variables are included on this command line. You only need to set $SHF03PPCOM if you need to use a specific C-preprocessor command line for Fortran 03 files. You should normally set the $SHFORTRANPPCOM variable, which specifies the default C-preprocessor command line for all Fortran versions.
   "SHF03PPCOMSTR", # The string displayed when a Fortran 03 source file is compiled to a shared-library object file after first running the file through the C preprocessor. If this is not set, then $SHF03PPCOM or $SHFORTRANPPCOM (the command line) is displayed.
   "SHF77", # The Fortran 77 compiler used for generating shared-library objects. You should normally set the $SHFORTRAN variable, which specifies the default Fortran compiler for all Fortran versions. You only need to set $SHF77 if you need to use a specific compiler or compiler version for Fortran 77 files.
   "SHF77COM", # The command line used to compile a Fortran 77 source file to a shared-library object file. You only need to set $SHF77COM if you need to use a specific command line for Fortran 77 files. You should normally set the $SHFORTRANCOM variable, which specifies the default command line for all Fortran versions.
   "SHF77COMSTR", # The string displayed when a Fortran 77 source file is compiled to a shared-library object file. If this is not set, then $SHF77COM or $SHFORTRANCOM (the command line) is displayed.
   "SHF77FLAGS", # Options that are passed to the Fortran 77 compiler to generated shared-library objects. You only need to set $SHF77FLAGS if you need to define specific user options for Fortran 77 files. You should normally set the $SHFORTRANFLAGS variable, which specifies the user-specified options passed to the default Fortran compiler for all Fortran versions.
   "SHF77PPCOM", # The command line used to compile a Fortran 77 source file to a shared-library object file after first running the file through the C preprocessor. Any options specified in the $SHF77FLAGS and $CPPFLAGS construction variables are included on this command line. You only need to set $SHF77PPCOM if you need to use a specific C-preprocessor command line for Fortran 77 files. You should normally set the $SHFORTRANPPCOM variable, which specifies the default C-preprocessor command line for all Fortran versions.
   "SHF77PPCOMSTR", # The string displayed when a Fortran 77 source file is compiled to a shared-library object file after first running the file through the C preprocessor. If this is not set, then $SHF77PPCOM or $SHFORTRANPPCOM (the command line) is displayed.
   "SHF90", # The Fortran 90 compiler used for generating shared-library objects. You should normally set the $SHFORTRAN variable, which specifies the default Fortran compiler for all Fortran versions. You only need to set $SHF90 if you need to use a specific compiler or compiler version for Fortran 90 files.
   "SHF90COM", # The command line used to compile a Fortran 90 source file to a shared-library object file. You only need to set $SHF90COM if you need to use a specific command line for Fortran 90 files. You should normally set the $SHFORTRANCOM variable, which specifies the default command line for all Fortran versions.
   "SHF90COMSTR", # The string displayed when a Fortran 90 source file is compiled to a shared-library object file. If this is not set, then $SHF90COM or $SHFORTRANCOM (the command line) is displayed.
   "SHF90FLAGS", # Options that are passed to the Fortran 90 compiler to generated shared-library objects. You only need to set $SHF90FLAGS if you need to define specific user options for Fortran 90 files. You should normally set the $SHFORTRANFLAGS variable, which specifies the user-specified options passed to the default Fortran compiler for all Fortran versions.
   "SHF90PPCOM", # The command line used to compile a Fortran 90 source file to a shared-library object file after first running the file through the C preprocessor. Any options specified in the $SHF90FLAGS and $CPPFLAGS construction variables are included on this command line. You only need to set $SHF90PPCOM if you need to use a specific C-preprocessor command line for Fortran 90 files. You should normally set the $SHFORTRANPPCOM variable, which specifies the default C-preprocessor command line for all Fortran versions.
   "SHF90PPCOMSTR", # The string displayed when a Fortran 90 source file is compiled to a shared-library object file after first running the file through the C preprocessor. If this is not set, then $SHF90PPCOM or $SHFORTRANPPCOM (the command line) is displayed.
   "SHF95", # The Fortran 95 compiler used for generating shared-library objects. You should normally set the $SHFORTRAN variable, which specifies the default Fortran compiler for all Fortran versions. You only need to set $SHF95 if you need to use a specific compiler or compiler version for Fortran 95 files.
   "SHF95COM", # The command line used to compile a Fortran 95 source file to a shared-library object file. You only need to set $SHF95COM if you need to use a specific command line for Fortran 95 files. You should normally set the $SHFORTRANCOM variable, which specifies the default command line for all Fortran versions.
   "SHF95COMSTR", # The string displayed when a Fortran 95 source file is compiled to a shared-library object file. If this is not set, then $SHF95COM or $SHFORTRANCOM (the command line) is displayed.
   "SHF95FLAGS", # Options that are passed to the Fortran 95 compiler to generated shared-library objects. You only need to set $SHF95FLAGS if you need to define specific user options for Fortran 95 files. You should normally set the $SHFORTRANFLAGS variable, which specifies the user-specified options passed to the default Fortran compiler for all Fortran versions.
   "SHF95PPCOM", # The command line used to compile a Fortran 95 source file to a shared-library object file after first running the file through the C preprocessor. Any options specified in the $SHF95FLAGS and $CPPFLAGS construction variables are included on this command line. You only need to set $SHF95PPCOM if you need to use a specific C-preprocessor command line for Fortran 95 files. You should normally set the $SHFORTRANPPCOM variable, which specifies the default C-preprocessor command line for all Fortran versions.
   "SHF95PPCOMSTR", # The string displayed when a Fortran 95 source file is compiled to a shared-library object file after first running the file through the C preprocessor. If this is not set, then $SHF95PPCOM or $SHFORTRANPPCOM (the command line) is displayed.
   "SHFORTRAN", # The default Fortran compiler used for generating shared-library objects.
   "SHFORTRANCOM", # The command line used to compile a Fortran source file to a shared-library object file.
   "SHFORTRANCOMSTR", # The string displayed when a Fortran source file is compiled to a shared-library object file. If this is not set, then $SHFORTRANCOM (the command line) is displayed.
   "SHFORTRANFLAGS", # Options that are passed to the Fortran compiler to generate shared-library objects.
   "SHFORTRANPPCOM", # The command line used to compile a Fortran source file to a shared-library object file after first running the file through the C preprocessor. Any options specified in the $SHFORTRANFLAGS and $CPPFLAGS construction variables are included on this command line.
   "SHFORTRANPPCOMSTR", # The string displayed when a Fortran source file is compiled to a shared-library object file after first running the file through the C preprocessor. If this is not set, then $SHFORTRANPPCOM (the command line) is displayed.
   "SHLIBEMITTER", # TODO
   "SHLIBPREFIX", # The prefix used for shared library file names.
   "SHLIBSUFFIX", # The suffix used for shared library file names.
   "SHLIBVERSION", # When this construction variable is defined, a versioned shared library is created. This modifies the $SHLINKFLAGS as required, adds the version number to the library name, and creates the symlinks that are needed. $SHLIBVERSION needs to be of the form X.Y.Z, where X and Y are numbers, and Z is a number but can also contain letters to designate alpha, beta, or release candidate patch levels.
   "SHLINK", # The linker for programs that use shared libraries.
   "SHLINKCOM", # The command line used to link programs using shared libraries.
   "SHLINKCOMSTR", # The string displayed when programs using shared libraries are linked. If this is not set, then $SHLINKCOM (the command line) is displayed.
   "SHLINKFLAGS", # General user options passed to the linker for programs using shared libraries. Note that this variable should not contain -l (or similar) options for linking with the libraries listed in $LIBS, nor -L (or similar) include search path options that scons generates automatically from $LIBPATH. See $_LIBFLAGS above, for the variable that expands to library-link options, and $_LIBDIRFLAGS above, for the variable that expands to library search path options.
   "SHOBJPREFIX", # The prefix used for shared object file names.
   "SHOBJSUFFIX", # The suffix used for shared object file names.
   "SOURCE", # A reserved variable name that may not be set or used in a construction environment. (See "Variable Substitution," below.)
   "SOURCE_URL", # The URL (web address) of the location from which the project was retrieved. This is used to fill in the Source: field in the controlling information for Ipkg and RPM packages.
   "SOURCES", # A reserved variable name that may not be set or used in a construction environment. (See "Variable Substitution," below.)
   "SPAWN", # A command interpreter function that will be called to execute command line strings. The function must expect the following arguments:
   "def spawn(shell, escape, cmd, args, env):", # sh is a string naming the shell program to use. escape is a function that can be called to escape shell special characters in the command line. cmd is the path to the command to be executed. args is the arguments to the command. env is a dictionary of the environment variables in which the command should be executed.
   "SUBST_DICT", # The dictionary used by the Substfile or Textfile builders for substitution values. It can be anything acceptable to the dict() constructor, so in addition to a dictionary, lists of tuples are also acceptable.
   "SUBSTFILEPREFIX", # The prefix used for Substfile file names, the null string by default.
   "SUBSTFILESUFFIX", # The suffix used for Substfile file names, the null string by default.
   "SUMMARY", # A short summary of what the project is about. This is used to fill in the Summary: field in the controlling information for Ipkg and RPM packages, and as the Description: field in MSI packages.
   "SWIG", # The scripting language wrapper and interface generator.
   "SWIGCFILESUFFIX", # The suffix that will be used for intermediate C source files generated by the scripting language wrapper and interface generator. The default value is _wrap$CFILESUFFIX. By default, this value is used whenever the -c++ option is not specified as part of the $SWIGFLAGS construction variable.
   "SWIGCOM", # The command line used to call the scripting language wrapper and interface generator.
   "SWIGCOMSTR", # The string displayed when calling the scripting language wrapper and interface generator. If this is not set, then $SWIGCOM (the command line) is displayed.
   "SWIGCXXFILESUFFIX", # The suffix that will be used for intermediate C++ source files generated by the scripting language wrapper and interface generator. The default value is _wrap$CFILESUFFIX. By default, this value is used whenever the -c++ option is specified as part of the $SWIGFLAGS construction variable.
   "SWIGDIRECTORSUFFIX", # The suffix that will be used for intermediate C++ header files generated by the scripting language wrapper and interface generator. These are only generated for C++ code when the SWIG 'directors' feature is turned on. The default value is _wrap.h.
   "SWIGFLAGS", # General options passed to the scripting language wrapper and interface generator. This is where you should set -python, -perl5, -tcl, or whatever other options you want to specify to SWIG. If you set the -c++ option in this variable, scons will, by default, generate a C++ intermediate source file with the extension that is specified as the $CXXFILESUFFIX variable.
   "SWIGINCPREFIX", # The prefix used to specify an include directory on the SWIG command line. This will be appended to the beginning of each directory in the $SWIGPATH construction variable when the $_SWIGINCFLAGS variable is automatically generated.
   "SWIGINCSUFFIX", # The suffix used to specify an include directory on the SWIG command line. This will be appended to the end of each directory in the $SWIGPATH construction variable when the $_SWIGINCFLAGS variable is automatically generated.
   "SWIGOUTDIR", # Specifies the output directory in which the scripting language wrapper and interface generator should place generated language-specific files. This will be used by SCons to identify the files that will be generated by the swig call, and translated into the swig -outdir option on the command line.
   "SWIGPATH", # The list of directories that the scripting language wrapper and interface generate will search for included files. The SWIG implicit dependency scanner will search these directories for include files. The default is to use the same path specified as $CPPPATH.", # Don't explicitly put include directory arguments in SWIGFLAGS; the result will be non-portable and the directories will not be searched by the dependency scanner. Note: directory names in SWIGPATH will be looked-up relative to the SConscript directory when they are used in a command. To force scons to look-up a directory relative to the root of the source tree use #:
   "SWIGVERSION", # The version number of the SWIG tool.
   "TAR", # The tar archiver.
   "TARCOM", # The command line used to call the tar archiver.
   "TARCOMSTR", # The string displayed when archiving files using the tar archiver. If this is not set, then $TARCOM (the command line) is displayed.
   "TARFLAGS", # General options passed to the tar archiver.
   "TARGET", # A reserved variable name that may not be set or used in a construction environment. (See "Variable Substitution," below.)
   "TARGET_ARCH", # Sets the target architecture for Visual Studio compiler (i.e. the arch of the binaries generated by the compiler). If not set, default to $HOST_ARCH, or, if that is unset, to the architecture of the running machine's OS (note that the python build or architecture has no effect). This variable must be passed as an argument to the Environment() constructor; setting it later has no effect. This is currently only used on Windows, but in the future it will be used on other OSes as well.", # Valid values for Windows are x86, i386 (for 32 bits); amd64, emt64, x86_64 (for 64 bits); and ia64 (Itanium). For example, if you want to compile 64-bit binaries, you would set TARGET_ARCH='x86_64' in your SCons environment.", # The name of the target hardware architecture for the compiled objects created by this Environment. This defaults to the value of HOST_ARCH, and the user can override it. Currently only set for Win32.
   "TARGET_OS", # The name of the target operating system for the compiled objects created by this Environment. This defaults to the value of HOST_OS, and the user can override it. Currently only set for Win32.
   "TARGETS", # A reserved variable name that may not be set or used in a construction environment. (See "Variable Substitution," below.)
   "TARSUFFIX", # The suffix used for tar file names.
   "TEMPFILEPREFIX", # The prefix for a temporary file used to execute lines longer than $MAXLINELENGTH. The default is '@'. This may be set for toolchains that use other values, such as '-@' for the diab compiler or '-via' for ARM toolchain.
   "TEX", # The TeX formatter and typesetter.
   "TEXCOM", # The command line used to call the TeX formatter and typesetter.
   "TEXCOMSTR", # The string displayed when calling the TeX formatter and typesetter. If this is not set, then $TEXCOM (the command line) is displayed.
   "TEXFLAGS", # General options passed to the TeX formatter and typesetter.
   "TEXINPUTS", # List of directories that the LaTeX program will search for include directories. The LaTeX implicit dependency scanner will search these directories for \include and \import files.
   "TEXTFILEPREFIX", # The prefix used for Textfile file names, the null string by default.
   "TEXTFILESUFFIX", # The suffix used for Textfile file names; .txt by default.
   "TOOLS", # A list of the names of the Tool specifications that are part of this construction environment.
   "UNCHANGED_SOURCES", # A reserved variable name that may not be set or used in a construction environment. (See "Variable Substitution," below.)
   "UNCHANGED_TARGETS", # A reserved variable name that may not be set or used in a construction environment. (See "Variable Substitution," below.)
   "VENDOR", # The person or organization who supply the packaged software. This is used to fill in the Vendor: field in the controlling information for RPM packages, and the Manufacturer: field in the controlling information for MSI packages.
   "VERSION", # The version of the project, specified as a string.
   "WIN32_INSERT_DEF", # A deprecated synonym for $WINDOWS_INSERT_DEF.
   "WIN32DEFPREFIX", # A deprecated synonym for $WINDOWSDEFPREFIX.
   "WIN32DEFSUFFIX", # A deprecated synonym for $WINDOWSDEFSUFFIX.
   "WIN32EXPPREFIX", # A deprecated synonym for $WINDOWSEXPSUFFIX.
   "WIN32EXPSUFFIX", # A deprecated synonym for $WINDOWSEXPSUFFIX.
   "WINDOWS_EMBED_MANIFEST", # Set this variable to True or 1 to embed the compiler-generated manifest (normally ${TARGET}.manifest) into all Windows exes and DLLs built with this environment, as a resource during their link step. This is done using $MT and $MTEXECOM and $MTSHLIBCOM.
   "WINDOWS_INSERT_DEF", # When this is set to true, a library build of a Windows shared library (.dll file) will also build a corresponding .def file at the same time, if a .def file is not already listed as a build target. The default is 0 (do not build a .def file).
   "WINDOWS_INSERT_MANIFEST", # When this is set to true, scons will be aware of the .manifest files generated by Microsoft Visua C/C++ 8.
   "WINDOWSDEFPREFIX", # The prefix used for Windows .def file names.
   "WINDOWSDEFSUFFIX", # The suffix used for Windows .def file names.
   "WINDOWSEXPPREFIX", # The prefix used for Windows .exp file names.
   "WINDOWSEXPSUFFIX", # The suffix used for Windows .exp file names.
   "WINDOWSPROGMANIFESTPREFIX", # The prefix used for executable program .manifest files generated by Microsoft Visual C/C++.
   "WINDOWSPROGMANIFESTSUFFIX", # The suffix used for executable program .manifest files generated by Microsoft Visual C/C++.
   "WINDOWSSHLIBMANIFESTPREFIX", # The prefix used for shared library .manifest files generated by Microsoft Visual C/C++.
   "WINDOWSSHLIBMANIFESTSUFFIX", # The suffix used for shared library .manifest files generated by Microsoft Visual C/C++.
   "X_IPK_DEPENDS", # This is used to fill in the Depends: field in the controlling information for Ipkg packages.
   "X_IPK_DESCRIPTION", # This is used to fill in the Description: field in the controlling information for Ipkg packages. The default value is $SUMMARY\n$DESCRIPTION
   "X_IPK_MAINTAINER", # This is used to fill in the Maintainer: field in the controlling information for Ipkg packages.
   "X_IPK_PRIORITY", # This is used to fill in the Priority: field in the controlling information for Ipkg packages.
   "X_IPK_SECTION", # This is used to fill in the Section: field in the controlling information for Ipkg packages.
   "X_MSI_LANGUAGE", # This is used to fill in the Language: attribute in the controlling information for MSI packages.
   "X_MSI_LICENSE_TEXT", # The text of the software license in RTF format. Carriage return characters will be replaced with the RTF equivalent \\par.
   "X_MSI_UPGRADE_CODE", # TODO
   "X_RPM_AUTOREQPROV", # This is used to fill in the AutoReqProv: field in the RPM .spec file.
   "X_RPM_BUILD", # internal, but overridable
   "X_RPM_BUILDREQUIRES", # This is used to fill in the BuildRequires: field in the RPM .spec file.
   "X_RPM_BUILDROOT", # internal, but overridable
   "X_RPM_CLEAN", # internal, but overridable
   "X_RPM_CONFLICTS", # This is used to fill in the Conflicts: field in the RPM .spec file.
   "X_RPM_DEFATTR", # This value is used as the default attributes for the files in the RPM package. The default value is (-,root,root).
   "X_RPM_DISTRIBUTION", # This is used to fill in the Distribution: field in the RPM .spec file.
   "X_RPM_EPOCH", # This is used to fill in the Epoch: field in the controlling information for RPM packages.
   "X_RPM_EXCLUDEARCH", # This is used to fill in the ExcludeArch: field in the RPM .spec file.
   "X_RPM_EXLUSIVEARCH", # This is used to fill in the ExclusiveArch: field in the RPM .spec file.
   "X_RPM_GROUP", # This is used to fill in the Group: field in the RPM .spec file.
   "X_RPM_GROUP_lang", # This is used to fill in the Group(lang): field in the RPM .spec file. Note that lang is not literal and should be replaced by the appropriate language code.
   "X_RPM_ICON", # This is used to fill in the Icon: field in the RPM .spec file.
   "X_RPM_INSTALL", # internal, but overridable
   "X_RPM_PACKAGER", # This is used to fill in the Packager: field in the RPM .spec file.
   "X_RPM_POSTINSTALL", # This is used to fill in the %post: section in the RPM .spec file.
   "X_RPM_POSTUNINSTALL", # This is used to fill in the %postun: section in the RPM .spec file.
   "X_RPM_PREFIX", # This is used to fill in the Prefix: field in the RPM .spec file.
   "X_RPM_PREINSTALL", # This is used to fill in the %pre: section in the RPM .spec file.
   "X_RPM_PREP", # internal, but overridable
   "X_RPM_PREUNINSTALL", # This is used to fill in the %preun: section in the RPM .spec file.
   "X_RPM_PROVIDES", # This is used to fill in the Provides: field in the RPM .spec file.
   "X_RPM_REQUIRES", # This is used to fill in the Requires: field in the RPM .spec file.
   "X_RPM_SERIAL", # This is used to fill in the Serial: field in the RPM .spec file.
   "X_RPM_URL", # This is used to fill in the Url: field in the RPM .spec file.
   "XGETTEXT", # Path to xgettext(1) program (found via Detect()). See xgettext tool and POTUpdate builder.
   "XGETTEXTCOM", # Complete xgettext command line. See xgettext tool and POTUpdate builder.
   "XGETTEXTCOMSTR", # A string that is shown when xgettext(1) command is invoked (default: '', which means "print $XGETTEXTCOM"). See xgettext tool and POTUpdate builder.
   "XGETTEXTFLAGS", # Additional flags to xgettext(1). See xgettext tool and POTUpdate builder.
   "XGETTEXTFROM", # Name of file containing list of xgettext(1)'s source files. Autotools' users know this as POTFILES.in so they will in most cases set XGETTEXTFROM="POTFILES.in" here. The $XGETTEXTFROM files have same syntax and semantics as the well known GNU POTFILES.in. See xgettext tool and POTUpdate builder.
   "XGETTEXTFROMPREFIX", # This flag is used to add single $XGETTEXTFROM file to xgettext(1)'s commandline (default: '-f').
   "XGETTEXTFROMSUFFIX", # (default: '')
   "XGETTEXTPATH", # List of directories, there xgettext(1) will look for source files (default: []).", # Note", # This variable works only together with $XGETTEXTFROM", # See also xgettext tool and POTUpdate builder.
   "XGETTEXTPATHPREFIX", # This flag is used to add single search path to xgettext(1)'s commandline (default: '-D').
   "XGETTEXTPATHSUFFIX", # (default: '')
   "YACC", # The parser generator.
   "YACCCOM", # The command line used to call the parser generator to generate a source file.
   "YACCCOMSTR", # The string displayed when generating a source file using the parser generator. If this is not set, then $YACCCOM (the command line) is displayed.
   "YACCFLAGS", # General options passed to the parser generator. If $YACCFLAGS contains a -d option, SCons assumes that the call will also create a .h file (if the yacc source file ends in a .y suffix) or a .hpp file (if the yacc source file ends in a .yy suffix)
   "YACCHFILESUFFIX", # The suffix of the C header file generated by the parser generator when the -d option is used. Note that setting this variable does not cause the parser generator to generate a header file with the specified suffix, it exists to allow you to specify what suffix the parser generator will use of its own accord. The default value is .h.
   "YACCHXXFILESUFFIX", # The suffix of the C++ header file generated by the parser generator when the -d option is used. Note that setting this variable does not cause the parser generator to generate a header file with the specified suffix, it exists to allow you to specify what suffix the parser generator will use of its own accord. The default value is .hpp, except on Mac OS X, where the default is ${TARGET.suffix}.h. because the default bison parser generator just appends .h to the name of the generated C++ file.
   "YACCVCGFILESUFFIX", # The suffix of the file containing the VCG grammar automaton definition when the --graph= option is used. Note that setting this variable does not cause the parser generator to generate a VCG file with the specified suffix, it exists to allow you to specify what suffix the parser generator will use of its own accord. The default value is .vcg.
   "ZIP", # The zip compression and file packaging utility.
   "ZIPCOM", # The command line used to call the zip utility, or the internal Python function used to create a zip archive.
   "ZIPCOMPRESSION", # The compression flag from the Python zipfile module used by the internal Python function to control whether the zip archive is compressed or not. The default value is zipfile.ZIP_DEFLATED, which creates a compressed zip archive. This value has no effect if the zipfile module is unavailable.
   "ZIPCOMSTR", # The string displayed when archiving files using the zip utility. If this is not set, then $ZIPCOM (the command line or internal Python function) is displayed.
   "ZIPFLAGS", # General options passed to the zip utility.
   "ZIPROOT", # An optional zip root directory (default empty). The filenames stored in the zip file will be relative to this directory, if given. Otherwise the filenames are relative to the current directory of the command. For instance:
]
