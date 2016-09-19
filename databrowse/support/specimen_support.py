#!/usr/bin/env python
###############################################################################
## Databrowse:  An Extensible Data Management Platform                       ##
## Copyright (C) 2012-2016 Iowa State University Research Foundation, Inc.   ##
## All rights reserved.                                                      ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##   1. Redistributions of source code must retain the above copyright       ##
##      notice, this list of conditions and the following disclaimer.        ##
##   2. Redistributions in binary form must reproduce the above copyright    ##
##      notice, this list of conditions and the following disclaimer in the  ##
##      documentation and/or other materials provided with the distribution. ##
##   3. Neither the name of the copyright holder nor the names of its        ##
##      contributors may be used to endorse or promote products derived from ##
##      this software without specific prior written permission.             ##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS       ##
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED ##
## TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A           ##
## PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER ##
## OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,  ##
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,       ##
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR        ##
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF    ##
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING      ## 
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS        ##
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              ##
##                                                                           ##
## This material is based on work supported by the Air Force Research        ##
## Laboratory under Contract #FA8650-10-D-5210, Task Order #023 and          ##
## performed at Iowa State University.                                       ##
##                                                                           ##
## DISTRIBUTION A.  Approved for public release:  distribution unlimited;    ##
## 19 Aug 2016; 88ABW-2016-4051.                                             ##
###############################################################################
""" support/specimen_support.py - Functions to Support Specimen Database """

import os
from lxml import etree

_specimendb = '/databrowse/specimens'
NS = {"specimen": "http://thermal.cnde.iastate.edu/specimen"}
NSSTR = "{http://thermal.cnde.iastate.edu/specimen}"
OUTPUT_STRING = 0
OUTPUT_ELEMENT = 1
OUTPUT_ETREE = 2
norecursion = []
attributekeys = { 
                  NSSTR + 'dimension': 'direction',
                  NSSTR + 'direction': 'name',
                  NSSTR + 'reference': 'face',
                  NSSTR + 'plane': 'face',
                  NSSTR + 'geometry': 'component',
                  NSSTR + 'physicalproperties': 'component',
                  NSSTR + 'flawparameters': 'index',
                  NSSTR + 'fiducialmark': 'name'
                }
mergechildren = [NSSTR + 'actionlog', NSSTR + 'identifiers', NSSTR + 'measurements', NSSTR + 'reldests']


class SpecimenException(Exception):
    """ Error Handling Class for Specimen Database """
    pass


