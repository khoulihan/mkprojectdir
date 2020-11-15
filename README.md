# mkprojectdir

A script to create standard directory structures for projects.

Copyright (c) 2020 by Kevin Houlihan

License: MIT, see LICENSE for more details.

## Prerequisites

The script depends on Python 3.7 (though possibly earlier versions of Python 3 will work fine).

## Usage

The script takes two arguments - a project template and a destination. The template is copied to the destination.

### Project Template

The project template can be a path to a directory, or the name of a template in the `project_templates` directory in the script's config directory (`~/.config/mkprojectdir` by default).

A template is just a directory structure with whatever files are required for the project type in question.

File and directory names in a template can include variables wrapped in braces (e.g. `{Project Name}.md`). In this event, values will be requested interactively and these variables will be replaced in the destination.
