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
    <h1>Journal Deposits</h1>

	% include('terms_nav.tpl')

	  <p>Showing deposits for <a href='{{journal['journal_url']}}'>{{ journal['title'] }}</a></p>
	  
	  <table class='table table-striped'>
	    <thead>
	      <tr>
	        <th>Date</th>
	        <th>Action</th>
	        <th>Vol</th>
	        <th>Iss</th>
	        <th>Pub date</th>
	        <th>Size</th>
	        <th>Processing State</th>
	        <th>Pln State</th>
	      </tr>
	    </thead>
	    <tbody>
	  
	  % for deposit in deposits:
	      <tr>
	        <td>{{ deposit['date_deposited'] }}</td>
	        <td>{{ deposit['deposit_action'] }}</td>
	        <td>{{ deposit['deposit_volume'] }}</td>
	        <td>{{ deposit['deposit_issue'] }}</td>
	        <td>{{ deposit['deposit_pubdate'] }}</td>
	        <td>{{ deposit['deposit_size'] }}</td>
	        <td>{{ deposit['processing_state'] }}</td>
	        <td>{{ deposit['pln_state'] }}</td>
	      </tr>
	  % end
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

    <!-- jQuery -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/static/js/bootstrap.min.js"></script>

  </body>
</html>
