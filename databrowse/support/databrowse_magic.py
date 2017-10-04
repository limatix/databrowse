def file_type(filepath):
    mime = "Mime not found"
    siglist_4bit = [['25', '50', '44', '46'],
                    ['47', '49', '46', '38'],
                    ['49', '49', '2A', '00'],
                    ['4D', '4D', '00', '2A'],
                    ['FF', 'D8', 'FF', 'D8'],
                    ['50' '4B' '03' '04'],
                    ['89' '50' '4E' '47'],
                    ['4F' '67' '67' '53'],
                    ['52' '49' '46' '46'],
                    ]
    siglist_2bit = [['4D', '5A'],
                    ['FF' 'FB'],
                    ['42' '4D'],
                    ['42' '4D']
                    ]
    typelist_4bit = ['application/pdf',
                     'image/gif',
                     'image/tiff',
                     'image/tiff',
                     'image/jpeg',
                     'application/x-zip-compressed',
                     'image/png',
                     'application/ogg',
                     'audio/wav',
                     ]
    typelist_2bit = ['application/octet-stream',
                     'audio/mpeg',
                     'image/bmp',
                     'audio/wav'
                     ]
    siglist_strings = [['3c', '3f', '78', '6d', '6c'],
                       ['58', '33', '44'],
                       ['68', '74', '6d', '6c'],
                       ]
    typelist_strings = ['application/xml',
                        'model/x3d+xml',
                        'text/html'
                        ]

    try:
        header = ["{:02x}".format(ord(c)) for c in open(filepath).read(140)]
    except IOError:
        print("Permission denied: %s" % filepath)
        return "text/plain"

    sig_2bit = header[:2]
    sig_4bit = header[:4]

    if sig_2bit in siglist_2bit:
        if sig_4bit in siglist_4bit:
            mime = typelist_4bit[siglist_4bit.index(sig_4bit)]
        else:
            mime = typelist_2bit[siglist_2bit.index(sig_2bit)]
    elif sig_4bit in siglist_4bit:
        mime = typelist_4bit[siglist_4bit.index(sig_4bit)]
    else:
        for sig_string in siglist_strings:
            if "".join(sig_string) in "".join(header):
                mime = typelist_strings[siglist_strings.index(sig_string)]
            else:
                print("Cannot determine mime type...defaulting to plain text")
                mime = "text/plain"
    return mime
