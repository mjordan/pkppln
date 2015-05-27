<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
 <title>PKP PLN Terms</title>
 <language>{{language}}</language>
 <description>The 10 most recent terms of service for the PKP PLN.</description>
 <link>http://example.org/feed/terms/rss</link>
 <pubDate>{{terms[0]['created']}}</pubDate>

  % for term in terms:
  <item>
    <title>Term updated</title>
    <link href="http://pkppln/path/to/term" />
    <pubDate>{{ !term['created'] }}</pubDate>
    <description>
      {{ !term['content'] }}
    </description>
  </item>
  % end

</channel>
</rss>
