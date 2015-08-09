#!/usr/local/bin/perl

print "Content-Type: text/html\n\n";
print "Here's an example of a .cgi that proves that .cgi's work on your website!\n\n";
print "The name of this .cgi is test.cgi and its located in your public_html directory\n\n";
$id = `/usr/bin/id`;
chop $id;
print "id -a: $id\n\n";

foreach (keys %ENV) {
	print "$_ = $ENV{$_}<BR>\n";
}


print "<BR><BR><A HREF=\"env.cgi\">EnvCHeck</A><HR>\n";
print "<FORM><INPUT NAME=joe><INPUT TYPE=SUBMIT></FORM>\n";
print `/usr/bin/whoami`;
print `/usr/ucb/whereis sendmail`;
print `/usr/bin/whereis sendmail`;
print `/bin/whereis sendmail`;

#print `/bin/whoami`;
print `whoami`;

print `pwd`;
print `whereis sendmail`;

