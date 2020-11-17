# mkprojectdir

A script to create standard directory structures for projects.

Copyright (c) 2020 by Kevin Houlihan

License: MIT, see LICENSE for more details.

## Prerequisites

The script depends on Python 3.7 (though possibly earlier versions of Python 3 will work fine).

## Usage

The script accepts three commands - create, list, and save.

### List

This command accepts no arguments, and just lists the available project templates.

`ls` is another alias for this command.

```
mkprojectdir list
```

### Save

Saves a specified directory as a template. By default the template will have the same name as the directory, but a different name can be specified with the `--name` (`-n` for short) switch.

```
mkprojectdir save --name art ./art_template
```

### Create

Creates a project directory based on a template. This command accepts two arguments - a project template to use, and a destination path.

The project template can be a path to a directory, or the name of a template in the `project_templates` directory in the script's config directory (`~/.config/mkprojectdir` by default). Templates can be saved to this directory using the `save` command described above.

```
mkprojectdir create art ./new_art_project
```

## Project Templates

A template is just a directory structure with whatever files are required for the project type in question.

File and directory names in a template can include variables wrapped in braces (e.g. `{Project Name}.md`). In this event, values will be requested interactively when the template is used, and these variables will be replaced in the destination.

Text files of several types will also be searched for variables to replace. Variables should be wrapped in double braces (`{{...}}`) for markdown, plain-text, HTML, TOML and INI files, and double angle brackets (`<<...>>`) for JSON, YAML and Python files. Other file types are not searched at this time.
