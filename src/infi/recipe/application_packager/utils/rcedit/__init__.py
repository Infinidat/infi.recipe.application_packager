from logging import getLogger
logger = getLogger(__name__)


def set_icon_in_executable(executable, icon):
    from pkg_resources import resource_filename
    from infi.recipe.application_packager.utils.execute import execute_assert_success
    rcedit = resource_filename(__name__, "rcedit.exe")
    execute_assert_success([rcedit, executable, '--set-icon', icon])


def set_icon_for_executables_in_directory(tempdir, icon):
    from os import walk, path
    for dirpath, dirnames, filenames in walk(tempdir):
        for filename in filter(lambda filename: filename.endswith('exe'), filenames):
            filepath = path.join(dirpath, filename)
            set_icon_in_executable(filepath, icon)


def set_icon_for_executables_in_archive(archive_path, icon):
    from os import listdir, path
    from infi.recipe.application_packager.utils import temporary_directory_context, signtool
    write_mode = 'w:gz' if archive_path.endswith('tar.gz') else 'w'
    with temporary_directory_context() as tempdir:
        with signtool.open_archive(archive_path) as archive:
            archive.extractall(tempdir)
        set_icon_for_executables_in_directory(tempdir, icon)
        if archive_path.endswith('.whl'):
            signtool.rewrite_record_file(tempdir)
        with signtool.open_archive(archive_path, write_mode) as archive:
            for item in listdir(tempdir):
                archive.add(path.join(tempdir, item), item)
