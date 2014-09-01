<service xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:sword="http://purl.org/net/sword/terms/"
    xmlns:atom="http://www.w3.org/2005/Atom"
    xmlns:pkp="http://pkp.sfu.ca/SWORD"
    xmlns="http://www.w3.org/2007/app">
    <sword:version>2.0</sword:version>
    <sword:maxUploadSize>1000</sword:maxUploadSize>
    <pkp:uploadChecksumType>SHA-1</pkp:uploadChecksumType>
    <pkp:pln_accepting>{{accepting}}</pkp:pln_accepting>
    <pkp:terms_of_use>
        % for term in terms:
        <pkp:{{term[2]}} updated="{{term[1]}}">{{term[4]}}</pkp:{{term[2]}}>
        % end
    </pkp:terms_of_use>
    <workspace>
        <atom:title>PKP PLN deposit for {{on_behalf_of}}</atom:title>     
        <collection href="{{sword_server_base_url}}/api/sword/2.0/col-iri/{{on_behalf_of}}">
            <accept>application/atom+xml;type=entry</accept> 
            <sword:mediation>true</sword:mediation>
        </collection>
    </workspace>
</service>
