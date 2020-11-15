#!/usr/bin/env python3

import sys
import os
import argparse
from pathlib import Path
import shutil
import re


_debug = False


_re_variable = re.compile("\{(?P<variable>[ \w]+)\}")


def _parse_arguments():
    parser = argparse.ArgumentParser(description="Create standard directory structures for projects.")
    parser.add_argument("project_template", type=str, help="the template to use for the project")
    parser.add_argument("destination", type=str, action="store", help="directory to create for the project")
    parser.add_argument("-d", "--debug", action="store_true", dest="debug", help="print debugging information")
    args = parser.parse_args()
    return args


def _get_project_template_path(pt):
    pt_path = Path(pt)
    if pt_path.exists():
        return pt_path
    try:
        xdg_config = Path(os.environ['XDG_CONFIG_HOME'])
    except KeyError:
        xdg_config = Path('~/.config').expanduser()
    config_path = xdg_config / 'mkprojectdir' / 'project_templates'
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


def _find_variables(destination):
    variables = set()
    for f in destination.iterdir():
        matches = re.findall(_re_variable, f.name)
        if matches:
            for match in matches:
                variables.add(match)
        if f.is_dir():
            variables = variables.union(_find_variables(f))
    return variables


def _get_replacements(variables):
    replacements = {}
    for variable in variables:
        replacement = input("%s: " % variable)
        replacements[variable] = replacement
    return replacements


def _replace_variables(destination, replacements):
    for f in destination.iterdir():
        if f.is_dir():
            _replace_variables(f, replacements)

        name = f.name
        complete = False
        modified = False
        while not complete:
            match = _re_variable.search(name)
            if match:
                modified = True
                variable = match.group('variable')
                name = name.replace("{%s}" % variable, replacements[variable])
            else:
                complete = True
        if modified:
            f.rename(f.parent / name)


def _main():
    args = _parse_arguments()
    global _debug
    _debug = args.debug
    try:
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

        variables = _find_variables(destination)
        if variables:
            print ("The specified template included variables for replacement.")
            print ("Please enter the desired values.")
            replacements = _get_replacements(variables)
            _replace_variables(destination, replacements)
    except KeyboardInterrupt:
        print()
        sys.exit(0)


if __name__ == "__main__":
    _main()
