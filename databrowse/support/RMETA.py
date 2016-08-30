#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  RMETA.py, S. Holland, 3/15/2013
#  Based on EXIF.py, information below

#
#
# Library to extract Exif information from digital camera image files.
# https://github.com/ianare/exif-py
#
#
# VERSION 1.2.0
#
# To use this library call with:
#    f = open(path_name, 'rb')
#    tags = EXIF.process_file(f)
#
# To ignore MakerNote tags, pass the -q or --quick
# command line arguments, or as
#    tags = EXIF.process_file(f, details=False)
#
# To stop processing after a certain tag is retrieved,
# pass the -t TAG or --stop-tag TAG argument, or as
#    tags = EXIF.process_file(f, stop_tag='TAG')
#
# where TAG is a valid tag name, ex 'DateTimeOriginal'
#
# These two are useful when you are retrieving a large list of images
#
# To return an error on invalid tags,
# pass the -s or --strict argument, or as
#    tags = EXIF.process_file(f, strict=True)
#
# Otherwise these tags will be ignored
#
# Returned tags will be a dictionary mapping names of Exif tags to their
# values in the file named by path_name.  You can process the tags
# as you wish.  In particular, you can iterate through all the tags with:
#     for tag in tags.keys():
#         if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename',
#                        'EXIF MakerNote'):
#             print "Key: %s, value %s" % (tag, tags[tag])
# (This code uses the if statement to avoid printing out a few of the
# tags that tend to be long or boring.)
#
# The tags dictionary will include keys for all of the usual Exif
# tags, and will also include keys for Makernotes used by some
# cameras, for which we have a good specification.
#
# Note that the dictionary keys are the IFD name followed by the
# tag name. For example:
# 'EXIF DateTimeOriginal', 'Image Orientation', 'MakerNote FocusMode'
#
# Copyright (c) 2002-2007 Gene Cash
# Copyright (c) 2007-2013 Ianaré Sévi and contributors
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
#  3. Neither the name of the authors nor the names of its contributors
#     may be used to endorse or promote products derived from this
#     software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
# ----- See 'changes.txt' file for all contributors and changes ----- #
#

# Moved imports here so they are available when ran as module - tylerl
import sys
import getopt
import string

