#include "Python.h"

int main(int argc, char **argv)
{{
    int sts;
    Py_FrozenFlag = 1;  // disable warnings from Python's getpath.c
    _PyRandom_Init();
    PySys_ResetWarnOptions();
    _PyOS_ResetGetOpt();
    Py_Initialize();
    Py_SetProgramName(argv[0]);
    PySys_SetArgv(argc, argv);

    if (Py_MakePendingCalls() == -1) {{
        PyErr_Print();
        sts = 1;
    }} else {{
        PyObject* main = PyImport_AddModule("__main__");
        PyModule_AddStringConstant(main, "__file__", "{0}");
        sts = PyRun_SimpleString("import {1}; exit({1}.{2}())") != 0;
    }}

    Py_Finalize();
    return sts;
}}
