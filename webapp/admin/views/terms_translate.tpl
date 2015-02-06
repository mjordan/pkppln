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

	% include('terms_nav.tpl')

	<p>Use the form to edit a translation of the the {{ display_lang }} 
	terms, based on US English. The US English term is shown below each input for reference.</p>

	<form action="/admin/terms/translate" method="post" role="form">
	
	% if display_lang == '':
	<div class='form-group'>
		<label for='display_lang'>Language</label>
		<input class='form-control' name='display_lang' id='display_lang'>
		<p class="help-block">This value must be one of the 
		<a target="_blank" href="http://pkp.sfu.ca/wiki/index.php/Translating_OxS#OJS_Languages">
		locale codes used by OJS</a>.</p>
	</div>
	<hr>
	% else:
		<input type='hidden' name='display_lang' id='display_lang' value='{{display_lang}}'>
	% end	

    %for term in terms:    
		<div class='form-group'>
			<label for="{{term['key_code']}}">{{term['key_code']}}</label>
			<textarea class='form-control' name="{{term['key_code']}}" id="{{term['key_code']}}">
% if term['lang_code'] != 'en-US':
{{term['content']}}
% end
			</textarea> 
    	<p class='help-block'>{{en_terms[term['key_code']]['content']}}</p>    	
    	</div>
    	<hr>
    %end
    
    
    <div class="form-group">
        <button type="submit" class="btn btn-primary">Save</button>
    </div>
    </form>

	% include('terms_nav.tpl')

	</div>

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