# process an image file (expects an open file object)
# this is the function that has to deal with all the arbitrary nasty bits
# of the EXIF standard
def process_file(f, stop_tag='UNDEF', details=True, strict=False, debug=False):
    # yah it's cheesy...
    global detailed
    detailed = details

    RMETA_2D_Barcodes={}  # indexed by (presumably) memo number

    # by default do not fake an EXIF beginning
    fake_exif = 0

    # determine whether it's a JPEG or TIFF
    data = f.read(12)
    if data[0:4] in ['II*\x00', 'MM\x00*']:
        # it's a TIFF file
        f.seek(0)
        endian = f.read(1)
        f.read(1)
        offset = 0
    elif data[0:2] == '\xFF\xD8':
        # it's a JPEG file
        if debug: print("JPEG format recognized data[0:2] == '0xFFD8'.")
        base = 2
        while data[2] == '\xFF' and data[6:10] in ('JFIF', 'JFXX', 'OLYM', 'Phot'):
            if debug: print("data[2] == 0xxFF data[3]==%x and data[6:10] = %s"%(ord(data[3]),data[6:10]))
            length = ord(data[4])*256+ord(data[5])
            if debug: print("Length offset is",length)
            f.read(length-8)
            # fake an EXIF beginning of file
            # I don't think this is used. --gd
            data = '\xFF\x00'+f.read(10)
            fake_exif = 1
            if base>2: 
                if debug: print("added to base ")
                base = base + length + 4 -2
            else: 
                if debug: print("added to zero ")
                base = length + 4
            if debug: print("Set segment base to",base)

        # Big ugly patch to deal with APP2 (or other) data coming before APP1
        f.seek(0)
        data = f.read(base+400000) # in theory, this could be insufficient since 64K is the maximum size--gd
        # base = 2
        while 1:
            if debug: print("Segment base 0x%X" % base)
            if data[base:base+2]=='\xFF\xE1':
                # APP1
                if debug: print("APP1 at base",hex(base))
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if data[base+4:base+8] == "Exif":
                    if debug: print("Decrement base by",2,"to get to pre-segment header (for compatibility with later code)")
                    #base = base-2
                    #break
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
            elif data[base:base+2]=='\xFF\xE0':
                # APP0
                if debug: print("APP0 at base",hex(base))
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
            elif data[base:base+2]=='\xFF\xE2':
                # APP2
                if debug: print("APP2 at base",hex(base))
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
            elif data[base:base+2]=='\xFF\xEE':
                # APP14
                if debug: print("APP14 Adobe segment at base",hex(base))
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                print("There is useful EXIF-like data here, but we have no parser for it.")
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
            elif data[base:base+2]=='\xFF\xDB':
                if debug: print("JPEG image data at base",hex(base),"No more segments are expected.")
                # sys.exit(0)
                break
            elif data[base:base+2]=='\xFF\xD8':
                # APP12
                if debug: print("FFD8 segment at base",hex(base))
                if debug: print("Got",hex(ord(data[base])), hex(ord(data[base+1])),"and", data[4+base:10+base], "instead.")
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
            elif data[base:base+2]=='\xFF\xEC':
                # APP12
                if debug: print("APP12 XMP (Ducky) or Pictureinfo segment at base",hex(base))
                if debug: print("Got",hex(ord(data[base])), hex(ord(data[base+1])),"and", data[4+base:10+base], "instead.")
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                print("There is useful EXIF-like data here (quality, comment, copyright), but we have no parser for it.")
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
                pass
            elif data[base:base+2]=='\xFF\xE5': # APP5
                app5totallen=ord(data[base+2])*256+ord(data[base+3])
                if debug: print("APP5 segment found. Length=%d" % (app5totallen))
                if data[(base+4):(base+13)]=="RMETA\0MM\x01":
                    rmetatotallen=ord(data[base+2])*256+ord(data[base+3])
                    if debug: print("RMETA segment found. Length=%d" % (rmetatotallen))
                    assert(rmetatotallen==app5totallen)  # sizes should match...
                    
                    if data[base+15]=="\x00": 
                        if debug: print("RMETA Format 0")
                        rmetabase=base+18
                        
                        pass
                    elif data[base+15]=="\x01":
                        if debug: print("RMETA Format 1")
                        rmetabase=base+20
                        pass
                    pos=0
                    while (rmetabase-base) < rmetatotallen-2:
                        
                        rmetatype=ord(data[rmetabase])*256 + ord(data[rmetabase+1])
                        rmetalength=ord(data[rmetabase+2])*256 + ord(data[rmetabase+3])
                        if debug: print("RMETA Type %x %x %d, length=%x %x %d" % (ord(data[rmetabase]),ord(data[rmetabase+1]),rmetatype,ord(data[rmetabase+2]),ord(data[rmetabase+3]),rmetalength))

                        if rmetatype==0 and rmetalength > 0:
                            rmetadatastring=data[(rmetabase+4):(rmetabase+rmetalength-2)]
                            #if debug: print("rmetadatastring=%s" % (rmetadatastring))
                            if rmetadatastring[:15]=="BARCODE_2D_DATA":
                                
                                memonum=int(rmetadatastring[16:18])
                                
                                # figure out how many digits there are in the length
                                lendigits=string.find(rmetadatastring,",",19)-19
                                # print lendigits
                                barcodelen=int(rmetadatastring[19:(19+lendigits)])
                                barcode=rmetadatastring[(19+lendigits+1):(19+lendigits+1+barcodelen)]
                                
                                if debug: print "Got 2D barcode:", barcode
                                RMETA_2D_Barcodes[memonum]=barcode.decode('utf-8')
                                
                                pass
                            else :
                                print "Unknown RMETA type 0 segment"
                            
                            pass

                        if pos==0:
                            rmetabase+=rmetalength+7
                            pass
                        else : # pos==1:
                            rmetabase+=rmetalength+2
                            pass
                        if debug: print pos, rmetabase-base, ord(data[base+2])*256+ord(data[base+3])

                        pos+=1
                        pass
                    #type=data[

                    pass
                
                
                
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
                pass
            else: 
                try:
                    if debug: print("Unexpected/unhandled segment type or file content.")
                    if debug: print base, len(data)
                    if debug: print("Got",hex(ord(data[base])), hex(ord(data[base+1])),"and", data[4+base:10+base], "instead.")
                    if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                except: 
                    raise
                try: base=base+ord(data[base+2])*256+ord(data[base+3])+2
                except: return {}
        f.seek(base+12)
        if data[2+base] == '\xFF' and data[6+base:10+base] == 'Exif':
            # detected EXIF header
            offset = f.tell()
            endian = f.read(1)
            #HACK TEST:  endian = 'M'
        elif data[2+base] == '\xFF' and data[6+base:10+base+1] == 'Ducky':
            # detected Ducky header.
            if debug: print("EXIF-like header (normally 0xFF and code):",hex(ord(data[2+base])) , "and", data[6+base:10+base+1])
            offset = f.tell()
            endian = f.read(1)
        elif data[2+base] == '\xFF' and data[6+base:10+base+1] == 'Adobe':
            # detected APP14 (Adobe)
            if debug: print("EXIF-like header (normally 0xFF and code):",hex(ord(data[2+base])) , "and", data[6+base:10+base+1])
            offset = f.tell()
            endian = f.read(1)
        else:
            # no EXIF information
            if debug: print("No EXIF header expected data[2+base]==0xFF and data[6+base:10+base]===Exif (or Duck)")
            if debug: print(" but got",hex(ord(data[2+base])) , "and", data[6+base:10+base+1])
            return RMETA_2D_Barcodes
    else:
        # file format not recognized
        if debug: print("file format not recognized")
        return {}

    return RMETA_2D_Barcodes


