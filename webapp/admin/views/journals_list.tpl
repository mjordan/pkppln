<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PKP PLN Terms of Use</title>

    <!-- Bootstrap -->
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/bootstrap-theme.min.css" rel="stylesheet">

    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <div class="container">
    <h1>PKP PLN Journals</h1>

	% include('terms_nav.tpl')

    <table class="table table-striped">
    <thead>
    <tr>
      <th>Title</th>
      <th>Publisher</th>
      <th>Contact</th>
      <th>Actions</th>
    </tr>
    </thead>
    <tbody>
    %for journal in journals:
    <tr>
    <td>{{ journal['title'] }}</td>
    <td>{{ journal['publisher_name'] }}</td>
    <td>{{ journal['contact_email'] }}</td>
    <td>
      <a href="/admin/journals/detail/{{ journal['journal_uuid'] }}">Detail</a>
    </td>
    </tr>
    %end
    </tbody>
    </table>
    
	<nav>
	<ul class='pager'>
	
	% if page > 1:
	<li><a href='?p={{ page - 1 }}'><span aria-hidden="true">&larr;</span> Previous page</a></li>
	% else:
	<li class='disabled'><a href='#'><span aria-hidden="true">&larr;</span> Previous page</a></li>
	% end
	
	% if page < pages:
	<li><a href='?p={{page + 1 }}'>Next page <span aria-hidden="true">&rarr;</span></a></li>
	% else:
	<li class='disabled'><a href='#'>Next page <span aria-hidden="true">&rarr;</span></a></li>
	% end
	</ul>
	</nav>
	

	% include('terms_nav.tpl')

    </div>

    <!-- jQuery -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/static/js/bootstrap.min.js"></script>

  </body>
</html>
