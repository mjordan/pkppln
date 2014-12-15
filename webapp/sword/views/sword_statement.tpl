<atom:feed xmlns:sword="http://purl.org/net/sword/terms/"
           xmlns:atom="http://www.w3.org/2005/Atom"
           xmlns:pkp="http://pkp.sfu.ca/SWORD">
    <atom:category scheme="http://purl.org/net/sword/terms/state"
      term="{{deposit['pln_state']}}" label="State">
      {{states[deposit['pln_state']]}}
    </atom:category>
    <atom:entry>
        <atom:category scheme="http://purl.org/net/sword/terms/"
          term="http://purl.org/net/sword/terms/originalDeposit" label="Original Deposit"/>
        <atom:content type="application/zip" src="{{deposit['deposit_url']}}"/>
    </atom:entry>
</atom:feed>
