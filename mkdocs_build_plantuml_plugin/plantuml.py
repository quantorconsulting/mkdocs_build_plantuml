import os
import time
import base64
import zlib
import string
import six
import httplib2

from mkdocs import utils as mkdocs_utils
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin
from subprocess import call
import mkdocs.structure.files

if six.PY2:
    from string import maketrans
else:
    maketrans = bytes.maketrans
    

plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
base64_alphabet   = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
b64_to_plantuml = maketrans(base64_alphabet.encode('utf-8'), plantuml_alphabet.encode('utf-8'))

class BuildPlantumlPlugin(BasePlugin):

  config_scheme = (
        ('render', mkdocs.config.config_options.Type(str, default="server")),
        ('server', mkdocs.config.config_options.Type(str, default="http://www.plantuml.com/plantuml")),
        ('bin_path', mkdocs.config.config_options.Type(str, default="/usr/local/bin/plantuml")),
        ('output_format', mkdocs.config.config_options.Type(str, default="png")),
        ('diagram_root', mkdocs.config.config_options.Type(str, default="docs/diagrams")),
        ('output_folder', mkdocs.config.config_options.Type(str, default="out")),
        ('input_folder', mkdocs.config.config_options.Type(str, default="src")),
        ('theme_enabled', mkdocs.config.config_options.Type(bool, default=False)),
        ('theme_folder', mkdocs.config.config_options.Type(str, default="include/themes/")),
        ('theme_light', mkdocs.config.config_options.Type(str, default="light.puml")),
        ('theme_dark', mkdocs.config.config_options.Type(str, default="dark.puml")),
    )

  def __init__(self):
    self.total_time = 0

  def on_pre_build(self, config):

    root_input = os.path.join(os.getcwd(), self.config['diagram_root'], self.config['input_folder'])

    # Run throgh input folder
    for subdir, dirs, files in os.walk(root_input):
      for file in files:
        diagram = PuElement(file,subdir)
        diagram.out_dir = os.path.join(os.getcwd(), self.config['diagram_root'], self.config['output_folder'],*subdir.replace(root_input,"").split(os.sep))

        # Handle to read source file
        with open(os.path.join(diagram.directory, diagram.file), "r") as f:
          diagram.src_file = f.readlines()
         
        # Search for start (@startuml <filename>)
        if not self._searchStartTag(diagram):
          # check the outfile (.ext will be set to .png or .svg etc)
          self._build_out_filename(diagram)
        
        # Checks mtimes for target and include files to know if we update
        self._build_mtimes(diagram)

        # Go through the file (only relevant for server rendering)
        self._readFile(diagram, False)

        # Finally convert
        self._convert(diagram)

        # Second time (if dark mode is enabled)
        if (self.config["theme_enabled"]):
          # Go through the file a second time for themed option
          self._readFile(diagram, True)

          # Finally convert
          self._convert(diagram, True) 

    return config

  # Search for a optional filename after the start tag
  def _searchStartTag(self, diagram):
    for line in diagram.src_file:
      line = line.rstrip()
      if line.strip().startswith("@startuml"):
        ws = line.find(" ")
        if ws > 0:
          # we look for <filename> which starts after a whitespace
          out_filename = line[ws+1:]
          diagram.out_file = os.path.join(diagram.out_dir, out_filename+"."+self.config["output_format"])
          if (self.config["theme_enabled"]):
            diagram.out_file_dark = os.path.join(diagram.out_dir, out_filename+"_dark."+self.config["output_format"]) 
          return True

  def _build_mtimes(self, diagram):
    # Compare the file mtimes between src and target
    try:
      diagram.img_time = os.path.getmtime(diagram.out_file)
    except:
      diagram.img_time = 0

    if(self.config["theme_enabled"]):
      try:
        diagram.img_time_dark = os.path.getmtime(diagram.out_file_dark)
      except:
        diagram.img_time_dark = 0 

    diagram.src_time = os.path.getmtime(os.path.join(diagram.directory, diagram.file))

    # Include time
    diagram.inc_time = 0
    

  def _readFile(self, diagram, dark_mode):
    temp_file = self._readFileRec(diagram.src_file, "", diagram, diagram.directory, dark_mode)
    try:
      zlibbed_str = zlib.compress( temp_file.encode('utf-8') )
      compressed_string = zlibbed_str[2:-4]
      diagram.b64encoded = base64.b64encode(compressed_string).translate(b64_to_plantuml).decode('utf-8')
    except:
      diagram.b64encoded = ""


  # Reads the file recursively 
  def _readFileRec(self, lines, temp_file, diagram, directory, dark_mode):

    for line in lines:
      if line.startswith("!include"):
        temp_file = self._readInclLine(diagram, line, temp_file, directory, dark_mode)
      else:
        temp_file += line
        if "\n" not in line:
          temp_file += "\n"

    return temp_file

  def _readInclLine(self, diagram, line, temp_file, directory, dark_mode):
    # If includeurl is found, we do not have to do anything here. Server 
    # can handle that
    if "!includeurl" in line:
      temp_file += line
      return temp_file
    
    # on the nineth position starts the filename
    inc_file = line[9:].rstrip()

    if (dark_mode):
      inc_file = inc_file.replace(self.config["theme_light"], self.config["theme_dark"])

    # According to plantuml, simple !include can also have urls, ignore that and continue
    if inc_file.startswith("http"):
      temp_file += line
      return temp_file
    else:
      # Otherwise we have to read the include file as well
      inc_file = os.path.normpath(os.path.join(directory,inc_file))

    # Save the mtime of the inc file to compare
    try:
      local_inc_time = os.path.getmtime(inc_file)
    except:
      local_inc_time = 0

    if local_inc_time > diagram.inc_time:
      diagram.inc_time = local_inc_time

    # Read contents of the included file
    try:
      with open(inc_file, "r") as inc:
        temp_file = self._readFileRec(inc, temp_file, diagram, os.path.dirname(os.path.realpath(inc_file)), dark_mode)
    except Exception as e:
      print("Could not open " + str(e))

    return temp_file


  def _build_out_filename(self, diagram):
    out_index = diagram.file.rfind(".")
    if (out_index > -1):
      diagram.out_file = diagram.file[:out_index+1] + self.config["output_format"]
      if (self.config["theme_enabled"]):
        diagram.out_file_dark = diagram.file[:out_index] + "_dark." + self.config["output_format"]

    diagram.out_file = os.path.join(diagram.out_dir,diagram.out_file)
    if (self.config["theme_enabled"]):
      diagram.out_file_dark = os.path.join(diagram.out_dir,diagram.out_file_dark)

    return diagram


  def _convert(self, diagram, dark_mode=False):

    if not dark_mode:
      if (diagram.img_time < diagram.src_time) or (diagram.inc_time > diagram.img_time):
        
        print("Converting " + os.path.join(diagram.directory, diagram.file))
        if self.config['render'] == 'local':
            command = self.config["bin_path"].rsplit()
            call([*command,"-t"+self.config["output_format"],os.path.join(diagram.directory, diagram.file),"-o",diagram.out_dir])
        else:
          self._call_server(diagram,diagram.out_file)

    # If Dark mode AND edit time of includes higher than image AND server render
    elif dark_mode and ((diagram.img_time_dark < diagram.src_time) or (diagram.inc_time > diagram.img_time_dark)) and self.config['render'] == 'server':
          self._call_server(diagram,diagram.out_file_dark)
        


  def _call_server(self,diagram,out_file):
    http = httplib2.Http({})
    url = self.config['server']+"/"+self.config['output_format']+"/"+diagram.b64encoded
    print(url)

    try:
      response, content = http.request(url)
      if response.status != 200:
        print("Wrong response status for " +diagram.file+": " + response.status)
    except:
      print("Server error while processing "+diagram.file)
    else:
      if not os.path.exists(os.path.join(diagram.out_dir)):
        os.makedirs(os.path.join(diagram.out_dir))
      
      out = open(os.path.join(diagram.out_dir, out_file), 'bw+')
      out.write(content)
      out.close()
    

class PuElement:
  def __init__(self, file, subdir):
    self.file = file
    self.directory = subdir
    self.out_dir = ""
    self.img_time = 0
    self.img_time_dark = 0
    self.inc_time = 0
    self.src_time = 0
    self.out_file = ""
    self.out_file_dark = ""
    self.b64encoded = ""