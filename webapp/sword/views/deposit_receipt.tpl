<entry xmlns="http://www.w3.org/2005/Atom" xmlns:sword="http://purl.org/net/sword/">

    <sword:treatment>Issues for preservation in the PKP PLN from
    journal {{journal_title}} ({{journal_uuid}}).</sword:treatment>

    <content src="{{sword_server_base_url}}/api/sword/2.0/cont-iri/{{journal_uuid}}/{{deposit_uuid}}" />

    <link rel="edit-media"
    href="{{sword_server_base_url}}/api/sword/2.0/col-iri/{{journal_uuid}}" />

    <link rel="edit-media"
    href="{{sword_server_base_url}}/api/sword/2.0/cont-iri/{{journal_uuid}}/{{deposit_uuid}}" />

    <link rel="http://purl.org/net/sword/terms/add"
    href="{{sword_server_base_url}}/api/sword/2.0/cont-iri/{{journal_uuid}}/{{deposit_uuid}}/edit" />

    <link rel="edit"
    href="{{sword_server_base_url}}/api/sword/2.0/cont-iri/{{journal_uuid}}/{{deposit_uuid}}/edit" />

    <link rel="http://purl.org/net/sword/terms/statement" type="application/atom+xml;type=feed"
    href="{{sword_server_base_url}}/api/sword/2.0/cont-iri/{{journal_uuid}}/{{deposit_uuid}}/state" />
</entry>
