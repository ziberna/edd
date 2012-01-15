Edd
===

Installation
------------
1. copy the file from bin to your `$PATH` (e.g. /usr/bin)
2. copy edd directory to your `$PYTHONPATH` (e.g. /usr/lib/python3.2/site-packages)
3. create file ~/.config/edd
4. read configuration sample bellow and edit the file ~/.config/edd


Help message
------------

    usage: edd [-h] [--conf [CONFIG_PATH]] [FILE] [TOOL]
    
    Edd (C) 2011 Jure Žiberna
    
    positional arguments:
      FILE                  file to edit
      TOOL                  tool to use
    
    optional arguments:
      -h, --help            show this help message and exit
      --conf [CONFIG_PATH]  path to configuration file


Configuration sample
--------------------

    # a comment
    [TOOLS]
    vim
    nano # another comment
    geany
    somevar=sometool -arg1 --arg2
    
    [PATHS]
    HOME=/home/myname
    
    [FILES]
    httpd=/etc/httpd/conf/httpd.conf
    i3=$HOME/.i3/config with nano -x
    xinit=$HOME/.xinitrc with $somevar


Sample of usage
---------------

    [jure@Kant ~]$ edd httpd nonexistent
    > Error running nonexistent /etc/httpd/conf/httpd.conf:
    No such file or directory: 'nonexistent'
    [jure@Kant ~]$ edd httpd
    > Edited /etc/httpd/conf/httpd.conf with vim.
    [jure@Kant ~]$ edd httpd ask
       1) vim
       2) nano
       3) geany
    > Choose tool or type a command (default=1): 3
    > Edited /etc/httpd/conf/httpd.conf with geany.
    [jure@Kant ~]$ edd httpd ask
       1) vim
       2) nano
       3) geany
    > Choose tool or type a command (default=1): nano -x
    > Edited /etc/httpd/conf/httpd.conf with nano -x.
    [jure@Kant ~]$ edd httpd "vim -e"
    > Edited /etc/httpd/conf/httpd.conf with vim -e.
    [jure@Kant ~]$

\* It may seem confusing, but before edd says "Edited x with y.", it actually
  opens file x with command y. The message is shown after you have closed the
  tool, tool being an editor with graphical or command-line user interface, or
  any command you wish to pass the file path to.

Tips
----
1. You can use empty string for a variable. This is useful for a file variable,
   which makes edd open that file by default, without passing any arguments.
   You could do something like this:

        ######### a part from an Edd's config file #########
        =$HOME/a-file-i-edit-often

2. To hardcode path to configuration file, pass the path to main function in
   bin/edd. This is useful for running edd as root with configuration
   file in your home folder.

License
-------

>    Edd  (C) 2011  Jure Žiberna
>    This program comes with ABSOLUTELY NO WARRANTY.
>    This is free software, and you are welcome to redistribute it
>    under the terms of the GNU General Public License, version 3 or later.
