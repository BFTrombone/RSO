#!/usr/local/bin/perl
#
  ##################################################################
  #
  # htaccess password protector Version 3.1
  #
  # Copyright 2002 Techno Trade http://www.technotrade.com
  # Written By : Sammy Afifi   sammy@technotrade.com
  #
  # This is commercial software, 
  # please visit http://htaccess.technotrade.com/ for pricing
  #
  # 9/9/02
  ##################################################################
  $version = "3.1";

  #
  # To run the script, just load admin.cgi in your browser, type in the 
  # password and directory you wish to protect then click refresh
  #
  # After that, just add users using the "Add user" form, it will
  # then create the .htpasswd file in the directory you selected.
  # Then select generate .htaccess and have it auto-create it in 
  # the protected directory. Now anytime someone access 
  # www.yourdomain.com/protected_directory/ they will be prompted for
  # a username/password.
  # If the script is not able to create the .htaccess or .htpasswd files
  # then you will need to upload a blank .htpasswd (create one offline 
  # with a text editor), ftp it to the server and chmod 666 or 777
  # You also may need to manually upload the .htaccess file.
  #

  #  You do not need to change any of these variables. All modifications are done
  #  through the admin.cgi script when you load it in your browser
  #

  ##################################################################
  #
  # URL where the script is located, just keeping it as "admin.cgi" will work in most cases
  #

  $formloc = "admin.cgi";


  $adminvarsfile = "adminvars.cgi";  #  should exist in same folder as admin.cgi


  ##################################################################
  #
  # File name for batch imports
  # To be placed in $basedir + directory name you enter / $htimportname
  #
  $htimportname = "htimport.txt";
  

  ##################################################################
  #
  # no need to change .. but you can use any file name for storing passwords
  #
  # On some servers, you may need to upload a blank .htpasswd file into the directory
  # you are protecting and chmod it to 777
  #

  $htpasswdname = ".htpasswd";


  ##################################################################
  #
  # If you want the script to be able to work without a password supplied by 
  # the admin then change the $requirepassword variable to 0 instead of 1
  # You also may need to set this to 0 if you forgot your password and need to 
  # generate a new one or some servers use a different crypt method so the 
  # default "test" won't even work

  $requirepassword = 1;


  &get_variables;


  ##################################################################
  #
  #  Nothing should be changed below here ....
  #
  ##################################################################

  &parse_form;

  $demo = 0;

  srand(time);
  $letterlist = "a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z";
  @letters = split(",",$letterlist);
  $r1 = $letters[int(rand(25))];
  $r2 = $letters[int(rand(25))];
  $r3 = $letters[int(rand(25))];

  # assign a random password if field was left blank
  $FORM{'pass'} = "$r1$r2$r3" . int(rand(5000)) if ($FORM{'pass'} eq "");

  # only here for demo
  $FORM{'targetdir'} = "secure" if ($demo);

  # strip funny characters off
  # this prevents you from typing in /directory/directory2 in the script
  # if you do want to be able to protect sub-sub directories then put a #
  # infront of each of the targetdir lines below
  #
  $FORM{'targetdir'} =~ s/\\//g;
  $FORM{'targetdir'} =~ s/\|//g;
  $FORM{'targetdir'} =~ s/\;//g;


  # do not change
  $htpasswdloc = "$basedir$FORM{'targetdir'}/$htpasswdname";
  $htimportloc = "$basedir$FORM{'targetdir'}/$htimportname";

  if (( (crypt($FORM{'password'},"aa") ne $correctpass) && ($requirepassword)) || ($FORM{'targetdir'} eq "")) {
    print "Content-type: text/html\n\n";
    &print_css_header;
    &askforpass;
    &print_css_footer;
    exit;
  }



  &view_dot_file($basedir . $FORM{'targetdir'} . "/" . $htpasswdname) if ($FORM{'action'} eq "VIEWHTPASSWD");
  &view_dot_file($basedir . $FORM{'targetdir'} . "/.htaccess") if ($FORM{'action'} eq "VIEWHTACCESS");

  print "Content-type: text/html\n\n";

  &adduser if ($FORM{'action'} eq "ADD");
  &batchadduser("form") if ($FORM{'action'} eq "IMPORT");
  &batchadduser("file") if ($FORM{'action'} eq "IMPORTFILE");
  &deleteuser if ($FORM{'action'} eq "DELETE");
  &generatehtaccess if ($FORM{'action'} eq "GEN") && (! $demo);
  &generatehtaccesscobalt if ($FORM{'action'} eq "GENC") && (! $demo);
  &generatehtaccesszeus if ($FORM{'action'} eq "GENZ") && (! $demo);

  &extractemails if ($FORM{'action'} eq "EMAILS");
  &update_settings if ($FORM{'action'} eq "CHANGESETTINGS") && (! $demo);

  &listusers($FORM{'searchby'},$FORM{'searchkey'});

  &print_css_header;
  &print_output;
  &print_css_footer;

  exit;



#################################################
sub view_dot_file {
   my($fname) = @_;
   print "Content-type: text/plain\n\n";
   open(F,$fname);
   while ($line = <F>) {
     print $line;
   }
   close(F);
   exit;
}

