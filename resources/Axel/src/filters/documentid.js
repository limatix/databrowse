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
 * DocumentId stores its value into xtiger.session(doc) as "documentId"
 * When used in an invisible part of the template, this allows to generate a document identifier 
 * which can be used by some primitive plugin editors to communicate with a server (e.g. Photo upload)
 */
var _DocumentIdFilter = (function _DocumentIdFilter() {

	/////////////////////////////////////////////////
	/////    Static DocumentId Mixin Part     ///////
	///////////////////////////////////////////////// 

	// none

	return {

		///////////////////////////////////////////////////
		/////     Instance DocumentId Mixin Part    ////////
		///////////////////////////////////////////////////

		// Property remapping for chaining
		'->' : {
			'_setData' : '__DocumentIdSuperSetData'
		},

		/** Creates the entry for the identifier into the TOC using it's default text  
		 *  DOES forward call.
		 */
		_setData : function(aData) {
			this.__DocumentIdSuperSetData(aData);
			xtiger.session(this.getDocument()).save('documentId', aData);
		}
	
		/** add any other method from the filtered object that you want to override */
	
		/** add any other method you want to add to the filtered object to be called with can() / execute() */

	};

})();

//Register this filter as a filter of the 'text' plugin (i.e. text.js must have been loaded)
xtiger.editor.Plugin.prototype.pluginEditors['text'].registerFilter(
		'documentId', _DocumentIdFilter);