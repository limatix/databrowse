/* ***** BEGIN LICENSE BLOCK *****
 *
 * Copyright (C) 2009, 2010, 2011  Stéphane Sire
 *
 * This file is part of the Adaptable XML Editing Library (AXEL), version 1.1.2-beta 
 *
 * Adaptable XML Editing Library (AXEL) is free software ; you can redistribute it 
 * and/or modify it under the terms of the GNU Lesser General Public License (the "LGPL")
 * as published by the Free Software Foundation ; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * The library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY ; 
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
 * PURPOSE. See the GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with this library ; 
 * if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, 
 * Boston, MA 02111-1307 USA.
 *
 * Web site : http://media.epfl.ch/Templates/
 * 
 * Author(s) : Stephane Sire, Antoine Yersin
 * 
 * ***** END LICENSE BLOCK ***** */  
 
xtiger.util.filterable = function (name, that) {
  
  if (! that) { // safe guard
    xtiger.cross.log('error', 'filter "' + name + '" is undefined');
    return that;
  }
  
  /* A registry to store filters */
	var _filtersRegistry = {};       
	
  /* A plugin name for log messages */
	var _pluginName = name;      
	
	/**
	 * <p>
	 * Registers a filter under the given key. The filter must implement the
	 * delegation pattern documented in Alex Russell's blog at
	 * http://alex.dojotoolkit.org/2008/10/delegate-delegate-delegate/.
	 * </p>
	 * 
	 * @param {string}
	 *            aKey A string key under which to register the filter
	 * @param {object}
	 *            aFilter A filtering object implementing the aforesaid
	 *            delegation pattern
	 */
	that.registerFilter = function registerFilter (aKey, aFilter) {
		if (! typeof(aFilter) == "object") // NOTE may test harder?
			return;
		if (_filtersRegistry[aKey])
			xtiger.cross.log('warning', '"' + _pluginName + '" plugin: filter "' + aKey + '" is already registred. Overwriting it.');
		_filtersRegistry[aKey] = aFilter;
	};     
	
	/**
	 * <p>
	 * Same as registerFilter but for a service delegate. It may evolve differently
	 * in the future (e.g. to print a different error message, to support service specific 
	 * parameters or to allow name collision between service delegates and plugin filters).
	 * </p>
	 */
	that.registerDelegate = that.registerFilter;
  
  /**
  * <p>
  * Apply all filters for the given model. The filtering implements a
  * DOJO-like delegation pattern, thanks to the explanation of Mr. Alex
  * Russell on his blog, at
  * http://alex.dojotoolkit.org/2008/10/delegate-delegate-delegate/. 
  * See filter's code for further explanations.
  * </p>
  * 
  * @param {_LinkModel}
  *            aModel The model to filter
  * @param {string}
  *            aFiltersParam The string of the "filters=" parameter
  * @return {_LinkModel} A filtered instance
  */
  that.applyFilters = function applyFilters (aModel, aFiltersParam) {

  	// the "_baseobject" condition avoid copying properties in "props"
  	// inherited from Object.prototype.  For example, if obj has a custom
  	// toString() method, don't overwrite it with the toString() method
  	// that props inherited from Object.protoype
  	var _baseobject = {};

  	var _filtersnames = aFiltersParam.split(' '); // filters are given as a space-separated name list

  	var _filtered = aModel;

  	// Apply filters
  	for (var _i = 0; _i < _filtersnames.length; _i++) {
  		var _unfiltered = _filtered;
  		var _filter = _filtersRegistry[_filtersnames[_i]]; // fetch the filter
  		if (!_filter) {
  		  xtiger.cross.log('warning', '"' + _pluginName + '" plugin: missing filter "' + _filtersnames[_i] + '"');
  			continue;    
  		}
  		var _Filtered = function () {}; // New anon class
  		_Filtered.prototype = _unfiltered; // Chain the prototype
  		_filtered = new _Filtered();
  		if (_filter) {
             var _remaps = _filter["->"];
             if (_remaps) {
                 //delete _filter["->"]; // TODO avoid for further uses?
                 for (var _p in _remaps) {
                     if (_baseobject[_p] === undefined || _baseobject[_p] != _remaps[_p]) {
                         if (_remaps[_p] == null) {
                             // support hiding via null assignment
                             _filtered[_p] = null;
                         }
                         else {
                             // alias the local version away 
                             // alias to no-op function if it doesn't exist
                             _filtered[_remaps[_p]] = _unfiltered[_p] || function () { };
                         }
                     }
                 }
             }
             xtiger.util.mixin(_filtered, _filter);
         }
  	}
  	return _filtered;
  };
   
  return that;
};   