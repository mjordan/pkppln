<service xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:sword="http://purl.org/net/sword/terms/"
    xmlns:atom="http://www.w3.org/2005/Atom"
    xmlns:lom="http://lockssomatic.info/SWORD2"
    xmlns="http://www.w3.org/2007/app">
    <sword:version>2.0</sword:version>
    <sword:maxUploadSize>1000</sword:maxUploadSize>
    <lom:uploadChecksumType>SHA-1</lom:uploadChecksumType>
    <workspace>
        <atom:title>PKP PLN deposit for {{on_behalf_of}}</atom:title>     
        <collection href="{{sword_server_base_url}}/api/sword/2.0/col-iri/{{on_behalf_of}}">
            <accept>application/atom+xml;type=entry</accept> 
            <sword:mediation>true</sword:mediation>
        </collection>
    </workspace>
</service>
