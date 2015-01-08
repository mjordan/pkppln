"""
Wrapper around the SWORD client used to deposit journals into the PKP PLN
via LOCKSS-O-Matic's SWORD server. SWORD Statement requests are handled
separately.

Copyright (c) 2014 Simon Fraser University Library
Copyright (c) 2014 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

client = 'pkppln_lockssomatic_sword_client.py' # @todo: add path to client as a congig param.
get_service_document_call = client + ' getSD'
deposit_call = client + 'createDeposit'

