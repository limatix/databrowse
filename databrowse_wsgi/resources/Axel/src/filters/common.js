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
  * Class NoXMLFilter (filter mixin)
  * 
  * @class _NoXMLFilter
  */
var _NoXMLFilter = (function _NoXMLFilter() {
 	return {  

 		// No mapping
 		'->': {
		},   

 		load : function (point, dataSrc) {
			// do not load
 		},		

 		save : function (text) {
			// do not save
 		}
   }    	
 })();

// Do not forget to register your filter on any compatible primitive editor plugin
xtiger.editor.Plugin.prototype.pluginEditors['text'].registerFilter('noxml', _NoXMLFilter);   
xtiger.editor.Plugin.prototype.pluginEditors['select'].registerFilter('noxml', _NoXMLFilter);   

// TBD : 'hidden' filter (forces handle's style to display:'none') 



 