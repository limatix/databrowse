  // <!-- this script section modified from http://jumk.de/nospam/stopspam.html-->
    function CryptMailto( s )
    {
        var n = 0;
        var r = "";

        for( var i=0; i < s.length; i++ )
        {
            n = s.charCodeAt( i );
            if( n >= 49 && n <= 126 && n != 92)
            {
                n = n-9;
                if (n==92) n=92+9;
            } else if (n >= 40 && n <= 48) {
                n=n-9+127-40;
            }
            r += String.fromCharCode(n);
        }
        return r
    }


    function UnCryptMailto( s )
    {
        var n = 0;
        var r = "";
        for( var i = 0; i < s.length; i++)
        {
            n = s.charCodeAt( i );
            if( n >= 40 && n <= 117 && n != 92)
            {
                n = n+9
                if (n==92+9+9) n=92+9
            }
            else if ( n >= 118 && n <= 126) 
            {
                n = n+9-127+40

            }
            r += String.fromCharCode( n  );
        }
        return r;
    }

    function linkTo_UnCryptMailto( s )
    {
        location.href=UnCryptMailto( s );
    }

    function linkTo_CryptMailto( s )
    {
        //location.href=CryptMailto( s );
        document.write(CryptMailto( s ));
    }
