 [
  % for i, term in enumerate(terms):
  {
    "pubDate": "{{term['last_updated']}}",
    "description": "{{term['text']}}"
  } \\
  <% if (i != len(terms)-1): %>
    ,
  <% end %>
  % end
]
