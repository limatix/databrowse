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

var _CopyService  = (function () {    

	return {      

		/**
		 * Remap property
		 */
		'->': {'onBroadcast': '__copySuperBroadcast'},

		onBroadcast : function (aModel, aResource, aData) {
			aModel.update(aData, true); // true to avoid reemitting update event
			this.__copySuperBroadcast(aModel, aResource, aData); // chains service
		}
	}

})(); 

xtiger.factory('service').registerDelegate('copy', _CopyService);

var _CopyCondService  = (function () {      
	    
	// Only copies aData to consumers subscribed to service with a resource key 
	// similar to "aResourceKey(floor)" or "aResourceKey(ceiling)" and if they meet the condition
	var _testAndCopy = function(aDelegate, aProducer, aResource, aDataAsNumber, aModel) {
		var cur;
		if (aModel == aProducer) {
			return; // no need to test the producer itself
		}
		if (aModel.checkServiceKey(aDelegate.getKey(), aResource + '(floor)')) {
			cur = parseInt(aModel.getData()); 
			if (isNaN(cur) || (aDataAsNumber < cur)) {
				aModel.update(aDataAsNumber.toString(), true); // true to avoid reemitting update event
			}
		} else if (aModel.checkServiceKey(aDelegate.getKey(), aResource + '(ceiling)')) { 
			cur = parseInt(aModel.getData()); 
			if(isNaN(cur) || (aDataAsNumber > cur)) {
				aModel.update(aDataAsNumber.toString(), true); // true to avoid reemitting update event
			}
		} // ignores other keys
	}

	return {      

		/**
		 * Remap property
		 */
		'->': {},
		
		notifyUpdate : function (aProducer, aResource, aData) {         
			var newVal = parseInt(aData);
			if (! isNaN(newVal)) {
				this._apply(aProducer, aResource, newVal, this.getHandle(), _testAndCopy);
			}
		}
	}

})(); 

xtiger.factory('service').registerDelegate('copycond', _CopyCondService);