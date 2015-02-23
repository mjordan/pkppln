<?xml version="1.0" encoding="utf-8"?>

<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{{language}}">

	<title>PKP PLN Terms</title>
	<subtitle>The 10 most recent terms of service for the PKP PLN.</subtitle>
	<link href="http://example.org/feed/terms/atom" rel="self" />
	<link href="http://example.org/" />
	<id>http://path/to/feed</id>
	<updated>{{terms[0]['created']}}</updated>

	% for term in terms:
	<entry>
		<title>Term updated</title>
		<link href="http://pkppln/path/to/term" />
		<id>{{term['id']}}</id>
		<updated>{{term['created']}}</updated>
		<content type="text">
			{{term['content']}}
		</content>
	</entry>
	% end

</feed>
