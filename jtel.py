import json, struct, time, argparse, re, socket, sys
from telnetlib import Telnet, IAC, DO, DONT, WILL, WONT, SB, SE, TTYPE
from . import settings


# Configuration
TELNET_TIMEOUT = 5  # reasonable value for intranet.
###############################################################################
#                            Other settings                                    #
################################################################################
STANDARD_PROMPT = 'jcli : '  # There should be no need to change this
INTERACTIVE_PROMPT ='> '  # Prompt for interactive commands

class jCliSessionError(Exception):
    pass

class jCliKeyError(Exception):
    pass

class Jptelnet(object):

    def __init__(self):
        self.host = settings.JASMIN_HOST
        self.port = settings.JASMIN_PORT
        self.username = settings.JASMIN_USER
        self.password = settings.JASMIN_PWD
        self.tn = None
        
    def got_connection(self):
        self.jcli = {'host': self.host,
                    'port': self.port,
                    'username': self.username,
                    'password': self.password}

        self.outcome = None
        try:
            self.tn = Telnet(self.jcli['host'], self.jcli['port'])
            self.tn.set_option_negotiation_callback(self.process_option)
            self.tn.read_until(b"Authentication required.", 16)
            self.tn.write(b"\r\n")
            self.tn.read_until(b"Username:", 16)
            self.tn.write(self.jcli['username'].encode('ascii') +b"\r\n")
            self.tn.read_until(b"Password:", 16)
            self.tn.write(self.jcli['password'].encode('ascii') +b"\r\n")
                
        # We must be connected
            
            idx, obj, response = self.tn.expect([rb'Welcome to Jasmin ([0-9a-z\.]+) console'], 16)
            if idx == -1:
                return (0)
            else:
            # Wait for prompt
                self.wait_for_prompt()
        except jCliSessionError as e:
            print('Exception in got connection', e)
            return(0)
        return(self.tn)
    
    def process_option(self, tn, command, option):
        if command == DO and option == TTYPE:
            tn.sendall(IAC + WILL + TTYPE)
            #print( 'Sending terminal type "mypython"')
            tn.sendall(IAC + SB + TTYPE + '\0' + 'mypython' + IAC + SE)
        elif command in (DO, DONT):
            #print ('Will', ord(option))
            tn.sendall(IAC + WILL + option)
        elif command in (WILL, WONT):
            #print ('Do', ord(option))
            tn.sendall(IAC + DO + option)
    
    def wait_for_prompt(self, command = None, prompt = rb'jcli :', to = 20):
        """Will  send 'command' (if set) and wait for prompt
        Will raise an exception if 'prompt' is not obtained after 'to' seconds
        """

        if command is not None:
            self.tn.write(command)

        idx, obj, response = self.tn.expect([prompt], to)
        if idx == -1:
            if command is None:
                raise jCliSessionError('Did not get prompt (%s)' % prompt)
            else:
                raise jCliSessionError('Did not get prompt (%s) for command (%s)' % (prompt, command))
        else:
            return response
    
    def interceptor(self,data):
        response=None
        try:
            direction = data[0]
            i_type = data[1]
            order = data[2]
            script = data[3]
            filters = data[4]
            self.tn = self.got_connection()

        except Exception:
            raise MissingKeyError('Missing parameter: Action required')
        
        if direction == 'mt': #its an mt interceptor
            if i_type == 'StaticMTInterceptor':
                self.tn.write(b"mtinterceptor -a\r\n")
                self.tn.write(b"type "+ i_type.encode() +b"\r\n")
                self.tn.write(b"order "+ order.encode() +b"\r\n")
                self.tn.write(b"script "+ script.encode() +b"\r\n")
                self.tn.write(b"filters "+ filters.encode() +b"\r\n")
                resp = self.wait_for_prompt(command = b"ok\r\n")
                if b'Successfully' in resp:
                    response= self.tn.write(b"persist a\r\n")
                else:
                    self.tn.write(b"ko\r\n")
                    response = resp.decode('ascii')    
            
            elif i_type == 'remove':
                resp = self.wait_for_prompt(command=b"mtinterceptor -r "+ order.encode() +b"\r\n")
                if b'Successfully' in resp:
                    response= self.tn.write(b"persist a\r\n")
                else:
                    self.tn.write(b"ko\r\n")
                    response = resp.decode('ascii')    
            
            elif i_type == 'flush':
                resp = self.wait_for_prompt(command=b"mtinterceptor -f\r\n")
                if b'Successfully' in resp:
                    response= self.tn.write(b"persist a\r\n")
                else:
                    self.tn.write(b"ko\r\n")
                    response = resp.decode('ascii')    
            else:
                self.tn.write(b"mtinterceptor -a\r\n")
                self.tn.write(b"type "+ i_type.encode() +b"\r\n")
                self.tn.write(b"script "+ script.encode() +b"\r\n")
                resp = self.wait_for_prompt(command=b"ok\r\n")
                if b'Successfully' in resp:
                    response= self.tn.write(b"persist a\r\n")
                else:
                    self.tn.write(b"ko\r\n")
                    response = resp.decode('ascii')    
            if self.tn is not None and self.tn.get_socket():
                self.tn.close()
            return response
        else:   #its an mo interceptor
            if i_type == 'StaticMOInterceptor':
                self.tn.write(b"mointerceptor -a\r\n")
                self.tn.write(b"type "+ i_type.encode() +b"\r\n")
                self.tn.write(b"order "+ order.encode() +b"\r\n")
                self.tn.write(b"script "+ script.encode() +b"\r\n")
                self.tn.write(b"filters "+ filters.encode() +b"\r\n")
                resp = self.wait_for_prompt(command=b"ok\r\n")
                if b'Successfully' in resp:
                    response= self.tn.write(b"persist a\r\n")
                else:
                    self.tn.write(b"ko\r\n")
                    response = resp.decode('ascii')    
                
            elif i_type == 'remove':
                resp = self.wait_for_prompt(command=b"mointerceptor -r "+ order.encode()  +b"\r\n")
                if b'Successfully' in resp:
                    response= self.tn.write(b"persist a\r\n")
                else:
                    self.tn.write(b"ko\r\n")
                    response = resp.decode('ascii')    
            
            elif i_type == 'flush':
                resp = self.wait_for_prompt(command=b"mointerceptor -f\r\n")
                if b'Successfully' in resp:
                    response= self.tn.write(b"persist a\r\n")
                else:
                    self.tn.write(b"ko\r\n")
                    response = resp.decode('ascii')    
                
            else:
                self.tn.write(b"mointerceptor -a\r\n")
                self.tn.write(b"type "+ i_type.encode() +b"\r\n")
                self.tn.write(b"script "+ script.encode() +b"\r\n")

                resp = self.wait_for_prompt(command=b"ok\r\n")
                if b'Successfully' in resp:
                    response= self.tn.write(b"persist a\r\n")
                else:
                    self.tn.write(b"ko\r\n")
                    response = resp.decode('ascii')    
            
            if self.tn is not None and self.tn.get_socket():
                self.tn.close()
            return response
    
    def stats(self,data):
        result = None
        try:
            action = data[0]
            self.tn = self.got_connection()

        except Exception:
            raise MissingKeyError('Missing parameter: Action required')

        if action == 'user':    # Show user stats using it’s UID
            usr = data[1]
            response = self.wait_for_prompt(command = b"stats --user=" + usr.encode() +b"\r\n")
            result = response.decode('ascii').strip().replace("\r", '').split("\n") #splitlines()
            
        elif action == 'users':    #Show stats for all users
            response = self.wait_for_prompt(command = b"stats --users\r\n")
            result = response.decode('ascii').strip().replace("\r", '').split("\n")

        elif action == 'smppc':    #Show smpp connector stats using it’s CID
            cid = data[1]
            response = self.wait_for_prompt(command = b"stats --smppc=" + cid.encode() +b"\r\n")
            result = response.decode('ascii').strip().replace("\r", '').split("\n") #splitlines()

        elif action == 'smppcs':    #Show all smpp connectors stats
            response = self.wait_for_prompt(command = b"stats --smppcs\r\n")
            result = response.decode('ascii').strip().replace("\r", '').split("\n")

        elif action == 'smppsapi':    #Show SMPP Server API stats
            response = self.wait_for_prompt(command = b"stats --smppsapi\r\n")
            result = response.decode('ascii').strip().replace("\r", '').split("\n")

        elif action == 'httpapi':    #Show HTTP stats
            response = self.wait_for_prompt(command = b"stats --httpapi\r\n")
            result = response.decode('ascii').strip().replace("\r", '').split("\n")
            
        else:
            result = 'Unknown stats type'
        
        if self.tn is not None and self.tn.get_socket():
            self.tn.close()
        return result

    def morouter(self,data):
        response=None
        try:
            action = data[0]
            self.tn = self.got_connection()

        except Exception:
            raise MissingKeyError('Missing parameter: Action required')
        if action == 'StaticMORoute':    # 1 connector many filters
            types = action
            order = data[1]
            connector = data[2]
            filters = data[3]

            self.tn.write(b"morouter -a\r\n")
            self.tn.write(b"type "+ types.encode() +b"\r\n")
            self.tn.write(b"order "+ order.encode() +b"\r\n")
            self.tn.write(b"connector "+ connector.encode() +b"\r\n")
            self.tn.write(b"filters "+ filters.encode() +b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        elif action == 'RandomRoundrobinMORoute':
            types = action
            order = data[1]
            connector = data[2]
            filt = data[3]
            filters = filt
            self.tn.write(b"morouter -a\r\n")
            self.tn.write(b"type "+ types.encode() +b"\r\n")
            self.tn.write(b"order "+ order.encode() +b"\r\n")
            self.tn.write(b"connectors "+ connector.encode() +b"\r\n")
            self.tn.write(b"filters "+ filters.encode() +b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        elif action == 'FailoverMORoute':
            types = action
            order = data[1]
            connector = data[2]
            filt = data[3]
            filters = filt
            self.tn.write(b"morouter -a\r\n")
            self.tn.write(b"type "+ types.encode() +b"\r\n")
            self.tn.write(b"order "+ order.encode() +b"\r\n")
            self.tn.write(b"connectors "+ connector.encode() +b"\r\n")
            self.tn.write(b"filters "+ filters.encode() +b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        elif action == 'DefaultRoute':
            types = action
            connector = data[1]
            self.tn.write(b"morouter -a\r\n")
            self.tn.write(b"type "+ types.encode() +b"\r\n")
            self.tn.write(b"connector "+ connector.encode() +b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        elif action == 'remove':
            route = data[1]
            resp = self.wait_for_prompt(command=b"morouter -r " + route.encode() +b"\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
        
        elif action == 'flush':
            resp = self.wait_for_prompt(command=b"morouter -f \r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
        else:
            response = 'Invalid MO router optoin'
        if self.tn is not None and self.tn.get_socket():
            self.tn.close()
        return response

    def mtrouter(self,data):
        response=None
        try:
            action = data[0]
            self.tn = self.got_connection()
        except Exception:
            raise MissingKeyError('Missing parameter: Action required')
        if action == 'StaticMTRoute':    # 1 connector many filters
            types = action
            order = data[1]
            connector = data[2]
            filt = data[3]
            filters = filt[:-1]
            rate = data[4]
            self.tn.write(b"mtrouter -a\r\n")
            self.tn.write(b"type "+ types.encode()+ b"\r\n")
            self.tn.write(b"order "+ order.encode() +b"\r\n")
            self.tn.write(b"connector "+ connector.encode() +b"\r\n")
            self.tn.write(b"filters "+ filters.encode() +b"\r\n")
            self.tn.write(b"rate "+ rate.encode() +b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        elif action == 'RandomRoundrobinMTRoute':
            types = action
            order = data[1]
            connector = data[2]
            filt = data[3]
            filters = filt
            print('Filters', filters)
            rate = data[4]
            self.tn.write(b"mtrouter -a\r\n")
            self.tn.write(b"type "+ types.encode() +b"\r\n")
            self.tn.write(b"order "+ order.encode() +b"\r\n")
            self.tn.write(b"connectors "+ connector.encode() +b"\r\n")
            self.tn.write(b"filters "+ filters.encode() +b"\r\n")
            self.tn.write(b"rate "+ rate.encode() +b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        elif action == 'FailoverMTRoute':
            types = action
            order = data[1]
            connector = data[2]
            filt = data[3]
            filters = filt
            rate = data[4]
            self.tn.write(b"mtrouter -a\r\n")
            self.tn.write(b"type "+ types.encode() +b"\r\n")
            self.tn.write(b"order "+ order.encode() +b"\r\n")
            self.tn.write(b"connectors "+ connector.encode() +b"\r\n")
            self.tn.write(b"filters "+ filters.encode() +b"\r\n")
            self.tn.write(b"rate "+ rate.encode() +b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        elif action == 'DefaultRoute':
            types = action
            connector = data[1]
            rate = data[2]
            self.tn.write(b"mtrouter -a\r\n")
            self.tn.write(b"type "+ types.encode() +b"\r\n")
            self.tn.write(b"connector "+ connector.encode() +b"\r\n")
            self.tn.write(b"rate "+ rate.encode() + b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')

        elif action == 'remove':
            route = data[1]
            resp = self.wait_for_prompt(command = b"mtrouter -r " + route.encode() +b"\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
           
        elif action == 'flush':
            resp = self.wait_for_prompt(command=b"mtrouter -f\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
        else:
            response = 'Invalid action for router'
        if self.tn is not None and self.tn.get_socket():
            self.tn.close()
        return response

    def filters(self,data):
        response=None
        try:
            action = data[0]
            self.tn = self.got_connection()
        except Excebption:
            raise MissingKeyError('Missing parameter: Action required')

        if action == 'delete':
            filter = data[1]
            resp = self.wait_for_prompt(command=b"filter -r" + filter.encode() +b"\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')

        elif action == 'create':
            fid = data[1].encode()
            ft = data[2]
            ftype = data[2].encode()
            fval = data[3].encode()
            if ft == 'TransparentFilter':
                self.tn.write(b"filter -a\r\n")
                self.tn.write(b"fid " + fid +b"\r\n")
                self.tn.write(b"type " + ftype +b"\r\n")
                resp = self.wait_for_prompt(command = b"ok\r\n")
                if b'Successfully' in resp:
                    response=self.tn.write(b"persist a\r\n")
                else:
                    response = resp.decode('ascii')

            elif ft == 'ShortMessageFilter':
                self.tn.write(b"filter -a\r\n")
                self.tn.write(b"fid " + fid+ b"\r\n")
                self.tn.write(b"type " + ftype +b"\r\n")
                self.tn.write(b"short_message " + fval +b"\r\n")
                resp = self.wait_for_prompt(command = b"ok\r\n")
                if b'Successfully' in resp:
                    response=self.tn.write(b"persist a\r\n")
                else:
                    response = resp.decode('ascii')

            elif ft == 'DateIntervalFilter':
                self.tn.write(b"filter -a\r\n")
                self.tn.write(b"fid " + fid + b"\r\n")
                self.tn.write(b"type " + ftype +b"\r\n")
                self.tn.write(b"dateInterval " + fval+ b"\r\n")
                resp = self.wait_for_prompt(command = b"ok\r\n")
                if b'Successfully' in resp:
                    response=self.tn.write(b"persist a\r\n")
                else:
                    response = resp.decode('ascii')

            elif ft == 'TimeIntervalFilter':
                self.tn.write(b"filter -a\r\n")
                self.tn.write(b"fid " + fid + b"\r\n")
                self.tn.write(b"type " + ftype +b"\r\n")
                self.tn.write(b"timeInterval " + fval +b"\r\n")
                resp = self.wait_for_prompt(command = b"ok\r\n")
                if b'Successfully' in resp:
                    response=self.tn.write(b"persist a\r\n")
                else:
                    response = resp.decode('ascii')

            elif ft == 'TagFilter':
                self.tn.write(b"filter -a\r\n")
                self.tn.write(b"fid " + fid +b"\r\n")
                self.tn.write(b"type " + ftype +b"\r\n")
                self.tn.write(b"tag " + fval +b"\r\n")
                resp = self.wait_for_prompt(command = b"ok\r\n")
                if b'Successfully' in resp:
                    response=self.tn.write(b"persist a\r\n")
                else:
                    response = resp.decode('ascii')

            elif ft == 'EvalPyFilter':
                self.tn.write(b"filter -a\r\n")
                self.tn.write(b"fid " + fid +b"\r\n")
                self.tn.write(b"type " + ftype +b"\r\n")
                self.tn.write(b"uid " + fval+ b"\r\n")
                resp = self.wait_for_prompt(command = b"ok\r\n")
                if b'Successfully' in resp:
                    response=self.tn.write(b"persist a\r\n")
                else:
                    response = resp.decode('ascii')
            elif ft == 'UserFilter':
                self.tn.write(b"filter -a\r\n")
                self.tn.write(b"fid " + fid +b"\r\n")
                self.tn.write(b"type " + ftype+b"\r\n")
                self.tn.write(b"uid " + fval+ b"\r\n")
                resp = self.wait_for_prompt(command = b"ok\r\n")
                if b'Successfully' in resp:
                    response=self.tn.write(b"persist a\r\n")
                else:
                    response = resp.decode('ascii')

            elif ft == 'DestinationAddrFilter':
                self.tn.write(b"filter -a\r\n")
                self.tn.write(b"fid "+ fid +b"\r\n")
                self.tn.write(b"type "+ ftype +b"\r\n")
                self.tn.write(b"destination_addr "+ fval +b"\r\n")
                resp = self.wait_for_prompt(command = b"ok\r\n")
                if b'Successfully' in resp:
                    response=self.tn.write(b"persist a\r\n")
                else:
                    response = resp.decode('ascii')

            elif ft == 'GroupFilter':
                self.tn.write(b"filter -a\r\n")
                self.tn.write(b"fid "+ fid +b"\r\n")
                self.tn.write(b"type "+ ftype +b"\r\n")
                self.tn.write(b"gid "+ fval +b"\r\n")
                self.tn.write(b"ok\r\n")
                resp = self.wait_for_prompt(command = b"ok\r\n")
                if b'Successfully' in resp:
                    response=self.tn.write(b"persist a\r\n")
                else:
                    response = resp.decode('ascii')

            elif ft == 'SourceAddrFilter':
                self.tn.write(b"filter -a\r\n")
                self.tn.write(b"fid "+ fid +b"\r\n")
                self.tn.write(b"type "+ ftype +b"\r\n")
                self.tn.write(b"source_addr "+ fval +b"\r\n")
                resp = self.wait_for_prompt(command = b"ok\r\n")
                if b'Successfully' in resp:
                    response=self.tn.write(b"persist a\r\n")
                else:
                    response = resp.decode('ascii')
        else:
            if self.tn is not None and self.tn.get_socket():
                self.tn.close()
                return response
        return()

    def http_cons(self,data):
        response=None
        try:
            action = data[0]
            self.tn = self.got_connection()
        except Exception:
            raise MissingKeyError('Missing parameter: Action required')
        if action == 'create':
            cid = data[1]
            method = data[2]
            base_url=data[3]
            self.tn.write(b"httpccm -a\r\n")
            self.tn.write(b"cid " + cid.encode()+b"\r\n")
            self.tn.write(b"method " + method.encode()+b"\r\n")
            self.tn.write(b"url " + base_url.encode()+b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        elif action == 'remove':
            cid = data[1]
            resp = self.wait_for_prompt(command = b"httpccm -r " + cid.encode() +b"\r\n")
            if b'Successfully' in resp:
                response=self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')

        elif action == 'update':
            response = self.wait_for_prompt(command = b"httpccm -u " + cid.encode() +b"\r\n")
        else:
            reponse = 'Invalid option for HTTP connectors'
        
        if self.tn is not None and self.tn.get_socket():
            self.tn.close()
        return response
    
    def list_it(self, list_type=None):  
        result = None
        self.tn = self.got_connection()
        try:
            if list_type == 'smppcs':
                response = self.wait_for_prompt(command = b"smppccm -l\r\n")
                result = response.decode('ascii').strip().replace("\r", '').split("\n") #splitlines()
                
            elif list_type == 'imos':
                response = self.wait_for_prompt(self.tn, command = "mointerceptor -l\r\n")
                result = response.strip().replace("\r", '').split("\n") #splitlines()
                
            elif list_type == 'imts':
                response = self.wait_for_prompt(command = b"mtinterceptor -l\r\n")
                result = response.decode('ascii').strip().replace("\r", '').split("\n") #splitlines()
                
            elif list_type == 'httpcs':
                response = self.wait_for_prompt(command = b"httpccm -l\r\n")
                result = response.decode('ascii').strip().replace("\r", '').split("\n") #splitlines()
                
            elif list_type == 'mtrouter':
                response = self.wait_for_prompt(command = b"mtrouter -l\r\n")
                result = response.decode('ascii').strip().replace("\r", '').split("\n") #splitlines()
                
            elif list_type == 'morouter':
                response = self.wait_for_prompt(command = b"morouter -l\r\n")
                result = response.decode('ascii').strip().replace("\r", '').split("\n") #splitlines()
                
            elif list_type == 'filters':
                response = self.wait_for_prompt(command = b"filter -l\r\n")
                result = response.decode('ascii').strip().replace("\r", '').split("\n") #splitlines()
                
            elif list_type == 'users':
                response = self.wait_for_prompt(command =  b"user -l\r\n")
                result = response.decode('ascii').strip().replace("\r", '').split("\n") #splitlines()
                
            elif list_type == 'groups':
                response = self.wait_for_prompt(command = b"group -l\r\n")
                result = response.decode('ascii').strip().replace("\r", '').split("\n") #splitlines()
                
            elif list_type == 'httpapi':
                result  = self.get_list_ids(response)
            
            elif list_type == 'smppsapi':
                users = self.get_smppsapi_stats(response)
                result['data'].append({'{#Stats}': stats})

        except Exception as e:
            if result is not None:
                print (e)
            if self.tn is not None and self.tn.get_socket():
                self.tn.close()
                return result
            
        if self.tn is not None and self.tn.get_socket():
            self.tn.close()
        return result
 
    def connector(self,data):
        response=None
        try:
            action = data[0]
            self.tn = self.got_connection()

        except Exception:
            raise MissingKeyError('Missing parameter: Action required')

        if action == 'start':
            cid = data[1]
            resp = self.wait_for_prompt(command=b"smppccm -1 " + cid.encode() +b"\r\n")
            if b'Successfully' in resp:
                response = self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        elif action == 'stop':
            cid = data[1]
            resp = self.wait_for_prompt(b"smppccm -0 " + cid.encode() +b"\r\n")
            if b'Successfully' in resp:
                response = self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        elif action == 'remove':
            cid = data[1]
            resp =self.wait_for_prompt(command=b"smppccm -r " + cid.encode() +b"\r\n")
            if b'Successfully' in resp:
                response = self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        elif action == 'show':
            cid = data[1]
            resp = self.wait_for_prompt(command = b"smppccm -s " + cid.encode() +b"\r\n")
            response = resp.decode('ascii').strip().replace("\r", '').split("\n") #splitlines()
            
        elif action == 'update':
            ripf = data[2]
            con_fail_delay= data[3]
            dlr_expiry= data[4]
            coding= data[5]
            logrotate= data[6]
            submit_throughput= data[7]
            elink_interval= data[8]
            bind_to= data[9]
            port= data[10]
            con_fail_retry= data[11]
            password= data[12]
            src_addr= data[13]
            bind_npi= data[14]
            addr_range= data[15]
            dst_ton= data[16]
            res_to= data[17]
            def_msg_id= data[18]
            priority= data[19]
            con_loss_retry= data[20]
            username= data[21]
            dst_npi= data[22]
            validity= data[23]
            requeue_delay= data[24]
            host= data[25]
            src_npi= data[26]
            trx_to= data[27]
            logfile= data[28]
            ssl = data[29]
            loglevel= data[30]
            bind= data[31]
            proto_id= data[32]
            dlr_msgid= data[33]
            con_loss_delay= data[34]
            bind_ton= data[35]
            pdu_red_to= data[36]
            src_ton= data[37]
            cid = data[1]
            self.tn.write(b"smppccm -u " + cid.encode() +b"\r\n")
            self.tn.write(b"bind " + bind.encode() +b"\r\n")
            
            self.tn.write(b"ripf " + ripf.encode()  +b"\r\n")
            self.tn.write(b"con_fail_delay " + con_fail_delay.encode() +b"\r\n")
            self.tn.write(b"dlr_expiry " + dlr_expiry.encode() +b"\r\n")
            self.tn.write(b"coding " + coding.encode() +b"\r\n")
            self.tn.write(b"logrotate " + logrotate.encode() +b"\r\n")
            self.tn.write(b"submit_throughput " + submit_throughput.encode() +b"\r\n")
            self.tn.write(b"elink_interval " + elink_interval.encode() +b"\r\n")
            self.tn.write(b"bind_to " + bind_to.encode() +b"\r\n")
            self.tn.write(b"port " + port.encode() +b"\r\n")
            self.tn.write(b"con_fail_retry " + con_fail_retry.encode() +b"\r\n")
            self.tn.write(b"password " + password.encode() +b"\r\n")
            self.tn.write(b"src_addr " + src_addr.encode() +b"\r\n")
            
            self.tn.write(b"bind_npi " + bind_npi.encode() +b"\r\n")
            self.tn.write(b"addr_range " + addr_range.encode() +b"\r\n")
            self.tn.write(b"dst_ton " + dst_ton.encode() +b"\r\n")
            self.tn.write(b"res_to " + res_to.encode() +b"\r\n")
            self.tn.write(b"def_msg_id " + def_msg_id.encode() +b"\r\n")
            
            self.tn.write(b"priority " + priority.encode() +b"\r\n")
            self.tn.write(b"con_loss_retry " +con_loss_retry.encode() +b"\r\n")
            self.tn.write(b"username " + username.encode() +b"\r\n")
            self.tn.write(b"dst_npi " + dst_npi.encode() +b"\r\n")
            self.tn.write(b"validity " + validity.encode() +b"\r\n")
            self.tn.write(b"requeue_delay " + requeue_delay.encode() +b"\r\n")
            
            self.tn.write(b"host " + host.encode() +b"\r\n")
            self.tn.write(b"src_npi " + src_npi.encode() +b"\r\n")
            self.tn.write(b"trx_to " + trx_to.encode() +b"\r\n")
            self.tn.write(b"logfile " + logfile.encode() +b"\r\n")
            self.tn.write(b"ssl " + ssl.encode() +b"\r\n")
            self.tn.write(b"loglevel " + loglevel.encode() +b"\r\n")
            
            self.tn.write(b"proto_id " + proto_id.encode() +b"\r\n")
            self.tn.write(b"dlr_msgid " + dlr_msgid.encode() +b"\r\n")
            self.tn.write(b"con_loss_delay " + con_loss_delay.encode() +b"\r\n")
            
            self.tn.write(b"bind_ton " + bind_ton.encode() +b"\r\n")
            self.tn.write(b"pdu_red_to " + pdu_red_to.encode() +b"\r\n")
            self.tn.write(b"src_ton " + src_ton.encode() +b"\r\n")
            resp = self.wait_for_prompt(command=b"ok\r\n")
            if b'Successfully' in resp:
                response = self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    
            
        elif action == 'create':
            cid = data[1]
            username = data[2]
            password = data[3]
            host = data[4]
            port = data[5]
            submit_throughput = data[6]
            self.tn.write(b"smppccm -a\r\n")
            self.tn.write(b"cid " + cid.encode() +b"\r\n")
            self.tn.write(b"username " + username.encode() +b"\r\n")
            self.tn.write(b"password " + password.encode() +b"\r\n")
            self.tn.write(b"host " + host.encode() +b"\r\n")
            self.tn.write(b"port " + port.encode() +b"\r\n")
            self.tn.write(b"submit_throughput " + submit_throughput.encode() +b"\r\n")
            resp = self.wait_for_prompt(command=b"ok\r\n")
            if b'Successfully' in resp:
                response = self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    
        else:
            response = 'Invalid fucntion for connectors'
        if self.tn is not None and self.tn.get_socket():
                self.tn.close()
        return response

    def users (self,data): #User and Group Management
        response=None
        try:
            action = data[0]
            self.tn = self.got_connection()
        except Exception:
            raise MissingKeyError('Missing parameter: Action required')
        
        types = 'users'
        if action == 'update':
            juser=data[1]
            default_src_addr=data[2]
            quota_http_throughput=data[3]
            quota_balance=data[4]
            quota_smpps_throughput=data[5]
            quota_sms_count=data[6]
            quota_early_percent=data[7]
            value_priority=data[8]
            value_content=data[9]
            value_src_addr=data[10]
            value_dst_addr=data[11]
            value_validity_period=data[12]
            author_http_send=data[13]
            author_http_dlr_method=data[14]
            author_http_balance=data[15]
            author_smpps_send=data[16]
            author_priority=data[17]
            author_http_long_content=data[18]
            author_src_addr=data[19]
            author_dlr_level=data[20]
            author_http_rate=data[21]
            author_validity_period=data[22]
            author_http_bulk=data[23]
            self.tn.write(b"user -u " + juser.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred defaultvalue src_addr " + default_src_addr.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred quota http_throughput " + quota_http_throughput.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred quota balance " + quota_balance.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred quota smpps_throughput " + quota_smpps_throughput.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred quota sms_count " + quota_sms_count.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred quota early_percent " + quota_early_percent.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred valuefilter priority " + value_priority.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred valuefilter content " + value_content.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred valuefilter src_addr " + value_src_addr.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred valuefilter dst_addr " + value_dst_addr.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred valuefilter validity_period " + value_validity_period.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred authorization http_send " + author_http_send.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred authorization http_dlr_method " + author_http_dlr_method.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred authorization http_balance " + author_http_balance.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred authorization smpps_send " + author_smpps_send.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred authorization priority " + author_priority.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred authorization http_long_content " + author_http_long_content.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred authorization src_addr " + author_src_addr.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred authorization dlr_level " + author_dlr_level.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred authorization http_rate " + author_http_rate.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred authorization validity_period " + author_validity_period.encode() +b"\r\n")
            self.tn.write(b"mt_messaging_cred authorization http_bulk " + author_http_bulk.encode() +b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response= self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    

        elif action == 'unbind':
            uid = data[1]
            resp = self.wait_for_prompt(command=b"user --smpp-unbind=" +uid.encode() +b"\r\n")
            if b'Successfully' in resp:
                response= self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    

        elif action=='ban':
            uid = data[1]
            resp = self.wait_for_prompt(command=b"user --smpp-ban=" +uid.encode() +b"\r\n")
            print('RESP in ban', resp)
            if b'Successfully' in resp:
                response= self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    

        elif action=='create_user':
            uid = data[1]
            username = data[2]
            password = data[3]
            gid = data[4]

            self.tn.write(b"user -a\r\n")
            self.tn.write(b"uid "+ uid.encode() +b"\r\n")
            self.tn.write(b"gid "+ gid.encode() +b"\r\n")
            self.tn.write(b"username "+ username.encode() +b"\r\n")
            self.tn.write(b"password "+ password.encode() +b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response= self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    

        elif action=='get_creds':
            uid = data[1]
            response = self.wait_for_prompt(command =  b"user -s" + uid.encode() +b"\r\n")
            result = response.decode('ascii').strip().replace("\r", '').split("\n")
            return result    
            
        elif action == 'create_group':
            gid = data[1]
            self.tn.write(b"group -a\r\n")
            self.tn.write(b"gid "+ str.encode(gid)+b"\r\n")
            resp = self.wait_for_prompt(command = b"ok\r\n")
            if b'Successfully' in resp:
                response= self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    
            
        elif action == 'enable_user':
            user = data[1]
            resp = self.wait_for_prompt(command = b"user -e" + user.encode() +b"\r\n")
            if b'Successfully' in resp:
                response= self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    
           
        elif action == 'enable_group':
            grp = data[1]
            resp = self.wait_for_prompt(command = b"group -e" + grp.encode() +b"\r\n")
            if b'Successfully' in resp:
                response= self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    
           
        elif action == 'disable_user':
            user = data[1]
            resp = self.wait_for_prompt(command = b"user -d" + user.encode()+b"\r\n")
            if b'Successfully' in resp:
                response= self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    
           
        elif action=='disable_group':
            grp = data[1]
            resp = self.wait_for_prompt(command = b"group -d" + grp.encode()+b"\r\n")
            if b'Successfully' in resp:
                response= self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    
           
        elif action == 'remove_user':
            outcome = None
            user = data[1]
            resp = self.wait_for_prompt(command = b"user -r" + user.encode() +b"\r\n")
            if b'Successfully' in resp:
                response= self.tn.write(b"persist a\r\n")
            else:
                response = resp.decode('ascii')    
          
        elif action == 'remove_group':
            grp = data[1]
            resp = self.wait_for_prompt(command = b"group -r" + grp.encode() +b"\r\n")
            if b'Successfully' in resp:
                response = self.wait_for_prompt(command = b"persist a\r\n")
            else:
                response = resp.decode('ascii')
            
        else:
            respone = 'Invalid action for user management'
        
        if self.tn is not None and self.tn.get_socket():
                self.tn.close()
        return (response)
    