"""
Wrapper around the SWORD client used to deposit journals into the PKP PLN
via LOCKSS-O-Matic's SWORD server.
"""

client = 'pkppln_lockssomatic_sword_client.py' # @todo: add path to client as a congig param.
get_service_document_call = client + ' getSD'
deposit_call = client + 'createDeposit'

