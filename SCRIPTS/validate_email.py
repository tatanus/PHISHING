#!/usr/bin/env python

import smtplib
import dns.resolver
import dns.reversename
import socket

MX_RECORD_CACHE = {}

# Attempt to validate that the system can actually communicate with the target MX server
def validate_mx(server, domain):
    try:
        if server in MX_RECORD_CACHE:
            return MX_RECORD_CACHE[server]
        smtp = smtplib.SMTP(timeout=10)
        smtp.connect(server)
        status, _ = smtp.helo()
        if status != 250:
            smtp.quit()
            print "%s answer: %s - %s" % (server, status, _)
        smtp.mail('')
        status, _ = smtp.rcpt("invalid@"+domain)
        if status == 250:
            smtp.quit()
            MX_RECORD_CACHE[server] = True
            return True
        print "%s answer: %s - %s" % (server, status, _)
        smtp.quit()
    except smtplib.SMTPServerDisconnected as e:  # Server not permits verify user
        print "%s disconnected. [%s]" % (server, e)
    except smtplib.SMTPConnectError as e:
        print "Unable to connect to %s. [%s]" % (server, e)
    except socket.timeout as e:
        print "Timedout connecting to %s. [%s]" % (server, e)
    MX_RECORD_CACHE[server] = False
    return False        

# Lookup a domain and get its mailserver
def get_mx_records(domain):
    records = dns.resolver.query(domain, 'MX')
    hosts = []
    for rdata in records:
        if (validate_mx((str(rdata.exchange))[:-1], domain)):
            hosts.append((str(rdata.exchange))[:-1])
    return hosts
    
# Lookup a domain and get its mailserver
def get_mx_record(domain):
    hosts = get_mx_records(domain)
    if (hosts):
        return hosts[0]
    else:
        return None

# validate email address by connecting to remote SMTP server
def validate_email_address(email_to, email_from, debug=False):
    # find the appropiate mail server
    domain = email_to.split('@')[1]
    remote_server = get_mx_record(domain)

    if (remote_server == None):
        print "No valid email server could be found for [%s]!" % (email_to)
        return False

    # Login into the mail exchange server
    try:
        smtp = smtplib.SMTP()
        smtp.connect(remote_server)
        if debug:
            smtp.set_debuglevel(True)
    except smtplib.SMTPConnectError, e:
        print e
        return False
 
    try:
        smtp.ehlo_or_helo_if_needed()
    except Exception, e:
        print e
        return False
 
    # First Try to verify with VRFY
    # 250 is success code. 400 or greater is error.
    v_code, v_message = smtp.verify(email_to)
    if v_code and v_code != 250:
        f_code, f_message = smtp.mail(email_from)
        # Then use RCPT to verify
        if f_code and f_code == 250:
            r_code, r_message = smtp.rcpt(email_to)
            if r_code and r_code == 250:
                return True, r_message
            if r_code and r_code == 550:
                return False, r_message
        else:
            return False
    else:
        return True, v_message

    smtp.quit()
    return False

if __name__ == "__main__":
    FROM_ADDRESS = ""
    TO_ADDRESS = ""
    print validate_email_address(TO_ADDRESS, FROM_ADDRESS, debug=False)