def GetSpecimen(specimen, output=OUTPUT_STRING, specimendb=_specimendb):
    """ Fetch the XML Representation of a Specimen with Specimen Group Data Integrated """

    # Locate the Speicmen File
    filename = os.path.join(specimendb, specimen + '.sdb')
    if not os.path.exists(filename):
        raise SpecimenException('Unable to Locate Specimen Data File')
    elif not os.access(filename, os.R_OK):
        raise SpecimenException('Unable to Access Specimen Database')

    # Read the Specimen File
    try:
        f = open(filename, 'r')
        specimenxml = etree.XML(f.read())
        f.close()
    except:
        raise SpecimenException('Unable to Read Specimen Data File "%s"' % filename)

    # Identify the Group
    groupidelem = specimenxml.xpath("specimen:groups/specimen:groupid", namespaces=NS)
    if len(groupidelem) > 1:
        groups = {}
        # Open all of the group files and load them into a dictionary
        for group in [x.text for x in groupidelem]:
            filename = os.path.join(specimendb, group + '.sdg')
            if not os.path.exists(filename):
                pass
            elif not os.access(filename, os.R_OK):
                raise SpecimenException('Unable to Access Group File ' + filename)
            else:
                try:
                    f = open(filename, 'r')
                    groups[group] = etree.XML(f.read())
                    f.close()
                except:
                    raise SpecimenException('Unable to Read Specimen Group Data File' + filename)
            pass
        if len(groups) > 0:
            # Let's try combining all of them and seeing if the override attribute shows up anywhere
            groupnames = groups.keys()
            groupxml = groups[groupnames[0]]
            for groupname in groupnames[1:]:
                _combine_element(groupxml, groups[groupname], groupname)
            if len(groupxml.xpath("//@override", namespaces=NS)) > 0:
                print etree.tostring(groupxml, pretty_print=True)
                raise SpecimenException("Group File Conflict - Will Not Continue Until Conflict Is Resolved - Specimen " + specimen)

            # Combine Trees
            _combine_element(specimenxml, groupxml, groupnames[0])

        # Output
        if output == OUTPUT_STRING:
            print etree.tostring(specimenxml, pretty_print=True)
        elif output == OUTPUT_ELEMENT:
            return specimenxml
        elif output == OUTPUT_ETREE:
            return specimenxml.getroottree()
        else:
            raise SpecimenException('Invalid Return Type')
        pass
        
    elif len(groupidelem) == 1:
        groupid = groupidelem[0].text

        # Locate the Group File
        filename = os.path.join(specimendb, groupid + '.sdg')
        if not os.path.exists(filename):
            if output == OUTPUT_STRING:
                print etree.tostring(specimenxml, pretty_print=True)
            elif output == OUTPUT_ELEMENT:
                return specimenxml
            elif output == OUTPUT_ETREE:
                return specimenxml.getroottree()
            else:
                raise SpecimenException('Invalid Return Type')
        elif not os.access(filename, os.R_OK):
            raise SpecimenException('Unable to Access Specimen Database')

        # Read Specimen Group File
        try:
            f = open(filename, 'r')
            groupxml = etree.XML(f.read())
            f.close()
        except:
            raise SpecimenException('Unable to Read Specimen Group Data File')

        # Combine Trees
        _combine_element(specimenxml, groupxml, groupid)

        # Output
        if output == OUTPUT_STRING:
            print etree.tostring(specimenxml, pretty_print=True)
        elif output == OUTPUT_ELEMENT:
            return specimenxml
        elif output == OUTPUT_ETREE:
            return specimenxml.getroottree()
        else:
            raise SpecimenException('Invalid Return Type')
        pass

    elif len(groupidelem) == 0:
        if output == OUTPUT_STRING:
            print etree.tostring(specimenxml, pretty_print=True)
        elif output == OUTPUT_ELEMENT:
            return specimenxml
        elif output == OUTPUT_ETREE:
            return specimenxml.getroottree()
        else:
            raise SpecimenException('Invalid Return Type')
    else:
        raise SpecimenException('Error Selecting Group ID Tag from Specimen Data File')

    pass

def tagname(el):
    if el.tag in attributekeys:
        try:
            return el.tag + el.get(attributekeys[el.tag])
        except:
            raise SpecimenException('Required attribute "' + attributekeys[el.tag] + '" missing from element "' + el.tag + '"')
    else:
        return el.tag

def _combine_element(one, other, group):
    """ Private Function to Recursively Combine etree Elements, Preferencing the First Element """
    mapping = {}
    for el in one:
        mapping[tagname(el)] = el
    for el in [el for el in other if tagname(el) not in [NSSTR + 'notes', NSSTR + 'specimenslist', NSSTR + 'identifiertags', NSSTR + 'groups', NSSTR + 'groupid']]:
        if len(el) == 0 and tagname(el) not in norecursion and  tagname(el) not in mergechildren:
            # Not nested
            if not tagname(el) in mapping:
                # An element with this name is not in the mapping
                mapping[tagname(el)] = el
                # Add it
                if not el.get('fromgroup'):
                    el.set('fromgroup', group)
                one.append(el)
            else:
                mapping[tagname(el)].set('override', group)

        else:
            if tagname(el) in norecursion:
                if not tagname(el) in mapping:
                     # Not in the mapping
                    mapping[tagname(el)] = el
                    if not el.get('fromgroup'):
                        el.set('fromgroup', group)
                    # Just add it
                    one.append(el)
                else:
                    mapping[tagname(el)].set('override', group)
            elif tagname(el) in mergechildren:
                if not tagname(el) in mapping:
                    mapping[tagname(el)] = el
                    for child in el:
                        if not el.get('fromgroup'):
                            el.set('fromgroup', group)
                    one.append(el)
                else:
                    for child in el:
                        if not el.get('fromgroup'):
                            child.set('fromgroup', group)
                        mapping[tagname(el)].append(child)
            else:   
                try:
                    # Recursively process the element, and update it in the same way
                    _combine_element(mapping[tagname(el)], el, group)
                except KeyError:
                    # Not in the mapping
                    mapping[tagname(el)] = el
                    if not el.get('fromgroup'):
                        el.set('fromgroup', group)
                    # Just add it
                    one.append(el)
    pass
