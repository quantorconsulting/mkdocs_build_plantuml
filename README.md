![PyPI - Downloads](https://img.shields.io/pypi/dm/mkdocs-build-plantuml-plugin)

# MkDocs-Build-Plantuml-Plugin

## Table of Contents

- [About the Project](#about-the-project)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Dark Mode Support](#dark-mode-support)
- [Known restrictions](#known-restrictions)
- [Contributing](#contributing)

## About the Project

This plugin automates the generation of PlantUML image files when using `mkdocs serve`.

The motivation behind this plugin is to provide a solution for users who prefer not to use inline diagrams and have encountered challenges with non-functional !includes.

**Note**: If you want inline diagrams in your Markdown files

````markdown
```plantuml
Alice -> Bob
```
````

this plugin does _not_ meet your requirements. Please check out [plantuml-markdown](https://github.com/mikitex70/plantuml-markdown) which does exactly that.

## Prerequisites

You need to have installed:

- Python3 (>= 3.12)
- [MkDocs](https://www.mkdocs.org)
- Java for Plantuml (If running locally)
- [Plantuml](https://plantuml.com) (if running locally)
- This plugin (needs [httplib2](https://pypi.org/project/httplib2/) for server rendering)

On macOS you can install plantuml with homebrew which puts a plantuml executable in `/usr/local/bin/plantuml`.

## Installation

```shell
pip3 install mkdocs-build-plantuml-plugin
```

## Usage

### Plugin Settings

In `mkdocs.yml` add this plugin section (depicted are the default values):

```yaml
plugins:
  - search
  - build_plantuml:
      render: 'server' # or "local" for local rendering
      bin_path: '/usr/local/bin/plantuml' # ignored when render: server
      server: 'http://www.plantuml.com/plantuml' # official plantuml server
      disable_ssl_certificate_validation: true # for self-signed and invalid certs
      output_format: 'svg' # or "png"
      allow_multiple_roots: false # in case your codebase contains more locations for diagrams (all ending in diagram_root)
      diagram_root: 'docs/diagrams' # should reside under docs_dir
      output_folder: 'out'
      input_folder: 'src'
      input_extensions: '' # comma separated list of extensions to parse, by default every file is parsed
```

It is recommended to use the `server` option, which is much faster than `local`.

### Example folder structure

This would result in this directory layout:

```python
docs/                         # the default MkDocs docs_dir directory
  diagrams/
    include/                  # for include files like theme.puml etc (optional, won't be generated)
    out/                      # the generated images, which can be included in your md files
      subdir1/file1.svg       # you can organise your diagrams in subfolders, see below
      file.svg
    src/                      # the Plantuml sources
      subdir1/file1.puml
      subdir2/
      file.puml
mkdocs.yml                    # mkdocs configuration file

```

When starting with `mkdocs serve`, it will create all diagrams initially.

Afterwards, it checks if the `*.puml` (or other ending) file has a newer timestamp than the corresponding file in out. If so, it will generate a new image (works also with includes). This way, it won‘t take long until the site reloads and does not get into a loop.

### Including generated images

Inside your `index.md` or any other Markdown file you can then reference any created image as usual:

```markdown
# My MkDocs Document

## Example Plantuml Images

![file](diagrams/out/file.svg)

![file1](diagrams/out/subdir1/file1.svg)
```

## Dark Mode Support

Since Version 1.4 this plugin can support dark mode when rendering with `server` (prefers-color-scheme).

**Note**: Not in local mode, only server rendering mode

1. Grab a general (ie. for [Material Theme](https://squidfunk.github.io/mkdocs-material/)) dark mode support css file (i.e. from [henrywhitaker3/mkdocs-material-dark-theme](https://github.com/henrywhitaker3/mkdocs-material-dark-theme)) for your theme
1. Enable theme support in this plugin:

        - build_plantuml:
            [...]
            theme_enabled: true
            theme_folder: "include/themes"
            theme_light: "light.puml"
            theme_dark: "dark.puml"

1. You have to provide two puml theme files, ie mydarkmode.puml and mylightmode.puml
1. In the out directory a `<file>.<ext>` will be created and additionally a `<file>_dark.<ext>`
1. Insert your images in markdown with `![file](diagrams/out/file.svg#darkable)` (this selector is then used in the [JS file](example/docs/javascript/images_dark.js) to know which images have to be exchanged)
1. provide [`extra_javascript`](./example/docs/javascript/images_dark.js) file which handles the switch

You can find an example in the [example folder](./example/)

### Example Output

![DarkMode](./switch_dark_mode.gif)

## Known restrictions

- If you use `!include` and the `render: "server"` option, this plugin merges those files manually. If there are any issues or side effects because of that, please open a ticket.
- Dark mode / theme support is currently only available in server rendering mode.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.
