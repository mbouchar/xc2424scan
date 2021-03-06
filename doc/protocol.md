Network protocol to get scanned files from a Xerox WorkCentre C2424
-------------------------------------------------------------------

The port for the xerox scanning protocol is : 14882

All commands are ending with : '\n' (new line)
All command parameters are separated with : '\t' (tab)

All commands and responses are received integrally. They are separated
in multiple lines below only for readability

-------------
| COMMANDS |
-------------

    S: -> What we are sending to the printer
    R: -> What is received from the printer
    E: -> A little explanation of the command (or response)
    
    Get the current directory
    -------------------------
        S: tellfolder\n
        R: folder\tPublic\n

        E: folder <tab> (folder name) <new line>

    Get all available directories
    -----------------------------

        S: listfolders\n
        R: foldercount\t2\nfolder\tPublic\n
        folder\tmbouchar\n

        E: foldercount <tab> (number of folders) <new line>
        folder <tab> (folder name #1) <new line>
        folder <tab> (folder name #2) <new line>

    Get all file names (and informations) from the current directory
    ----------------------------------------------------------------

        S: listfiles\n
        R: filecount\t2\n
           file\t2006-01-27@10.03.17.tif\t2125464\t1138356222\t5\t100\t100\t848\t1096\t24\t139\t180\t24\n
           file\t2006-01-30@09.35.53.tif\t898086\t1138613772\t4\t100\t100\t848\t1096\t24\t139\t180\t24\n

        E: filecount <tab> (number of files) <new line>
           file <tab> (file name #1) <tab> (file size) <tab> unknown <tab> (number of pages) <tab> (max horizontal resolution) <tab> (max vertical resolution) <tab> (nb horizontal pixels) <tab> (nb vertical pixels) <tab> (max samplerate) <tab> (nb horizontal pixels preview) <tab> (nb vertical pixels preview) <tab> (max samplerate preview) <new line>
           ...

        for more informations about the returned fields, please read
        the file listfiles_example.txt.           

    Delete a file
    -------------

        S: deletefile\t2006-01-27@10.03.17.tif\n
        R: ok\n

        E: deletefile <tab> (file name) <new line>

----------------------
| SPECIFIC PROTOCOLS |
----------------------

    Get a preview of a file
    -----------------------

        S: setfile\t2006-01-27@10.03.17.tif\n
        R: ok\n
        S: setformat\tbmp\n
        R: ok\n
        S: setpage\t-1\n
        R: ok\n
        # Not necessary, but the Xerox scanning app is always
        # getting the file size before getting the file preview
        S: tellfilesize\n
        R: filesize\t75654\n
        S: sendblock\t10240
        R: sending\t10240\nBM*()*DSF*(8dsf9as) (...)

        E: setfile <tab> (file name) <new line>
        E: setformat <tab> (file format) <new line>
        E: setpage <tab> (page number) <new line>
        E: filesize <tab> (file size in bytes) <new line>
        E: sendblock <tab> (unknown)
        E: sending <tab> (unknown) <new line>
        (image data)

        Valid file formats are :
            bmp,
            gif,
            jpeg,
            pdf,
            tiff

        Valid page numbers are :
            -1 (for the preview)
            Nothing (for all the pages (pdf only))
            The page number, beginning with 1

        WARNING : tellfilesize only works if the format is tiff or bmp.
            
        WARNING : Some files don't have a preview (scanned at graphic,
                  for example). When asking for page -1, the server 
                  returns the error "no such". The client must handle
                  this event.

    Get a file
    ----------

        S: setfile\t2006-01-27@10.03.17.tif\n
        R: ok\n
        S: setusage\t1\t2
        R: ok\n
        S: setformat\ttiff\n
        R: ok\n
        S: setpage\n
        R: ok\n
        S: setresolution\t100\t100\n
        R: ok\n
        S: setsamplesize\t24\n
        R: ok\n
        S: sendblock\t10240\n
        R: sending\t10240\n*D0s(Fds98***) (...)
        ...

        E: setusage <tab> unknown <tab> unknown <new line>
        E: setresolution <tab> (horizontal) <tab> (vertical) <new line>
        E: setsamplesize <tab> (sample size) <new line>

        Valid Horizontal and Vertical resolutions are:
        	100
        	200
        	300
        	400
        	600
        Setting an invalid resolution or a resolution higher than the one
        used when scanning the file returns an error instead of 'ok'.

        Valid sample size are :
            1 (black and white)
            8 (grayscale)
            24 (24 bits color)
        Setting a sample size of 24 on a file scanned only on black and
        white doesn't result in an error.
            
        The maximum resolution of the file is set when scanning the
        file. If we try to get a higher resolution, an error will
        be sent.
        
        sendblock is asking a data size. The WorkCentre is sending the
        maximum bytes availables. If we are asking for 10240 bytes and
        we are receiving only 2046 bytes, then the file is complete.
        
        WARNING : When asking for a pdf, each page is sent separately.
            If the pdf has 5 pages, there will be 5 end of files, so we
            cannot only check for the end of one file while getting a pdf.

    Get in a protected folder
    -------------------------

        S: setpassword\t-1\n
        R: error\tprotected\n
        S: setpassword\t1234
        R: ok\n
        S: setfolder\ttesting\n
        R: ok\n

        E: setpassword <tab> (clear text password) <new line>
        
        The passwords for the protected folders are only 4 numbers long

----------
| Errors |
----------

    R: error\tsyntax\n

    Received when there is a syntax error in a command or if an
    invalid command has been send (ex. 'setformat bmp' instead of
    'setformat\tbmp')

    R: error\tcannot\n

    Received when a command parameter is invalid (ex. 'setformat\tpng')

    R: error\tnosuch\n

    Received when a dynamic parameter is invalid (ex. a 'setfile' command
    with an invalid file name or a 'setpage' command with an invalid
    page number)

    R: error\tprotected\n

    Received when trying to access a protected folder (with 'setfolder'
    command) with an invalid password

    R: error\teof\n

    Received when trying to receive more data where the file transmission
    is finished

-----------
| Unknown |
-----------

    This is a list of the unknown (or not clear) parameters

    - setusage : I have absolutely no idea what this command is supposed
                 to do
    - listfiles : Some of the informations returned are unknown. See
                  the file listfiles_example for more informations.
    - setsamplesize : What are the different values (now, we got 1, 8 and 24)?
    - The Xerox scan utility has already sent the following data to the scanner:
      02 04 05 B4 01 01 04 02
      The answer was :
      02 04 05 B4
    - ??? : Maybe there are other commands available, but for now, this is
            the list of known commands :
                - deletefile
                - listfiles
                - listfolders
                - sendblock
                - setfile
                - setformat
                - setpage
                - setpassword
                - setresolution
                - setsamplesize
                - setusage
                - tellfilesize
                - tellfolder
    
For questions about the protocol, send an email to :
Mathieu Bouchard <mbouchar@bioinfo.ulaval.ca>
