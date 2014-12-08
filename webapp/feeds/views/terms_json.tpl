 [
  % for i, term in enumerate(terms):
  {
    "pubDate": "{{ term['last_updated'] }}",
    "description": {{ !json.dumps(term['text'], ensure_ascii=False) }}
  } \\
  <% if (i != len(terms)-1): %>
    ,
  <% end %>
  % end
]
