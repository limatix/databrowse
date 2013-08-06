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
 * Manages tab navigation between basic string editors.
 */
xtiger.editor.TabGroupManager = function (rootNode) {
	this.root = rootNode;
	this.isChangingFocus = false;	  
	this.direction = 0;
}

xtiger.editor.TabGroupManager.prototype = {
	
	startEditingSession : function (editor) {
		if (this.isChangingFocus)	return; // guard
		this.tabs = [];		
		var treeWalker = xtiger.cross.makeTreeWalker (this.root, xtdom.NodeFilter.SHOW_ELEMENT,
				function (node) { 
						if (node.xttPrimitiveEditor && node.xttPrimitiveEditor.isFocusable()) {
							return xtdom.NodeFilter.FILTER_ACCEPT
						} else {
							return xtdom.NodeFilter.FILTER_SKIP; 
						}
				} );
		while(treeWalker.nextNode()) {
			// FIXME: how to avoid input nodes within unselected XttChoiceEditor control ?
			this.tabs.push(treeWalker.currentNode.xttPrimitiveEditor);		
		}		
		this.curEditor = editor;
	},

	stopEditingSession : function () {
		if (this.isChangingFocus)	return; // guard
		this.tabs = undefined;
		this.curEditor = undefined;
	},
	
	// Intercepts Tab KeyDown events
	// Returns true if it has intercepted it
	filterKeyDown : function (ev) {       
		this.direction = 0; // For firefox
		if (ev.keyCode == 9) { // it's a Tab
				if (xtiger.cross.UA.gecko)	{ // we must wait for KeyPress event because canceling will not work
					this.direction = ev.shiftKey ? -1 : 1;					
				} else { // we can act immediatly
					this._focusNextInput(ev.shiftKey ? -1 : 1);
				}               
				try {
					xtdom.preventDefault(ev);
					xtdom.stopPropagation(ev);
				} catch (e) {
  				// on IE !					
				}
				return true
		} else {
			return false;
		}
	},			
	
	// For some certain kinds of browsers filterKeyDown does not cancel the Tab event
	// in that case we get a chance to modify its effect in KeyPress event handling
	// This is the case with Firefox (v2 on OS X at least)
	filterKeyPress : function (ev) {
		if (xtiger.cross.UA.gecko && (this.direction != 0)) {
			// window.console.log('Focused next input');
			return (this._focusNextInput(this.direction));
		}
		return false;
	},	
	
	_focusNextInput : function (direction) {
		var res = false;
		if (!this.tabs)
			return; // safety guard
		for (var i = 0; i < this.tabs.length; i++) {
			if (this.tabs[i] == this.curEditor) {
				break;
			}
		}
		if (i < this.tabs.length) {
			var next;
			if ((i + direction) < 0) {
				next = this.tabs.length - 1;
			} else {
				next = (i + direction) % this.tabs.length;
			}
			this.isChangingFocus = true;  
			this.tabs[i].unfocus();       
			this.tabs[next].focus ();
			this.isChangingFocus = false;
			this.curEditor = this.tabs[next];
			res = true;
		}		     
		this.direction = 0;
		return res;
	}	
}	
