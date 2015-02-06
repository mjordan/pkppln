<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PKP PLN Terms of Use: {{form_title}}</title>

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

	% include('terms_nav.tpl')
    
    <h2>{{form_title}}</h2>

    <form action="/admin/terms/save" method="POST" role="form">
        % if defined('id'):
             <input type="hidden" name="id" value="{{id}}" />
        % end
        % if defined('weight'):
        	<input type='hidden' name='weight' value="{{weight}}" />
       	% end
        <div class="form-group">
             <label for="language">Language</label>
             <input name="language" type="text" maxlength="20" class="form-control" id="language" value="{{lang_code}}" />
             <span class="help-block">This value must be one of the <a target="_blank" href="http://pkp.sfu.ca/wiki/index.php/Translating_OxS#OJS_Languages">locale codes used by OJS</a>.</span>
        </div>
        <div class="form-group">
             <label for="key">Locale string key</label>
             <input name="key" type="text" maxlength="256" class="form-control" id="key" value="{{key_code}}" />
             <span class="help-block">Enter the locale key here. It must start with 'plugins.generic.pln.terms_of_use.'</span>
        </div>
        <div class="form-group">
             <label for="text">Term text</label>
             <textarea name="text" rows="5" class="form-control" id="key">{{content}}</textarea>
             <span class="help-block">Enter the text of the term here.</span>
        </div>
        <div class="form-group">
            <button type="submit" class="btn btn-primary">Save</button>
        </div>
    </form>
    
	% include('terms_nav.tpl')

    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/js/bootstrap.min.js"></script>
  </body>
</html>
