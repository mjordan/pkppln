<atom:feed xmlns:sword="http://purl.org/net/sword/terms/"
           xmlns:atom="http://www.w3.org/2005/Atom"
           xmlns:pkp="http://pkp.sfu.ca/SWORD">
    <atom:category scheme="http://purl.org/net/sword/terms/state" term="{{state_term}}" label="State">{{state_description}}</atom:category>
    <atom:entry>
        <atom:category scheme="http://purl.org/net/sword/terms/" term="http://purl.org/net/sword/terms/originalDeposit" label="Orignal Deposit"/>
        % for file in files:
        <atom:content type="application/zip" src="{{file}}"/>
        % end
    </atom:entry>
</atom:feed>
