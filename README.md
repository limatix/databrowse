# Databrowse #
Databrowse:  An Extensible Data Management Platform     
Copyright (C) 2012-2016 Iowa State University Research Foundation, Inc. 

## Documentation ##
Please see the documentation in [doc/Manual/Manual.pdf](https://github.com/limatix/databrowse/blob/master/doc/Manual/Manual.pdf) for more 
information and installation instructions.

## License ##
Databrowse is released under the BSD 3-Clause License.  Please see the file
[COPYING](https://github.com/limatix/databrowse/blob/master/COPYING) for more information.

## Acknowledgments ##
This material is based on work supported by the Air Force Research Laboratory
under Contract #FA8650-10-D-5210, Task Order #023 and performed at Iowa State 
University.

DISTRIBUTION A.  Approved for public release:  distribution unlimited; 19 Aug 
2016; 88ABW-2016-4051.

This material is based on work supported by NASA under Contract
NNX16CL31C and performed by Iowa State University as a subcontractor
to TRI Austin.

Approved for public release by TRI Austin: distribution unlimited;
01 June 2018; by Carl W. Magnuson (NDE Division Director).

## CEFDatabrowse Install Instructions ##
Dependencies are platform specific and can be found in [requirements](https://github.com/limatix/databrowse/blob/master/requirements).

From PIP:<br>
    `> pip install databrowse`<br>
From source:<br>
    `> cd databrowse_source_dir`<br>
    `> python setup.py install`<br>


```
Usage: databrowse [-h] [-s path] [-e] [-g [path]]

    Databrowse: An Extensible Data Management Platform

    optional arguments:
      -h, --help                    show this help message and exit
      -s path, --setdataroot path   path to set new dataroot
      -e, --openconfig              open cefdatabrowse config file
      -g [path], --go [path]        open cefdatabrowse in a directory
```
## Changelog ##

### v0.8 ###
 * Approval for Public release following work with TRI Austin
 * CEFDatabrowse, a server-less client, Implemented
 * SDT File Viewer Plugin Implemented
 * Magic bug fixes
 * Various other bug fixes

### v0.7 ###
 * Approval for Public Release
 * Packaging Cleanup
 * License Change to BSD-3

### v0.6 ###
 * Databrowse Library Implemented
 * Restructuring of Files for Packaging Completed
 * Starting of Documentation
 * Restructuring of Directory Plugin Output
 * Complete Reworking of Speicmen Database Plugins
 * Numerous Updates to Dataguzzler and DatacollectV2 Plugins
 * All Use of etree.register_namespace Global Removed and Basic Namespace
   Handling Implemented
 * Numerous Bugfixes

### v0.5 ###

 * Directory Restructuring For Distribution
 * Style Updates for Several Plugins
 * Tabular Views in DatacollectV2 Plugin
 * Minor Bugfixes

### v0.4 ###
 
 * Major Updates to DatacollectV2, Checklist, Specimen/Xducer, and Dataguzzler
 * Numerous Bugfixes
 * Branch Merges

### v0.3 ###

 * Plugins Restructures into Python Modules
 * Numerous Plugin Updates and Bugfixes
 * Menus and Location Bars Added
 * Numerous Style Updates

### v0.2 ###

 * Numerous Plugin Updates
 * New Stylesheet using latest version of ISU Template

### v0.1 ###

 * Initial Commit of Baseline Plugins and Basic Infrastructure



