"""
Databrowse:  An Extensible Data Management Platform
Copyright (C) 2012-2016 Iowa State University Research Foundation, Inc.

This package contains support modules used by the Databrowse library and its
plugins.  There are also several configuration files contained inside of this
package that are used by Databrowse internally.

The following modules/classes are contained here:

  EXIF              - Module used to extract raw EXIF tag data from images
  RMETA             - Module containing functionality to extract specialized
                      meta tags contained within EXIF data saved by a RICOH
                      G700 SE digital camera; meta tags contain barcodes with
                      XML data that must be extracted
  debug_support     - Class that enables PDB to be wrapped around other fcns
  dummy_web_support - Modified version of web_support class for the Databrowse
                      library; to be eventually merged back into web_support
  handler_support   - Class containing necessary functionality to process all
                      plugins "handlers.py" files and to subsequently determine
                      which plugins are able to handle which files
  images2gif        - Module used to convert a series of PIL images into an
                      animated GIF - useful to avoid system calls to external
                      systems to render videos
  renderer_support  - Base class for all Databrowse plugins; contains support
                      functionality needed by all and allows plugins to only
                      contain the absolutely necessary code
  specimen_support  - Support functionality used by Specimen Database plugins
                      to generate combined XML representations of Specimen and
                      Specimen Group Files
  web_support       - Class contianing core support functionality needed for
                      plugins to be aware of the environment and to handle 
                      inputs from the web server; also contains code for
                      building menus and other support structures for the web
  xslt_support      - DEPRECATED! Contains wrapper functions around the Amara
                      XML library - still used by some external functionality,
                      but this will be removed by Ver 1.0.0

The following configuration files are contained here:
  
  directoryplugins.conf - Contains a listing of plugins that are designated for 
                          handling directories and the icons that should be
                          associated with those types of directories
  hiddenfiles.conf      - A glob-style list of files that should be hidden from
                          view in directory listings produced by Databrowse;
                          also contains a shown section to explicitly override
                          the display of certain files that would othrewise be
                          hidden from view
  iconmap.conf          - A mapping between content-types/extensions to the
                          icon used to represent different types of files;  if
                          the mapping is not specified here, the default icon
                          will be used

To import modules from this package, we suggest the following code:

>>> from databrowse.support import specimen_support as ss
>>> from databrowse.support.debug_support import Debugger
"""