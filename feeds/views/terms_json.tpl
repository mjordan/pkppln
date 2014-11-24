 [
  % for i, term in enumerate(terms):
  {
    "pubDate": "{{ term['last_updated'] }}",
    "description": {{ !json.dumps(term['text']) }}
  } \\
  <% if (i != len(terms)-1): %>
    ,
  <% end %>
  % end
]