# show command line usage
def usage(exit_status):
    msg = 'Usage: EXIF.py [OPTIONS] file1 [file2 ...]\n'
    msg += 'Extract EXIF information from digital camera image files.\n\nOptions:\n'
    msg += '-q --quick   Do not process MakerNotes.\n'
    msg += '-t TAG --stop-tag TAG   Stop processing when this tag is retrieved.\n'
    msg += '-s --strict   Run in strict mode (stop on errors).\n'
    msg += '-d --debug   Run in debug mode (display extra info).\n'
    print(msg)
    sys.exit(exit_status)

# library test/debug function (dump given files)
if __name__ == '__main__':

    # parse command line options/arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hqsdt:v", ["help", "quick", "strict", "debug", "stop-tag="])
    except getopt.GetoptError:
        usage(2)
    if args == []:
        usage(2)
    detailed = True
    stop_tag = 'UNDEF'
    debug = False
    strict = False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage(0)
        if o in ("-q", "--quick"):
            detailed = False
        if o in ("-t", "--stop-tag"):
            stop_tag = a
        if o in ("-s", "--strict"):
            strict = True
        if o in ("-d", "--debug"):
            debug = True

    # output info for each file
    for filename in args:
        try:
            file=open(str(filename), 'rb')
        except:
            print("'%s' is unreadable\n"%filename)
            continue
        print(filename + ':')
        # get the tags
        data = process_file(file, stop_tag=stop_tag, details=detailed, strict=strict, debug=debug)
        if not data or len(data.keys())==0: 
            print('No RDATA barcodes found')
            continue

        x=data.keys()
        x.sort()
        for i in x:
            print "Barcode %d: %s" % (i,data[i])
