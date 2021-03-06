<service xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:sword="http://purl.org/net/sword/terms/"
    xmlns:atom="http://www.w3.org/2005/Atom"
    xmlns:pkp="http://pkp.sfu.ca/SWORD"
    xmlns="http://www.w3.org/2007/app">
    <sword:version>2.0</sword:version>
    <sword:maxUploadSize>1000</sword:maxUploadSize>
    <pkp:uploadChecksumType>SHA-1</pkp:uploadChecksumType>
    % if accepting == 'Yes':
    <pkp:pln_accepting is_accepting="{{accepting}}">The PKP PLN is currently accepting deposits.</pkp:pln_accepting>
    % else:
    <pkp:pln_accepting is_accepting="{{accepting}}">The PKP PLN is currently in pilot phase and is only accepting deposits from members of the pilot.</pkp:pln_accepting>
    % end

    <pkp:terms_of_use>
        % for term in terms:
        <pkp:{{term['key_code']}} updated="{{term['created']}}">
          {{term['content']}}
        </pkp:{{term['key_code']}}>
        % end
    </pkp:terms_of_use>

    <workspace>
        <atom:title>PKP PLN deposit for {{on_behalf_of}}</atom:title>
        <collection href="{{sword_server_base_url}}/col-iri/{{on_behalf_of}}">
            <accept>application/atom+xml;type=entry</accept>
            <sword:mediation>true</sword:mediation>
        </collection>
    </workspace>
</service>
