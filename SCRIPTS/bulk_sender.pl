use strict;
use warnings;

use Email::Sender::Simple qw(sendmail);
use Email::Sender::Transport::SMTP ();
use Email::Simple ();
use Email::Simple::Creator ();
use Try::Tiny;
use Getopt::Std;
use Config::Simple;

sub do_help {
  print "\n";
  print "Usage: bulk_email.pl -c <config file> -t <targets file> -b <email body file> [-v|-h]\n";
  print "                -c <file> = File containing SMTP config information\n";
  print "                -t <file> = File containing phishing targets\n";
  print "                -b <file> = File containing the body of the phishing email\n";
  print "                -v        = Verbose output\n";
  print "                -h        = This help message\n";
  print "\n\n";
  exit 0;
}

my $body_file = '';
my $config_file = '';
my $target_file = '';
my $verbose;
my @targets;
my $body = '';
my $sleep = 10;

my %options=();
getopts("c:t:b:vh", \%options);
$config_file = $options{c} if defined $options{c};
$target_file = $options{t} if defined $options{t};
$body_file = $options{b} if defined $options{b};
$verbose = 1 if defined $options{v};
do_help() if defined $options{h};

if (($body_file eq '') || ($config_file eq '') || ($target_file eq '')) {
  do_help();
}

#read in targets
open FILE, $target_file or die "Couldn't open file: $!"; @targets = <FILE>; close FILE;

#read in body
open FILE, $body_file or die "Couldn't open file: $!"; 
while (<FILE>){ $body .= $_; } close FILE;

#read in config
my $cfg = new Config::Simple($config_file);
my $smtpserver = $cfg->param('SMTPSERVER');
my $smtpport = $cfg->param('SMTPPORT');
my $smtpuser   = $cfg->param('USER');
my $smtppassword = $cfg->param('PASSWORD');
my $fromemail = $cfg->param('FROM');
my $subject = $cfg->param('SUBJECT');
$sleep = $cfg->param('SLEEP');

#my $transport = Email::Sender::Transport::SMTP->new({
#  host => $smtpserver,
#  port => $smtpport,
#  sasl_username => $smtpuser,
#  sasl_password => $smtppassword,
#});

foreach (@targets) {
my $transport = Email::Sender::Transport::SMTP->new({
  host => $smtpserver,
  port => $smtpport,
});
  print "\nSleeping for [$sleep] seconds between sending emails.\n" if $verbose;
#  sleep($sleep);
  chomp;
  my $line = $_;
  my @parts = split(',',$line);
  my $body_temp = $body;

  my $email = $parts[0];
  if ($email eq "") {
    print "\n[-] ERROR:: Could not identify email address in line [$line]\n";
    next;
  } 

  print "\n[ ] Building email for [$email]...\n";

  my $fname = $parts[1];
  my $lname = $parts[2];

  if ( !defined($fname)) { $fname = ""; }
  if ( !defined($lname)) { $lname = ""; }

  if ($body =~ m/<FNAME>/) {
    if ($fname eq "") {
      print "[-] ERROR:: Could not identify <FNAME> value for Search Replace in message body\n";
      next;
    }
    $body_temp =~ s/<FNAME>/$fname/g;
  }

  if ($body =~ m/<LNAME>/) {
    if ($lname eq "") {
      print "[-] ERROR:: Could not identify <LNAME> value for Search Replace in message body\n";
      next;
    }
    $body_temp =~ s/<LNAME>/$lname/g;
  }

  my $email_message = Email::Simple->create(
    header => [
      To      => $email,
      From    => $fromemail,
      Subject => $subject,
    ],
    body => $body_temp,
  );

  print "[ ] Sending Email...\n" if $verbose;
  try {
    sendmail($email_message, { transport => $transport });
  } catch {
    print "[-] ERROR:: $_\n";
  };
}
print "\n";
