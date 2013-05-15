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

/**
 * This file contains some utility functions to debug AXEL applications
 * These functions are located within the xtiger.debug namespace
 * This file should not be built with the other files when deploying AXEL applications, it's for debug only
 */
xtiger.debug = {};

/**
 * Loads the XHTML document at URL
 * Experimental version that uses XMLHTTPRequest object on all browser except IE
 * On IE (IE8, IE7 ?, untested on IE6) it uses the MSXML2.DOMDocument ActiveX for parsing XML documents into an IXMLDOMElement
 * as a benefit it can open templates / XML documents from the local file system on IE
 *
 * Accepts an optional logger (xtiger.util.Logger) object to report errors
 * Returns the document (should be a DOM Document object) or false in case of error
 */
xtiger.debug.loadDocument = function (url, logger) {
	if (window.navigator.appName == "Microsoft Internet Explorer") { // will try with MSXML2.DOMDocument
		var errMsg;		
		try {
			var xtDoc = new ActiveXObject("MSXML2.DOMDocument.6.0");  
			xtDoc.async = false;
			xtDoc.resolveExternals = false;
			xtDoc.validateOnParse = false; 
			xtDoc.setProperty("ProhibitDTD", false); // true seems to reject files with a DOCTYPE declaration
			xtDoc.load(url);
			if (xtDoc.parseError.errorCode != 0) {
			    errMsg = xtDoc.parseError + ' ' + xtDoc.parseError.reason;
			} else {
				return xtDoc; // OK, returns the IXMLDOMElement DOM element 
			}
		} catch (e) {
			errMsg = e.name;
		}
		if (errMsg) {
			if (logger) {
				logger.logError('Error while loading $$$ : ' + errMsg, url);
			} else {
				alert("ERROR:" + errMsg);					
			}
		    xtDoc = null;
		}		
	} else {
		return xtiger.cross.loadDocument(url, logger);
	}
	return false;	
}

