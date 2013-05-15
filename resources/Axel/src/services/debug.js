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

var _DebugService  = (function () {    

	return {      

		/**
		 * Remap property
		 */
		'->': {                             
			    // configuration method
				'configure': '__debugSuperConfigure', 
				// Producer notification methods  
				'notifyLoad': '__debugSuperNotifyLoad', 
				'notifyUpdate': '__debugSuperNotifyUpdate', 
				'askUpdate': '__debugSuperAskUpdate',
				'notifyRemove': '__debugSuperNotifyRemove',
				// Consumer callback method				
				'onBroadcast': '__debugSuperOnBroadcast'
			  },

		configure : function (aConfigurator, aResource, aData) {
			xtiger.cross.log('debug', 'configure[' + aResource + '] => ' + aData);
			this.__debugSuperConfigure(aConfigurator, aResource, aData);
		},      
		
		notifyLoad : function (aProducer, aResource, aData) {
			xtiger.cross.log('debug', 'notifyLoad[' + aResource + '] => ' + aData);
			this.__debugSuperNotifyLoad(aProducer, aResource, aData);
		},		

		notifyUpdate : function (aProducer, aResource, aData) {
			// var k = aProducer.getKey();
			xtiger.cross.log('debug', 'notifyUpdate[' + aResource + '] => ' + aData);
			this.__debugSuperNotifyUpdate(aProducer, aResource, aData);
		},

		askUpdate : function (aConsumer, aResource) {
			// var k = aProducer.getKey();
			xtiger.cross.log('debug', 'askUpdate[' + aResource + ']');
			this.__debugSuperAskUpdate(aConsumer, aResource);
		},

		notifyRemove : function (aProducer, aResource, aData) {   
			// var k = aProducer.getKey();
			xtiger.cross.log('debug', 'notifyRemove[' + aResource + '] => ' + aData);
			this.__debugSuperNotifyRemove(aProducer, aResource, aData);
		},
		
		onBroadcast : function (aConsumer, aResource, aData) {
			// var k = aProducer.getKey();
			xtiger.cross.log('debug', 'onBroadcast[' + aResource + '] => ' + aData);
			this.__debugSuperOnBroadcast(aConsumer, aResource, aData);
		}			
	}

})(); 

xtiger.factory('service').registerDelegate('debug', _DebugService);
