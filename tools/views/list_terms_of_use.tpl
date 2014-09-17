<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PKP PLN Terms of Use</title>

    <!-- Bootstrap -->
    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/bootstrap-theme.min.css" rel="stylesheet">

    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <div class="container">
    <h1>PKP PLN Terms of Use</h1>
    <p class="text-right"><a href="/add_term/new">Add new term</a></p>

    <table class="table condensed">
    <tr><th>ID</th><th>Current version</th><th>Last updated</th><th>Key</th><th>Locale</th><th>Text</th><th>Actions</th></tr>
    %for row in rows:
    <tr>
    %for col in row:
    <td>{{col}}</td>
    %end
    %if row[0] != 'ID':
    <td><a href="/edit_term/{{row[0]}}">Edit</a> / <a href="/add_term/{{row[0]}}">Clone</a> / <a class="confirm-delete" href="/delete_term/{{row[0]}}">Delete</a></td>
    %end
    </tr>
    %end
    </table>
    <p class="text-right"><a href="/add_term/new">Add new term</a></p>
    </div>

    <!-- jQuery -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/js/bootstrap.min.js"></script>

    <!-- Simple confirm delete function. -->
    <script>
    $( document ).ready(function() {
        $('.confirm-delete').click(function(c) {
	    c.preventDefault();
	    thisHref = $(this).attr('href');
	    if(confirm('Are you sure you want to delete this item?')) {
		window.location = thisHref;
	    }
        });
    });
    </script>

  </body>
</html>
