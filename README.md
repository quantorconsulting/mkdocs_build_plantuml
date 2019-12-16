# Mkdocs Plantuml Plugin

Does build you Plantuml diagrams with mkdocs serve automatically. Intend was, that I do not like inline diagrams and stumbled upon issues like non-working `!includes`.

## Prerequesites

You need to have installed

- Python3
- [MkDocs](https://www.mkdocs.org)
- Java for Plantuml (if running locally)
- [Plantuml](https://plantuml.com) (if running locally)
- This plugin (needs httplib2 for server rendering)

On OSX you can install plantuml with homebrew which puts a plantuml executable in `/usr/local/bin/plantuml`.

## Installation

`pip3 install mkdocs_build_plantuml`

## Usage

In `mkdocs.yml` add this plugin section (depicted are the default values):

```yaml
plugins:
  - search
  - build_plantuml:
      render: "server"                             # "local" for local rendering
      bin_path: `/usr/local/bin/plantuml"          # ignored when render: server
      server: "http://www.plantuml.com/plantuml"   # offical plantuml server
      output_format: "svg"                         # or "png"
      diagram_root: "docs/diagrams"
      output_folder: "out"
      input_folder: "src"

```

This would result in this directory layout:

```
docs/                         # the default MkDocs docs directory
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

Afterwards, it checks if the `*.puml` (or other ending) file has a newer timestamp than the corresponding file in out. If so, it will generate a new image (works also with includes). This way, it won‘t take long until the site reloads.

It is recommended to use the `server` option, which is much faster than `local`.

## Known restrictions

- If you use `!include`s and the `render: "server"` option, this plugin merges those files manually. If there are any issues because of that, please open a ticket.
- Only files are currently supported for `!include` and `render: "server"`, no urls
