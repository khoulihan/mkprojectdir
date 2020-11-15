#!/usr/bin/env python3

import sys
import os
import argparse
from pathlib import Path
import shutil


_debug = False


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
            shutil.copy(content, destination)
    except KeyboardInterrupt:
        print()
        sys.exit(0)


if __name__ == "__main__":
    _main()
