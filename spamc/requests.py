#!/usr/bin/env python3

import email.message

from headers import *
from responses import *


class SpamdRequest:
    '''SPAMC request object.'''
    
    protocol = 'SPAMC/1.5'
    request_with_body = '{verb} {protocol}\r\n{headers}\r\n{body}'
    request_without_body = '{verb} {protocol}\r\n{headers}\r\n'
    
    def __init__(self, verb, headers = [], body = None):
        ''''''
        
        self.verb = verb
        self.headers = headers
        self.body = body
        
    def __bytes__(self):
        return self.compose().encode()
    
    def __repr__(self):
        return 'SpamdRequest({}, {}, {})'.format(self.verb, self.headers, self.body)
        
    def compose(self):
        '''Composes a request based on the verb and headers that are currently set.'''
        
        if self.body:
            self.headers.append( ContentLength( len(bytes(self.body)) ) )
            request = self.request_with_body.format(verb = self.verb,
                                                    protocol = self.protocol,
                                                    headers = ''.join(map(str, self.headers)),
                                                    body = self.body.to_string())
        else:
            self.headers.append( ContentLength(0) )
            request = self.request_without_body.format(verb = self.verb, 
                                                        protocol = self.protocol, 
                                                        headers = ''.join(map(str, self.headers)))
        
        self.headers.pop() # get rid of Content-length header in case the request is reused
        
        return request
    
class Ping(SpamdRequest):
    def __init__(self):
        super().__init__('PING')
        
    def __repr__(self):
        return 'Ping()'