#################################################
sub get_variables {

  $cannotopen = 0;

  if (! (-e $adminvarsfile)) {
    $cannotopen = 1 if (! open(A,">$adminvarsfile"));
    $base = &get_basedir;


    $vardata=<<ADVARS;
$base
XZZZZZZZZZX
aaqPiZY5xR5l.
XZZZZZZZZZX
/usr/lib/sendmail
XZZZZZZZZZX
info\@yourdomain.com
XZZZZZZZZZX
Your Access Account
XZZZZZZZZZX
10
XZZZZZZZZZX
This is some text that will be placed at the top of e-mails sent to users.
XZZZZZZZZZX
Text to be placed at the bottom of the e-mail

Techno Trade's Password Protector at http://www.technotrade.com/protect/
XZZZZZZZZZX

ADVARS
    print A $vardata;
    close(A);
  } 

  if ($cannotopen) {
    print "Content-type: text/html\n\n";
    print "Trouble creating the $adminvarsfile, you will need to copy/paste the variables";
    print " below into a file called $adminvarsfile and upload it to the server<br><br>\n";
    print "<br><pre>$vardata</pre><br>\n";
    exit;
  }   
  open(A,$adminvarsfile);
  @AVARS = <A>;
  close(A);
  foreach $var (@AVARS) {
    #chop($var);
    $avar.= $var;
  }
  @adminvars = split("XZZZZZZZZZX",$avar);
#  foreach $var (@adminvars) {
#    print "var = $var<br>\n"
#  }
  $basedir      = &clean_string($adminvars[0]);
  $correctpass  = &clean_string($adminvars[1]);
  $mailprog     = &clean_string($adminvars[2]);
  $emailfrom    = &clean_string($adminvars[3]);
  $emailsubject = &clean_string($adminvars[4]);
  $scrollsize   = &clean_string($adminvars[5]);
  $emailtop     = $adminvars[6];
  $emailbottom  = $adminvars[7];

  #print "$basedir - $correctpass - $mailprog --<br>\n";
}



#################################################
sub update_settings {


  $cannotopen = 0;
  $cannotopen = 1 if (! open(A,">$adminvarsfile"));

  $FORM{'newpassword'} = crypt($FORM{'newpassword'},"aa");
  $vardata=<<ADVARS;
$FORM{'newbasedir'}
XZZZZZZZZZX
$FORM{'newpassword'}
XZZZZZZZZZX
$FORM{'newmailprog'}
XZZZZZZZZZX
$FORM{'newemailfrom'}
XZZZZZZZZZX
$FORM{'newemailsubject'}
XZZZZZZZZZX
$FORM{'newscrollsize'}
XZZZZZZZZZX
$FORM{'newemailtop'}
XZZZZZZZZZX
$FORM{'newemailbottom'}
XZZZZZZZZZX

ADVARS
    print A $vardata;
    close(A);


  if ($cannotopen) {
    print "Content-type: text/html\n\n";
    print "Trouble updating the $adminvarsfile, you may need to change the file's permissions by chmod 777 $adminvarsfile<br><br>\n";
    print "Here is what the $adminvarsfile should look like : <HR><br><pre>$vardata</pre><br>\n";
    exit;
  }   

  print "Program Settings have been saved : <A HREF=\"$formloc\">Click Here to log back in</A><br>\n";
  exit;



}
#################################################
sub clean_string {
  my($s) = @_;

  $s =~ s/\"//g;
  $s =~ s/\cM/\n/g;

  $s =~ s/\n//g;

  return($s);
}

#################################################
sub get_basedir {

  $bd = $ENV{'DOCUMENT_ROOT'};
  $bd.= "/";

  $bd =~ s/\/\//\//;
  return($bd);

}

#################################################
sub  print_css_footer {
print<<CSSF;

</BODY>
</HTML>

CSSF

}


