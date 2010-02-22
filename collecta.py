from zope.interface import implements

from twisted.internet import defer
from twisted.python import log
from twisted.words.protocols.jabber import (
    xmlstream, sasl, client as jclient, sasl_mechanisms, jid)

from wokkel import client, pubsub



class Search(pubsub.PubSubClient):
    """A collecta client example class.
    """
    
    api_key = None
    query   = None
    
    service = 'search.collecta.com'
    node    = 'search'
    
    @defer.inlineCallbacks
    def connectionInitialized(self):
        pubsub.PubSubClient.connectionInitialized(self)
        self.send("<presence/>")

        options = {}
        if self.api_key:
            options['x-collecta#api_key'] = self.api_key
        if self.query:
            options['x-collecta#query'] = self.query

        yield self.subscribe(self.service, self.node, self.getJid(), options) 
        
        

    def itemsReceived(self, event):
        """Do something with collecta events.
        """
        log.msg("EVENT RECEIVED : ")
        for item in event.items:
            log.msg(item.toXml())
    

    def getJid(self):
	"""Return the JID the connection is authenticed as."""

	return self.xmlstream.authenticator.jid
        

## the stuff below is for older versions of twisted words

class HybridAuthenticator(client.HybridAuthenticator):

    def associateWithStream(self, xs):
        client.HybridAuthenticator.associateWithStream(self, xs)

        xs.initializers = [jclient.CheckVersionInitializer(xs)]
        inits = [(xmlstream.TLSInitiatingInitializer, False),
                 (SASLInitiatingInitializer, True),
                 (jclient.BindInitializer, False),
                 (jclient.SessionInitializer, False),
                 ]

        for initClass, required in inits:
            init = initClass(xs)
            init.required = required
            xs.initializers.append(init)

        

def HybridClientFactory(jid, password):
    """
    Client factory for XMPP 1.0.

    This is similar to L{client.XMPPClientFactory} but also tries non-SASL
    autentication.
    """

    a = HybridAuthenticator(jid, password)
    return xmlstream.XmlStreamFactory(a)



class Client(client.XMPPClient):
    """
    Service that initiates an XMPP client connection.
    """

    def __init__(self, jid, password, host=None, port=5222):
        self.jid = jid
        self.domain = jid.host
        self.host = host
        self.port = port

        factory = HybridClientFactory(jid, password)
        factory.authenticator = HybridAuthenticator(jid, password)
        client.StreamManager.__init__(self, factory)
    


## override internal stuff so that we can get sasl anonymous
class Anonymous(object):
    implements(sasl_mechanisms.ISASLMechanism)
    name = 'ANONYMOUS'
    
    def getInitialResponse(self):
        return None


class SASLInitiatingInitializer(sasl.SASLInitiatingInitializer):
    def setMechanism(self):
        jid = self.xmlstream.authenticator.jid
        password = self.xmlstream.authenticator.password

        mechanisms = sasl.get_mechanisms(self.xmlstream)

        if jid.user is not None:
            if 'DIGEST-MD5' in mechanisms:
                self.mechanism = sasl_mechanisms.DigestMD5('xmpp',
                                                           jid.host,
                                                           None,
                                                           jid.user,
                                                           password)
            elif 'PLAIN' in machanisms:
                self.mechanism = sasl_mechanisms.Plain(None, jid.user, 
                                                       password)
            else:
                raise sasl.SASLNoAcceptableMechanism()
        else:
            if 'ANONYMOUS' in mechanisms:
                self.mechanism = Anonymous()
            else:
                raise sasl.SASLNoAccetableMechanism()




class XMPPAuthenticator(jclient.XMPPAuthenticator):
    def associateWithStream(self, xs):
        xmlstream.ConnectAuthenticator.associateWithStream(self, xs)

        xs.initializers = [jclient.CheckVersionInitializer(xs)]
        inits = [(xmlstream.TLSInitiatingInitializer, False),
                 (SASLInitiatingInitializer, True),
                 (jclient.BindInitializer, False),
                 (jclient.SessionInitializer, False),
                 ]

        for initClass, required in inits:
            init = initClass(xs)
            init.required = required
            xs.initializers.append(init)

