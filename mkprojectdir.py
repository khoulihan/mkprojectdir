#!/usr/bin/env python3

import sys
import os
import argparse
from pathlib import Path
import shutil
import re
import tempfile


_debug = False


_re_fs_variable = re.compile("\{(?P<variable>[ \w]+)\}")
_re_double_brace_variable = re.compile("\{\{(?P<variable>[ \w]+)\}\}")
_re_double_angles_variable = re.compile("\<\<(?P<variable>[ \w]+)\>\>")
_double_brace_suffixes = ['.md', '.txt', '.html', '.toml', '.ini']
_double_angles_suffixes = ['.json', '.yaml', '.py']

def _parse_arguments():
    parser = argparse.ArgumentParser(description="Create standard directory structures for projects.")
    parser.add_argument("-d", "--debug", action="store_true", dest="debug", help="print debugging information")
    subparsers = parser.add_subparsers(dest='command')

    # Create command
    create_parser = subparsers.add_parser('create', aliases=['c', 'mk'], help="create a project directory")
    create_parser.add_argument("project_template", type=str, help="the template to use for the project")
    create_parser.add_argument("destination", type=str, action="store", help="directory to create for the project")
    create_parser.add_argument("--no-subs", action="store_true", dest="no_subs", help="skip requesting or substituting variable values")

    # List templates command
    list_parser = subparsers.add_parser('list', aliases=['ls'], help="list available templates")

    # Save template command
    save_parser = subparsers.add_parser('save', aliases=['s'], help="save a directory as a template")
    save_parser.add_argument("template", type=str, action="store", help="directory to save as a template")
    save_parser.add_argument("-n", "--name", type=str, action="store", dest="name", help="name to use for the template, if it should be different from the original directory name")

    args = parser.parse_args()
    return args


def _get_template_directory():
    try:
        xdg_config = Path(os.environ['XDG_CONFIG_HOME'])
    except KeyError:
        xdg_config = Path('~/.config').expanduser()
    return xdg_config / 'mkprojectdir' / 'project_templates'


def _get_template_backup_directory():
    try:
        xdg_config = Path(os.environ['XDG_CONFIG_HOME'])
    except KeyError:
        xdg_config = Path('~/.config').expanduser()
    return xdg_config / 'mkprojectdir' / 'template_backups'


def _get_project_template_path(pt):
    pt_path = Path(pt)
    if pt_path.exists():
        return pt_path
    config_path = _get_template_directory()
    if not config_path.exists():
        config_path.mkdir(parents=True)
    pt_path = config_path / pt
    if not pt_path.exists():
        raise FileNotFoundError()
    return pt_path


def _verify_destination(destination):
    p = Path(destination)
    if not p.exists():
        p.mkdir()
        return p
    else:
        raise FileExistsError()


def _find_file_variables(f, pattern):
    variables = set()
    contents = f.read_text()
    matches = re.findall(pattern, contents)
    if matches:
        for match in matches:
            variables.add(match)
    return variables


def _find_variables(destination):
    variables = set()
    for f in destination.iterdir():
        matches = re.findall(_re_fs_variable, f.name)
        if matches:
            for match in matches:
                variables.add(match)
        if f.is_dir():
            variables = variables.union(_find_variables(f))
        elif f.suffix:
            if f.suffix in _double_brace_suffixes:
                variables = variables.union(
                    _find_file_variables(f, _re_double_brace_variable)
                )
            elif f.suffix in _double_angles_suffixes:
                variables = variables.union(
                    _find_file_variables(f, _re_double_angles_variable)
                )

    return variables


def _get_replacements(variables):
    replacements = {}
    for variable in variables:
        replacement = input("%s: " % variable)
        replacements[variable] = replacement
    return replacements


def _replace_file_variables(f, pattern, pattern_format, replacements):
    contents = f.read_text()
    complete = False
    modified = False
    while not complete:
        match = pattern.search(contents)
        if match:
            modified = True
            variable = match.group('variable')
            contents = contents.replace(pattern_format % variable, replacements[variable])
        else:
            complete = True
    if modified:
        f.write_text(contents)

def _replace_variables(destination, replacements):
    for f in destination.iterdir():
        if f.is_dir():
            _replace_variables(f, replacements)
        elif f.suffix:
            if f.suffix in _double_brace_suffixes:
                _replace_file_variables(
                    f,
                    _re_double_brace_variable,
                    "{{%s}}",
                    replacements
                )
            elif f.suffix in _double_angles_suffixes:
                _replace_file_variables(
                    f,
                    _re_double_angles_variable,
                    "<<%s>>",
                    replacements
                )

        name = f.name
        complete = False
        modified = False
        while not complete:
            match = _re_fs_variable.search(name)
            if match:
                modified = True
                variable = match.group('variable')
                name = name.replace("{%s}" % variable, replacements[variable])
            else:
                complete = True
        if modified:
            f.rename(f.parent / name)


def _create(args):
    try:
        pt_path = _get_project_template_path(args.project_template)
    except FileNotFoundError as e:
        print ("The specified project template does not exist")
        sys.exit(1)

    try:
        destination = _verify_destination(args.destination)
    except FileExistsError:
        print ("The specified destination already exists.")
        sys.exit(1)
    except FileNotFoundError:
        print ("The specified destination directory could not be created because of missing parents.")
        sys.exit(1)
    except PermissionError:
        print ("The destination directory could not be created due to inadequate permissions.")
        sys.exit(1)

    for content in pt_path.iterdir():
        if content.is_file():
            shutil.copy(content, destination)
        else:
            shutil.copytree(content, destination / content.name, copy_function=shutil.copy)

    if not args.no_subs:
        variables = _find_variables(destination)
        if variables:
            print ("The specified template included variables for replacement.")
            print ("Please enter the desired values.")
            replacements = _get_replacements(variables)
            _replace_variables(destination, replacements)


def _list_templates(args):
    config_path = _get_template_directory()
    if not config_path.exists():
        config_path.mkdir(parents=True)
    print("Available templates:")
    print()
    for template in config_path.iterdir():
        print(template.name)


def _save_template(args):
    config_path = _get_template_directory()
    if not config_path.exists():
        config_path.mkdir(parents=True)

    template = Path(args.template)
    if not template.exists():
        print("The specified template does not exist.")
        sys.exit(1)
    if not template.is_dir():
        print("Only directories can be saved as templates.")
        sys.exit(1)
    name = template.name
    if args.name:
        name = args.name
    saved_path = config_path / name
    if saved_path.exists():
        backup_directory = _get_template_backup_directory()
        if not backup_directory.exists():
            backup_directory.mkdir(parents=True)
        template_backup = backup_directory / name
        if template_backup.exists():
            shutil.rmtree(template_backup)
        shutil.copytree(saved_path, template_backup, copy_function=shutil.copy)
        shutil.rmtree(saved_path)
    shutil.copytree(template, saved_path, copy_function=shutil.copy)


def _main():
    args = _parse_arguments()
    global _debug
    _debug = args.debug
    try:
        if args.command in ["create", "c"]:
            _create(args)
        elif args.command in ["list", "ls"]:
            _list_templates(args)
        elif args.command in ["save", "s"]:
            _save_template(args)
    except KeyboardInterrupt:
        print()
        sys.exit(0)


if __name__ == "__main__":
    _main()