#################################################
sub print_css_header {

print<<CSSH;

<HTML>
	<HEAD>

	<title>TechnoTrade's .htaccess manager</title>
<STYLE type=text/css>
.tbody{COLOR: black;FONT-FAMILY:  Verdana, Helvetica, Arial;FONT-SIZE: 9pt;LINE-HEIGHT: normal;TEXT-DECORATION: none}
.tbody A{COLOR: navy;FONT-FAMILY:  Verdana, Arial, helvetica;FONT-SIZE: 9pt;TEXT-DECORATION: none}
.tbody A:active{COLOR: navy;FONT-FAMILY:  verdana, arial, helvetica;FONT-SIZE: 9pt}
.tbody A:hover{COLOR: navy;FONT-FAMILY:  verdana, arial, helvetica;FONT-SIZE: 9pt;TEXT-DECORATION: none}
.tbodygrey{COLOR: gray;FONT-FAMILY:  Verdana, Helvetica, Arial;FONT-SIZE: 9pt;LINE-HEIGHT: normal;TEXT-DECORATION: none}
.tbodygrey A{COLOR: gray;FONT-FAMILY:  Verdana, Arial, helvetica;FONT-SIZE: 9pt;TEXT-DECORATION: none}
.tbodygrey A:active{COLOR: navy;FONT-FAMILY:  verdana, arial, helvetica;FONT-SIZE: 9pt}
.tbodygrey A:hover{COLOR: navy;FONT-FAMILY:  verdana, arial, helvetica;FONT-SIZE: 9pt;TEXT-DECORATION: none}
.tbodybig{COLOR: black;FONT-FAMILY: Trebuchet MS,verdana, tahoma, arial, helvetica;FONT-SIZE: 11pt;LINE-HEIGHT: normal;TEXT-DECORATION: none}
.tbodybig A{COLOR: navy;FONT-FAMILY:  verdana, arial, helvetica;FONT-SIZE: 11pt;TEXT-DECORATION: none}
.tbodybig A:active{COLOR: navy;FONT-FAMILY:  verdana, arial, helvetica;FONT-SIZE: 11pt}
.tbodybig A:hover{COLOR: navy;FONT-FAMILY:  verdana, arial, helvetica;FONT-SIZE: 11pt;TEXT-DECORATION: none}
.tbodysmall{COLOR: black;FONT-FAMILY:  Verdana, Helvetica, Arial;FONT-SIZE: 8pt;LINE-HEIGHT: normal;TEXT-DECORATION: none}
.tbodysmall A{COLOR: navy;FONT-FAMILY:  Verdana, Arial, helvetica;FONT-SIZE: 8pt;TEXT-DECORATION: none}
.tbodysmall A:active{COLOR: navy;FONT-FAMILY:  verdana, arial, helvetica;FONT-SIZE: 8pt}
.tbodysmall A:hover{COLOR: navy;FONT-FAMILY:  verdana, arial, helvetica;FONT-SIZE: 8pt;TEXT-DECORATION: none}
.smummaincolor {BACKGROUND-COLOR: #cccc99}
.smumhlcolor {BACKGROUND-COLOR: #e6dec4}
.smumsepcolor {BACKGROUND-COLOR: #e1e1e1}
.white {BACKGROUND-COLOR: white}
.black {BACKGROUND-COLOR: black}
.smumbordercolor {BACKGROUND-COLOR: darkgray}
.smumcolora {BACKGROUND-COLOR: #cccc99}
.smumcolorb {BACKGROUND-COLOR: #999966}
</style>
</HEAD>


<BODY marginwidth=0 marginheight=0 leftmargin=0 topmargin=0>
<BR><BR>


CSSH


}





####################################
#

#
sub print_output {

   $demotext = "";
   $demotext = "<BR><b>After you add a user, go to <A HREF=\"/secure/\" target=\"loginwin\">http://htaccess.technotrade.com/secure/</A> and try logging in to the secure folder</b>" if ($demo);
print<<RELO1;



<table cellspacing=0 border=0 cellpadding=0 width=90% align=center>
<tr>
<td align=center valign=middle>
						
<table border=0 cellspacing=0 cellpadding=0 width=95% class=smumbordercolor>
	<form action="$formloc" method=post>
	<input name=todo type=hidden value=login>
	<input name=url type=hidden value="/smusermanager/admin/default.asp">
<tr class=smumbordercolor>
<td>
	<table border=0 cellspacing=1 cellpadding=0 width=100% >
	<tr class=smumbordercolor>
	<td colspan=3>
		<table border=0 cellspacing=1 cellpadding=5 width=100% colspan=3>



 		<tr class=smumhlcolor>
		<td colspan=2 align=center><font class=tbody><b>Techno Trade's Password Protection -- Add User</b></font>
		</td>
 
  
                <tr class=smumsepcolor>
		<td ><font class=tbodysmall>

  <PRE><FORM METHOD=POST ACTION="$formloc">
  username  : <INPUT NAME="username" SIZE=20> 
  password  : <INPUT TYPE=password SIZE=20 name="pass"> (leave blank for random)
  name      : <INPUT SIZE=20 name="name"> 
  email     : <INPUT SIZE=30 name="email">
  comments  : <INPUT SIZE=30 name="comments">
  expires   : <INPUT SIZE=10 name="expires"> YYYYMMDD (ex: 20040212)

  Extra E-mail Text : 
  <TEXTAREA NAME="extratext" COLS=50 ROWS=4 WRAP=VIRTUAL></TEXTAREA>

  <INPUT TYPE="CHECKBOX" NAME="sendemail" VALUE="Y">       : Check to e-mail new entry to user

  </PRE>
  <INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
  <INPUT TYPE="hidden" NAME="targetdir" VALUE="$FORM{'targetdir'}">
  <INPUT TYPE="submit" Value="Add User">
  <INPUT TYPE="hidden" NAME="action" VALUE="ADD">
$demotext
  </FORM>

                </font>
		</td>
		</tr>


$listusers

		<tr class=smumhlcolor>
		<td colspan=2 align=center><font class=tbody><b>Change Protected Directory</b></font>
		</td>
		</tr>

		<tr class=smumsepcolor>
		<td ><font class=tbodysmall>
 Change to a directory which you want password protected<BR> 
 <FORM METHOD="POST" ACTION="$formloc">
 <PRE><INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
 Current Base Path : $basedir
 Directory         : <INPUT NAME="targetdir" VALUE="$FORM{'targetdir'}" SIZE=40>
 </PRE>
 <INPUT TYPE="submit" Value=" Change Directory ">
 </FORM>
<br>
<table align=right>
<tr><td>
<FORM METHOD="POST" ACTION="$formloc">
<INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
<INPUT TYPE="hidden" NAME="targetdir" VALUE="$FORM{'targetdir'}">
<INPUT TYPE="hidden" NAME="action" VALUE="VIEWHTACCESS">
<INPUT TYPE=submit VALUE=" View .htaccess file ">
</FORM>
</td>
<td>
<FORM METHOD="POST" ACTION="$formloc">
<INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
<INPUT TYPE="hidden" NAME="targetdir" VALUE="$FORM{'targetdir'}">
<INPUT TYPE="hidden" NAME="action" VALUE="VIEWHTPASSWD">
<INPUT TYPE=submit VALUE=" View $htpasswdname file ">
</FORM>
</td>
</tr></table>
                </font>
		</td>
		</tr>



 		<tr class=smumhlcolor>
		<td colspan=2 align=center><font class=tbody><b>Generate .htaccess file</b></font>
		</td>

                <tr class=smumsepcolor>
		<td ><font class=tbodysmall>

 <FORM METHOD="POST" ACTION="$formloc">
 <PRE><INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
 Directory : <INPUT NAME="targetdir" VALUE="$FORM{'targetdir'}">
 Realm     : <INPUT NAME="realm" VALUE="Member Area"> Message displayed in pop-up login box
 <INPUT TYPE=CHECKBOX NAME="create" VALUE="Y"> Create the .htaccess file on server ?

 <INPUT TYPE=RADIO NAME="action" VALUE="GEN" CHECKED>.htaccess file for Apache
 <INPUT TYPE=RADIO NAME="action" VALUE="GENC">.htaccess file for Cobalt RAQ
 <INPUT TYPE=RADIO NAME="action" VALUE="GENZ">.htaccess file for Zeus
 </PRE>
 <INPUT TYPE="submit" Value=" Generate ">
 </FORM>
 <BR>
 This will display what your .htaccess file should look like for the above directory<BR>
 Just copy and paste the results of this to a text editor, save the file as .htaccess and
 upload to the directory you wish to password protect. (Use your browser's back button to return).
 <P>If you checked "create htaccess" then the script will attempt to create a .htaccess file in
 addition to displaying it in your browser. If this doesn't work on your server, then you will
 manually have to upload the .htaccess file.

                </font>
		</td>
		</tr>

 		<tr class=smumhlcolor>
		<td colspan=2 align=center><font class=tbody><b>Extract Emails</b></font>
		</td>

                <tr class=smumsepcolor>
		<td ><font class=tbodysmall>

 <FORM METHOD="POST" ACTION="$formloc">
 <INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
 <INPUT TYPE=HIDDEN NAME="targetdir" VALUE="$FORM{'targetdir'}">

 <INPUT TYPE="hidden" NAME="action" VALUE="EMAILS">
 <INPUT TYPE=CHECKBOX NAME="comma" VALUE="Y"> Add a comma after each line ?<BR>
 <INPUT TYPE="submit" Value=" Extract E-mails "><BR><BR>
 This feature is used to pull all the e-mail address from your member list.
 You can then copy and paste the list to your favorite e-mail program.
 </FORM>
                </font>
		</td>
		</tr>


 		<tr class=smumhlcolor>
		<td colspan=2 align=center><font class=tbody><b>Manual Import</b></font>
		</td>

                <tr class=smumsepcolor>
		<td ><font class=tbodysmall>

 <FORM METHOD="POST" ACTION="$formloc">
 <INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
 <INPUT TYPE=HIDDEN NAME="targetdir" VALUE="$FORM{'targetdir'}">
 Copy/paste your data here :<BR>
 <TEXTAREA NAME="batch" COLS=50 ROWS=10 WRAP=VIRTUAL></TEXTAREA><BR>
 <INPUT TYPE=CHECKBOX NAME="sendemail" VALUE="Y"> Send an e-mail to each user ? (if e-mail address supplied)<BR>
 <INPUT TYPE=CHECKBOX NAME="sendcomment" VALUE="Y"> Include comments field in emails ?<BR>
 <INPUT TYPE="hidden" NAME="action" VALUE="IMPORT">
 <INPUT TYPE="submit" Value=" Batch Import "><BR><BR>
 This feature lets you batch import multiple usernames/passwords at the same time.<BR>
 Format is username,password,name,email,comments.<BR>
 Or you can add usernames and passwords only : username,password<BR>
 Or username/password and name : username,password,name etc.<BR>
 </FORM>
                </font>
		</td>
		</tr>


 		<tr class=smumhlcolor>
		<td colspan=2 align=center><font class=tbody><b>Import from file</b></font>
		</td>

                <tr class=smumsepcolor>
		<td ><font class=tbodysmall>

 <FORM METHOD="POST" ACTION="$formloc">
 <INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
 <INPUT TYPE=HIDDEN NAME="targetdir" VALUE="$FORM{'targetdir'}">
 File name to import : $htimportloc<BR>
 <br><br>
 <INPUT TYPE=CHECKBOX NAME="sendemail" VALUE="Y"> Send an e-mail to each user ? (if e-mail address supplied)<BR>
 <INPUT TYPE=CHECKBOX NAME="sendcomment" VALUE="Y"> Include comments field in emails ?<BR>
 <INPUT TYPE="hidden" NAME="action" VALUE="IMPORTFILE">
 <INPUT TYPE="submit" Value=" Batch Import "><BR><BR>
 This feature lets you batch import multiple usernames/passwords from a text file.<BR>
 Format is username,password,name,email,comments.<BR>
 Or you can add usernames and passwords only : username,password<BR>
 Or username/password and name : username,password,name etc.<BR>
 You may also leave the password field blank and the script will generate a random one. ex:<br>
 joe123,,Joe Smith,joe\@joe.com
 </FORM>
 <BR>
                </font>
		</td>
		</tr>


 		<tr class=smumhlcolor>
		<td colspan=2 align=center><font class=tbody><b>Change Program Settings</b></font>
		</td>

                <tr class=smumsepcolor>
		<td ><font class=tbodysmall>

 <FORM METHOD="POST" ACTION="$formloc">
 <PRE><INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
 Base Directory   : <INPUT NAME="newbasedir" SIZE=60 VALUE="$basedir">
 Password         : <INPUT NAME="newpassword" SIZE=20 VALUE="$FORM{'password'}" TYPE=PASSWORD>
 Path to Sendmail : <INPUT NAME="newmailprog" SIZE=40 VALUE="$mailprog">
 List Scroll Size : <INPUT NAME="newscrollsize" SIZE=10 VALUE="$scrollsize"> Size of member list window

 Email From       : <INPUT NAME="newemailfrom" SIZE=40 VALUE="$emailfrom">
 Email Subject    : <INPUT NAME="newemailsubject" SIZE=40 VALUE="$emailsubject">

 Top of Email     : 
                    <TEXTAREA NAME="newemailtop" COLS=50 ROWS=5>$emailtop</TEXTAREA>

 Bottom of Email  : 
                    <TEXTAREA NAME="newemailbottom" COLS=50 ROWS=5>$emailbottom</TEXTAREA>

 </PRE>
 <INPUT TYPE="hidden" NAME="action" VALUE="CHANGESETTINGS">
 <INPUT TYPE=HIDDEN NAME="targetdir" VALUE="$FORM{'targetdir'}">
 <INPUT TYPE="submit" Value=" Update Program Settings ">
 </FORM>
 <BR>

                </font>
		</td>
		</tr>
		</table>

	</td>
	</tr>
	</table>
</td>
</tr>
</form>
</table>

</td>
</tR>
<tr>
<td align=center><br><br><font class=tbody>Copyright <a href="http://htaccess.technotrade.com/">TechnoTrade.com</a>. All rights Reserved. Version $version</font>
</td>
</tr>
</table>

RELO1
}


#######################################
sub askforpass {

 #print "Content-type: text/html\n\n";

 $invalidpass = "";
 if ((crypt($FORM{'password'},"aa") ne $correctpass) && ($requirepassword) && ($FORM{'password'} ne "")) {
    $invalidpass = "<font class=tbodysmall>Invalid Password, try again.</font><br>"; 
 }

 print<<REFRE1;

<table cellspacing=0 border=0 cellpadding=0 width=90% align=center>
<tr>
<td align=center valign=middle>
						
<table border=0 cellspacing=0 cellpadding=0 width=95% class=smumbordercolor>
	<form action="$formloc" method=post>
	<input name=todo type=hidden value=login>
	<input name=url type=hidden value="/smusermanager/admin/default.asp">
<tr class=smumbordercolor>
<td>
	<table border=0 cellspacing=1 cellpadding=0 width=100% >
	<tr class=smumbordercolor>
	<td colspan=3>
		<table border=0 cellspacing=1 cellpadding=5 width=100% colspan=3>
		<tr class=smumhlcolor>
		<td colspan=2 align=center><font class=tbody><b>.htaccess Manager</b></font>
		</td>
		</tr>

		<tr class=smumsepcolor>
		<td colspan=2 align=center>$invalidpass<font class=tbodysmall>Please login with your Password and Directory to Protect.</font>
		</td>
		</tr>

		<tr class=smumsepcolor>
		<td align=right><font class=tbody><b>Password</b></font>
		</td>
		<td><font class=tbody><input name=password type=password type=text size=20>
		</td>
		</tr>

		<tr class=smumsepcolor>
		<td align=right><font class=tbody><b>Directory</b></font>
		</td>
		<td><font class=tbody><input name=targetdir size=20>
		</td>
		</tr>

		<tr class=smumsepcolor>
		<td colspan=2 align=right><input type=submit Value=" Login ">
		</td>
		</tr>
		</table>
	</td>
	</tr>
	</table>
</td>
</tr>
</form>
</table>

</td>
</tR>
<tr>
<td align=center><br><br><font class=tbody>Copyright <a href="http://htaccess.technotrade.com/">TechnoTrade.com</a>. All rights Reserved.</a> Version $version</font>
</td>
</tr>
</table>


REFRE1
}


#####################################
#
# Prints the bottom box showing path and .htaccess format
#
sub generatehtaccess {

  $FORM{'realm'} =~ s/\"//g;

print<<GENHT;
<PRE>
AuthName "$FORM{'realm'}"
AuthType Basic
AuthUserFile $basedir$FORM{'targetdir'}/$htpasswdname
&lt;limit GET POST>
require valid-user
&lt;/limit>
</PRE>
GENHT

  if ($FORM{'create'} eq "Y") {
    if (! open(F,">$basedir$FORM{'targetdir'}/.htaccess")) {
      print "<BR><BR>Sorry, can't create the .htaccess file\n";
      exit;
    }
    print F<<GENHT1;
AuthName "$FORM{'realm'}"
AuthType Basic
AuthUserFile $basedir$FORM{'targetdir'}/$htpasswdname
<limit GET POST>
require valid-user
</limit>

GENHT1
    close(F);
    print "<BR><BR><BR> File Created ! FTP into your $basedir$FORM{'targetdir'}/ and see if a .htaccess file exists\n";
  }
  exit;
}

#####################################
#
# Prints the bottom box showing path and .htaccess format
#
#####################################
#
# Prints the bottom box showing path and .htaccess format
#
sub generatehtaccesscobalt {

  $FORM{'realm'} =~ s/\"//g;


print<<GENHT;
<PRE>
order allow,deny 
allow from all 
require valid-user 
Authname "$FORM{'realm'}
AuthPAM_Enabled off 
Authtype Basic 
AuthUserFile $basedir$FORM{'targetdir'}/$htpasswdname
</PRE>
GENHT

  if ($FORM{'create'} eq "Y") {
    if (! open(F,">$basedir$FORM{'targetdir'}/.htaccess")) {
      print "<BR><BR>Sorry, can't create the .htaccess file\n";
      exit;
    }
    print F<<GENHT1;
order allow,deny 
allow from all 
require valid-user 
Authname "$FORM{'realm'}"
AuthPAM_Enabled off 
Authtype Basic 
AuthUserFile $basedir$FORM{'targetdir'}/$htpasswdname

GENHT1
    close(F);
    print "<BR><BR><BR> File Created ! FTP into your $basedir$FORM{'targetdir'}/ and see if a .htaccess file exists\n";
  }
  exit;
}

#####################################
#
# Prints the bottom box showing path and .htaccess format
#
#####################################
#
# Prints the bottom box showing path and .htaccess format
#
sub generatehtaccesszeus {

  $FORM{'realm'} =~ s/\"//g;


print<<GENHT;
<PRE>
AuthType Basic
AuthName "$FORM{'realm'}"
AuthUserFile $htpasswdname
Require valid-user
&lt;Files .*>
deny from all
&lt;/Files>
</PRE>
GENHT

  if ($FORM{'create'} eq "Y") {
    if (! open(F,">$basedir$FORM{'targetdir'}/.htaccess")) {
      print "<BR><BR>Sorry, can't create the .htaccess file\n";
      exit;
    }
    print F<<GENHT1;
AuthType Basic
AuthName "$FORM{'realm'}"
AuthUserFile $htpasswdname
Require valid-user
<Files .*>
deny from all
</Files>

GENHT1
    close(F);
    print "<BR><BR><BR> File Created ! FTP into your $basedir$FORM{'targetdir'}/ and see if a .htaccess file exists\n";
  }
  exit;
}


###########################################
#
#  List users
#
sub listusers {

  my($searchby,$searchkey) = @_;

  #$searchby = "keyword";
  #$searchkey = "joe";

  local($user,$counter,$x);
  if (!(-e $htpasswdloc)) {
    $counter = 0;
$listusers=<<LLNONE;

 		<tr class=smumhlcolor>
		<td colspan=2 align=center><font class=tbody><b>Member List</b></font>
		</td>

                <tr class=smumsepcolor>
		<td ><font class=tbodysmall>
                User list is currently blank for : $htpasswdloc
   		</font>
		</td>
		</tr>

LLNONE

    return;
  }
 
  $listusers=<<LISTUSERS;
 		<tr class=smumhlcolor>
		<td colspan=2 align=center><font class=tbody><b>List Users</b><br>Directory : $basedir$FORM{'targetdir'}</font>
		</td>

                <tr class=smumsepcolor>
		<td ><font class=tbodysmall>

  <FORM METHOD="POST" ACTION="$formloc">

LISTUSERS

  open(FILE,$htpasswdloc);
  #flock(FILE,2);
  @USERS = <FILE>;
  close(FILE);

  foreach $us (@USERS) {
    chop($us);
    if (substr($us,0,1) ne "#") {
      ($user,$pass) = split (":",$us,2);
      $MYUSERLIST{$user} = 1;
      $PASSLIST{$user} = $pass;
    } else {
      $commentline = substr($us,1);
      ($user,$name,$email,$comments,$extra) = split(/\s*\|\s*/,$commentline,5);
      #($created,$expired) = split(/\s*\-\s*/,$extra,2);
      $expired = $extra;
      $MYUSERLIST{$user} = $expired;
      $USERINFO{$user} = $commentline;
    }
  }

  #
  # Sort by username
  #
  

  if ($searchby eq "expired") {

    @USERLIST = sort {
  		    $MYUSERLIST{$a} cmp $MYUSERLIST{$b}
  	    } keys %MYUSERLIST; 	
  } else {
    @USERLIST = sort keys %MYUSERLIST;
  }
  #@USERLIST = sort {$a cmp $b} @USERLIST;

  $listusers.= "<SELECT NAME=\"username\" SIZE=$scrollsize MULTIPLE>\n";

  $listcount = 0;

  foreach $user (@USERLIST) {
    if (($searchby eq "keyword" && $USERINFO{$user} =~ /$searchkey/i) || ($searchby ne "keyword") ) {
      $listcount++;
      $listusers.= "<OPTION VALUE=\"$user\">$user";
      $listusers.= "(b)" if ($PASSLIST{$user} eq "");
      if ($USERINFO{$user}) {
         ($user,$name,$email,$comments,$extra) = split(/\s*\|\s*/,$USERINFO{$user},5);
         #($created,$expired) = split(/\s*\-\s*/,$extra,2);
         $expired = $extra;
  
         if ($searchby eq "expired") {
           $listusers.= " - $expired - $name - $email - $comments\n";
         } else {
           $listusers.= " - $name - $email - $expired - $comments\n";
         }
      }
     }
  }
$listusers.=<<LU1;
</SELECT>
<INPUT TYPE="hidden" NAME="action" VALUE="DELETE">
<INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
<INPUT TYPE="HIDDEN" NAME="targetdir" VALUE="$FORM{'targetdir'}">
<BR>
<INPUT TYPE=\"submit\" Value=\"Delete User (Select one or more from list)\">  There are $listcount users.
<BR><BR>
<PRE>

<b>Or Select a user above then modify</b>

New Password   : <INPUT TYPE=PASSWORD NAME="newpass" SIZE=15>

New Name       : <INPUT NAME="newname" SIZE=20>

New E-mail     : <INPUT NAME="newemail" SIZE=30>

New Comments   : <INPUT NAME="newcomments" SIZE=30>

New Expiration : <INPUT NAME="newexpiration" SIZE=10> (format : YYYYMMDD)

<INPUT TYPE="CHECKBOX" NAME="sendemail" VALUE="Y">       : Check to e-mail modification to user
</PRE>

<INPUT NAME="modbutton" TYPE="submit" Value="Modify User">
<INPUT NAME="searchby" TYPE="hidden" Value="$FORM{'searchby'}">
</FORM>

<table width=100%>
<tr>
<td width=33%>
<FORM METHOD="POST" ACTION="$formloc">
<INPUT TYPE="hidden" NAME="action" VALUE="LISTUSERS">
<INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
<INPUT TYPE="HIDDEN" NAME="targetdir" VALUE="$FORM{'targetdir'}">
<INPUT TYPE="hidden" NAME="searchby" VALUE="expired">
<INPUT TYPE=SUBMIT VALUE=" Sort By Expiration Date ">
</FORM>
</td>
<td width=33%>
<FORM METHOD="POST" ACTION="$formloc">
<INPUT TYPE="hidden" NAME="action" VALUE="LISTUSERS">
<INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
<INPUT TYPE="HIDDEN" NAME="targetdir" VALUE="$FORM{'targetdir'}">
<INPUT TYPE="hidden" NAME="searchby" VALUE="">
<INPUT TYPE=SUBMIT VALUE=" Sort By UserName ">
</FORM>
</td>
<td width=33%>
<FORM METHOD="POST" ACTION="$formloc">
<INPUT TYPE="hidden" NAME="action" VALUE="LISTUSERS">
<INPUT TYPE="hidden" NAME="password" VALUE="$FORM{'password'}">
<INPUT TYPE="HIDDEN" NAME="targetdir" VALUE="$FORM{'targetdir'}">
<INPUT TYPE="hidden" NAME="searchby" VALUE="keyword">
<INPUT NAME="searchkey" size=10 value=$FORM{'searchkey'}> <INPUT TYPE=SUBMIT VALUE=" Keyword Search ">
</FORM>
</td>
</tr>
</table>


                </font>
		</td>
		</tr>

LU1
}

###########################################
#
#  Extract E-mails
#
sub extractemails {

  local($user,$counter,$x);
  if (!(-e $htpasswdloc)) {
    $counter = 0;
    return;
  }
 
  open(FILE,$htpasswdloc);
  #flock(FILE,2);
  @USERS = <FILE>;
  close(FILE);
  print "Extracting E-mails ... <BR><BR>";
  foreach $us (@USERS) {
    if (substr($us,0,1) eq "#") {
      $commentline = substr($us,1);
      ($user,$name,$email,$comments,$extra) = split(/\s*\|\s*/,$commentline,5);
      if ($email =~ /\@/) {
         print "$email";
         print "," if ($FORM{'comma'} eq "Y");
         print "<BR>\n";
      }
    }
  }
  exit;
}


###################################################
#
# Delete User
#
sub deleteuser {

  open(FILE,$htpasswdloc);
  #flock(FILE,2);
  @USERS = <FILE>;
  close(FILE);
  if (($FORM{'modbutton'} eq "Modify User") && ($morethanone)) {
    print "You can only modify one user at a time ...<br>";
    exit;
  }
  @multipleusers = split(/\s*\,\s*/,$FORM{'username'});
  foreach $mu (@multipleusers) {
    $MULUSERS{$mu} = 1;
    #print "MULUSER = $mu<br>\n";
  }
  open(FILE,">$htpasswdloc");
  #flock(FILE,2);
  $counter = @USERS;
  for ($x=0; $x < $counter; $x++) {
    $USERS[$x] =~ s/\n//g;
    if (substr($USERS[$x],0,1) ne "#") {
      ($user,$pass) = split (":",$USERS[$x],2);
      $delpass = $pass if ($FORM{'username'} eq $user);
      $deluser = $user if ($FORM{'username'} eq $user);
    } else {
      $commentline = substr($USERS[$x],1);
      $commentline =~ s/\n//g;
      ($user,$name,$email,$comments,$extra) = split(/\s*\|\s*/,$commentline,5);
      if ($FORM{'username'} eq $user) {
        $deluser = $user;
        $delname = $name;
        $delemail = $email;
        $delcomments = $comments;
        $delextra = $extra;
      }
    }
    print FILE "$USERS[$x]\n" if ($MULUSERS{$user} != 1);
  }

  if (($FORM{'username'} ne "") && ($FORM{'modbutton'} eq "Modify User")) {

    if ($FORM{'newpass'} eq "") {
      print FILE "$deluser:$delpass\n";
    } else {
      $r1 = $letters[int(rand(25))];
      $r2 = $letters[int(rand(25))];
      print FILE "$deluser:" . crypt($FORM{'newpass'},"$r1$r2") . "\n";
    }
    $delname     = $FORM{'newname'} if ($FORM{'newname'} ne "");
    $delemail    = $FORM{'newemail'} if ($FORM{'newemail'} ne "");
    $delcomments = $FORM{'newcomments'} if ($FORM{'newcomments'} ne "");
    $delextra = $FORM{'newexpiration'} if ($FORM{'newexpiration'} ne "");
    $delname =~ s/\|//g;
    $delemail =~ s/\|//g;
    $delcomments =~ s/\|//g;
    $delextra =~ s/\|//g;

    print FILE "#$deluser|$delname|$delemail|$delcomments|$delextra\n";
    if (($FORM{'sendemail'} eq "Y") && ($delemail =~ /\@/)) {
       &send_email($delemail,$deluser,$FORM{'newpass'},"");
    }
  }
  close(FILE);

}

#################################################
#
# Add user to the file
#
sub adduser {

  $FORM{'pass'} =~ s/\n//g;
  $FORM{'email'} =~ s/\n//g;
  $FORM{'name'} =~ s/\n//g;
  $FORM{'comments'} =~ s/\n//g;
  $FORM{'pass'} =~ s/\|//g;
  $FORM{'email'} =~ s/\|//g;
  $FORM{'name'} =~ s/\|//g;
  $FORM{'comments'} =~ s/\|//g;
  $FORM{'expires'} =~ s/\|//g;

  
  &endscript("Username must be alphabetic + numeric!")
    unless $FORM{'username'} =~ /^[A-Z,a-z,0-9,\-,\@,\.,\_]+$/;

  &endscript("Your must enter a password!")
    unless $FORM{'pass'} =~ /\S/;


  open (PW, "+>>$htpasswdloc") ||
  &endscript("Cannot Locate $htpasswdloc: $!");
  #flock (PW, 2);			
  seek (PW, 0, 0);
  while ($line = <PW>) {
    ($user,$other) = split (":",$line);
    &endscript("sorry, that username is already taken") if $user eq $FORM{'username'};
  }

  seek (PW, 0, 2);
  $password = $FORM{'pass'};
  $r1 = $letters[int(rand(25))];
  $r2 = $letters[int(rand(25))];
  print PW "$FORM{'username'}:" . crypt($password,"$r1$r2") . "\n";
  print PW "#$FORM{'username'}|$FORM{'name'}|$FORM{'email'}|$FORM{'comments'}|$FORM{'expires'}\n";
  close PW;
  
  if (($FORM{'sendemail'} eq "Y") && ($FORM{'email'} =~ /\@/)) {
     &send_email($FORM{'email'},$FORM{'username'},$FORM{'pass'},$FORM{'extratext'});
  }

}

#################################################
#
# Batch Add users to the file
#
sub batchadduser {
  my($imptype) = @_;

  if ($imptype eq "form") {
     @alldata = split(/\s*\n\s*/,$FORM{'batch'});
     foreach $line (@alldata) {
       $line =~ s/\n//g;
       $line =~ s/\cM//g;
       push (@batching,$line) if (length($line) > 2);
     }
  }

  if ($imptype eq "file") {
     open(IFILE,$htimportloc);
     @implines = <IFILE>;
     close(IFILE);
     foreach $line (@implines) {
       $line =~ s/\n//g;
       $line =~ s/\cM//g;
       push (@batching,$line) if (length($line) > 2);
     }

  }

  $numbatching = @batching;

  &endscript("Nothing found to batch import") if ($numbatching == 0);
  
  open(FILE,$htpasswdloc);
  #flock(FILE,2);
  @USERS = <FILE>;
  close(FILE);

  $counter = @USERS;
  for ($x=0; $x < $counter; $x++) {
    chop($USERS[$x]);
    if (substr($USERS[$x],0,1) ne "#") {
      ($user,$pass) = split (":",$USERS[$x],2);
      $PASSWORDS{$user} = $pass;
    } else {
      $commentline = substr($USERS[$x],1);
      $commentline =~ s/\n//g;
      ($user,$name,$email,$comments,$extra) = split(/\s*\|\s*/,$commentline,5);
      $NAMES{$user} = $name;
      $EMAILS{$user} = $email;
      $COMMENTS{$user} = $ibill;
      $EXTRAS{$user} = $extra;
    }
  }

  foreach $line (@batching) {
    ($user,$password,$name,$email,$comments,$extra) = split(/\s*\,\s*/,$line,6);
    &endscript("Sorry, \"$user\" already exists (nothing imported)") if ($PASSWORDS{$user} ne "");
    $NEWUSERS{$user}++;
    &endscript("Sorry, found duplicate for \"$user\" in your batch (nothing imported)") if ($NEWUSERS{$user} > 1);
    &endscript("Sorry, \"$user\" is an invalid username (nothing imported)") unless ($user =~ /^[A-Z,a-z,0-9,\-,\@,\.,\_]+$/);
    #&endscript("Sorry, \"$user\" has an invalid password (nothing imported)") unless ($password =~ /\S/);
  }
  
  open(PW,">>$htpasswdloc");
  foreach $line (@batching) {
    $line =~ s/\|//g;
    ($user,$password,$name,$email,$comments,$extra) = split(/\s*\,\s*/,$line,6);
    if ($password eq "") {
       $r1 = $letters[int(rand(25))];
       $r2 = $letters[int(rand(25))];
       $r3 = $letters[int(rand(25))];
       $password = "$r1$r2$r3" . int(rand(5000));
    }

    $r1 = $letters[int(rand(25))];
    $r2 = $letters[int(rand(25))];

    $crypted = crypt($password,"$r1$r2");
    print PW "$user:$crypted\n";

    print PW "#$user|$name|$email|$comments|$extra\n";
    if (($FORM{'sendemail'} eq "Y") && ($email =~ /\@/)) {
      if ($FORM{'sendcomment'} eq "Y") {
        &send_email($email,$user,$password,"$comments");
      } else {
        &send_email($email,$user,$password,"");
      }
    }

  }
  close PW;
  

}
####################################################
sub send_email {
  local($uemail,$uname,$upass,$extratext) = @_;

  open(MAIL, "|$mailprog -t") || die "Can't open $mailprog!\n";
  print MAIL "To: $uemail\n";
  print MAIL "From: $emailfrom\n";
  print MAIL "Return-Path: $emailfrom\n";
  print MAIL "Subject: $emailsubject\n\n";
  print MAIL "$emailtop";
  print MAIL " Username : $uname\n";
  print MAIL " Password : $upass\n\n";
  print MAIL "$extratext\n";
  print MAIL "$emailbottom";
  close(MAIL);
}

####################################################
sub endscript {
  local ($str) = @_;

  print " $str <BR> \n";
  exit;

}

#####################################################
#
# Parse Form Data
#
sub parse_form {

   read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
   if (length($buffer) < 5) {
         $buffer = $ENV{QUERY_STRING};
    }
   @pairs = split(/&/, $buffer);
   $morethanone = 0;
   foreach $pair (@pairs) {
      ($name, $value) = split(/=/, $pair);

      $value =~ tr/+/ /;
      $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

      if ($FORM{$name}) {
        $FORM{$name}.= "," . $value;
        $morethanone = 1;
      } else {
        $FORM{$name} = $value;
      }
   }

}

