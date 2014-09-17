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
    <h2>{{form_title}}</h2>

    <form action="/login" method="post">
        <div class="form-group">
             <label for="language">Language</label>
             <input name="language" type="text" class="form-control" id="language" value="{{term_values['language']}}" {{disabled}}/>
             % if len(disabled):
             <span class="help-block">You can't edit the language of the term.</span>
             % end
        </div>
        <div class="form-group">
             <label for="key">Locale string key</label>
             <input name="key" type="text" size="20" class="form-control" id="key" value="{{term_values['key']}}" {{disabled}} />
             % if len(disabled):
             <span class="help-block">You can't edit the locale string key of the term.</span>
             % end
        </div>
        <div class="form-group">
             <label for="text">Term text</label>
             <textarea name="text" rows="5" class="form-control" id="key">{{term_values['text']}}</textarea>
             <span class="help-block">Enter the text of the term here.</span>
        </div>
        <div class="form-group">
            <button type="submit" class="btn btn-primary">Save</button>
        </div>
    </form>
    <p class="text-left"><a href="/list_terms">Cancel / return to list</a></p>

    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/js/bootstrap.min.js"></script>
  </body>
</html>
