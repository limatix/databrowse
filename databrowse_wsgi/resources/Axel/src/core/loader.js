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
 * Author(s) : Stephane Sire
 * 
 * ***** END LICENSE BLOCK ***** */
 
/*
 * Single global object used by XTiger Forms library. 
 */
if (typeof xtiger == "undefined" || !xtiger) {
	var xtiger = {};	
	xtiger.COMPONENT = 1; // XTiger node type constants
	xtiger.REPEAT = 2;
	xtiger.USE = 3;
	xtiger.BAG = 4;         
	xtiger.ATTRIBUTE = 5;	
	xtiger.SERVICE = 6;	// extension
	xtiger.UNKNOWN = -1;	
}

// the following modules will be filled by other library files
/** @namespace Contains parsing facilities to handle the XTiger XML language */
xtiger.parser = {};
/** @namespace Contains editors and plugins */
xtiger.editor = {};
/** @namespace Contains services */
xtiger.service = {};
/** @namespace Contains utilities to make the library cross-browser */
xtiger.cross = {};
/** @namespace Contains various utility methods */
xtiger.util = {};

/**
 * Single global object that contains DOM dependent methods which may also 
 * depend of the user agent.
 */
if (typeof xtdom == "undefined" || !xtdom) {
	xtdom = {};	
}

/**
 * Contains methods for managing the modules under the xtiger namespace.
 * It will evolve toward dynamical module loading.
 */
// xtiger.util.Loader = {};

/**
 * Associates a hash storage with a document. This is used to share objects for the life time
 * of a document, such as a keyboard manager, a tabgroup manager, etc.
 */

// a simpe Hash could be enough to manage sessions but maybe we will add methods in the future
xtiger.util.Session = function () {	
	this.store = {};
}

xtiger.util.Session.prototype = {	
	save : function (name, object) {
		this.store[name] = object;
	},
	load : function (name) {
		return this.store[name];
	}
}

// Lazily extends document object with a xtiger.util.Session object and/or returns it.
// @doc is the document to extend
// We use this method (document extension) because if the document is deleted by the user
// then it's session will also be deleted without the need to call a Session.delete() method
xtiger.session = function (doc) {
	if (! doc._xtigerSession) {
		doc._xtigerSession = new xtiger.util.Session ();
	}
	return doc._xtigerSession;
}

/**
 * Resource manager for managing access to UI resources (icons at that time)
 * It could evolve to also manage error messages and i18n
 */
xtiger.util.Resources = function () {	
	this.bundles = {}; // raw bundles (no paths)
	xtiger.bundles = {}; // "mount" point for exporting bundles to the editors
}

xtiger.util.Resources.prototype = {
	// Copies keys from the bundle name into xtiger.bundles namespace
	_mountBundle : function (name, baseurl) {
		var bsrc = this.bundles[name];
		var bdest = xtiger.bundles[name];
		for (var k in bsrc) {
			bdest[k] = baseurl + name + '/' + bsrc[k];
		}		
	},	
	// A bundle is just a hash where each key points to an icon file name
	// It is expected that there will be one bundle for each editor that need to display icons in the UI	
	addBundle : function (name, bundle) { 
		this.bundles[name] = bundle;
		xtiger.bundles[name] = {}; // makes the "mount" point
		for (var k in bundle) { // copy icon URLs 
			xtiger.bundles[name][k] = bundle[k]; // although it should be copied with setBase()
		}			
	},
	// Sets the base path for all the icon URLs in all the bundles
	setBase : function (baseUrl) {
		if (baseUrl.charAt(baseUrl.length -1) != '/') { // forces a trailing slash
			baseUrl = baseUrl + '/';
		}		
		for (var bkey in this.bundles) {
			this._mountBundle(bkey, baseUrl);
	 	}		
	}
}

// Resource manager instance (Singleton)
xtiger.resources = new xtiger.util.Resources ();
// bundles will be mounted under "xtiger.bundles"

/**
 * Central factory registry 
 * This allows to share some classes (essentially devices) between editors with decoupling
 */
xtiger.util.FactoryRegistry = function () {	
	this.store = {};
}

xtiger.util.FactoryRegistry.prototype = {	
	
	registerFactory : function (name, factory) {  
		if (this.store[name]) {
			alert("Error (AXEL) attempt to register an already registered factory : '" + name + "' !");
		} else {
			this.store[name] = factory;
		}
	},
	
	getFactoryFor : function (name) {
		if (! this.store[name]) {
			alert("Fatal Error (AXEL) unkown factory required : '" + name + "' \nYour editor will NOT be generated !");
			// FIXME: we could return a "dummy" factory that would return a "dummy" factory to getInstance
		} else {
			return this.store[name];
		}
	}
}

// Resource manager instance (Singleton)
xtiger.registry = new xtiger.util.FactoryRegistry ();
xtiger.factory = function (name) {	return xtiger.registry.getFactoryFor(name); } // simple alias

