"""
Databrowse:  An Extensible Data Management Platform
Copyright (C) 2012-2016 Iowa State University Research Foundation, Inc.

This meta package contains all packages declared in the databrowse.plugins
namespace.  Not all of these plugins may actually be physically contained in
the main Databrowse distribution.  Please refer to the documentation contained
inside each plugin for more details about that plugin.

To import modules from this package, we suggest the following code:

>>> from databrowse.plugins.db_default import db_default

The plugin name is a critical component in building new plugins for Databrowse.
After determining the name for your plugin (must be a valid Python class name),
it is critical that this name is used consistently throughout the plugin.
Components of Databrowse depend on this naming structure to function properly.

The following componets are required to make up a complete plugin package:

  __init__.py            - File to indicate that this is a package and to 
                           contain base package documentation
  db_pluginname.py       - File name matching the plugin name, prefixed with
                           db_ containing the db_pluginname class.  This class
                           should be inherited from renderer_support.  See the
                           documentation for more information.
  dbs_stylesheetname.xml - Any number of optional XSLT stylesheet files that
                           can be applied to transform the XML output from the
                           plugin into HTML for the web.  Multiple files
                           matching this naming structure will result in a menu
                           item being generated for each stylesheet found.
  handlers.py            - A file containing a function with a name prefixed by
                           dbh_ that will be called in alphabetical order with
                           all other handler functions pulled in from other
                           plugins to determine whether a plugin can/should be
                           called to handle a particular file.  The last plugin
                           to be called will be the default plugin used for the
                           file.  This should return the name of the plugin to
                           be used, otherwise it should return False.

See the documentation for more details on building plugins.
"""