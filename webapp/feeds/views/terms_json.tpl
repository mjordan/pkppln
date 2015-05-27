 [
  % for i, term in enumerate(terms):
  {
    "pubDate": "{{ term['created'] }}",
    "description": {{ !json.dumps(term['content'], ensure_ascii=False) }}
  } \\
  <% if (i != len(terms)-1): %>
    ,
  <% end %>
  % end
]
