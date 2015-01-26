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
    <link href="/css/jquery-ui.min.css" rel='stylesheet'>

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

	%if message is not None:
	  <div class="alert alert-success" role="alert">{{ message }}</div>
    %end

	<p>Drag and drop the terms below to set their order.</p>

	<form action="/admin/terms/sort" method="post" role="form">
	<input type='hidden' name='order' id='order' value=''>
	<ul class="list-group" id='list-order'>
    %for term in terms:    
    <li class="list-group-item" id="{{term['key']}}">
    	{{term['key']}}<br>
    	{{term['text']}}
    </li>
    %end
    </ul>
    <div class="form-group">
        <button type="submit" class="btn btn-primary">Save</button>
    </div>
    </form>

    <!-- jQuery -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/js/bootstrap.min.js"></script>
    <script src="/js/jquery-ui.min.js"></script>

    <!-- Simple confirm delete function. -->
    <script>
    $( document ).ready(function() {
      $('#list-order').sortable({
        containment: 'parent',
        cursor: 'move'
      });
      $('button').click(function(){
      	$('#order').val($("#list-order").sortable("toArray"));
  	  });
    });
    </script>

  </body>
</html>
