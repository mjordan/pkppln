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
    <h1>PKP PLN Terms of Use</h1>

	% include('terms_nav.tpl')

	<p>Journal details</p>

	<dl class='dl-horizontal'>
	  <dt>Title</dt>
	  <dd>{{ journal['title'] }}</dd>
	  
	  <dt>Url</dt>
	  <dd><a href='{{journal['journal_url']}}'>{{ journal['journal_url'] }}</a></dd>
	  
	  <dt>Publisher</dt>
	  <dd><a href='{{ journal['publisher_url'] }}'>{{ journal['publisher_name'] }}</a></dd>
	  
	  <dt>Contact</dt>
	  <dd>{{ journal['contact_email'] }}</dd>
	  
	  <dt>ISSN</dt>
	  <dd>{{ journal['issn'] }}</dd>
	  
	  <dt>Recent Contact</dt>
	  <dd>{{ journal['contact_date'] }}</dd>
	  
	  <dt>Status</dt>
	  <dd>{{ journal['journal_status'] }}</dd>
	  	  
	  <dt>Notification sent</dt>
	  <dd>{{ journal['notified_date'] }}</dd>	  
	</dl>


	% include('terms_nav.tpl')

    <!-- jQuery -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/static/js/bootstrap.min.js"></script>

  </body>
</html>
