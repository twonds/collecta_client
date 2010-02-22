"""
An XMPP Pubsub Client for Collecta.

"""

from twisted.application import service
from twisted.words.protocols.jabber.jid import JID
from wokkel import client
import collecta

# Configuration parameters

COLLECTA_JID = JID('search.collecta.com')
DOMAIN = JID("guest.collecta.com")
LOG_TRAFFIC = False
QUERY = "collecta"
API_KEY = None


# Set up the Twisted application

application = service.Application("Collecta Client")

client = collecta.Client(DOMAIN, None)
client.logTraffic = LOG_TRAFFIC
client.setServiceParent(application)

handler = collecta.Search()
handler.service = COLLECTA_JID
handler.query = QUERY
handler.api_key = API_KEY
handler.setHandlerParent(client)
