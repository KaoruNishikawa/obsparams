# obsparams

宣言された/使用されたobsparamを抽出します

poetryで環境構築をした後、obsfiles_params_check.ipynbを使ってください
- 2つ目のセルにgithubのtokenを書き込んで使ってください
  - github > settings > developer settings > Personal access token > generate new token
- 5つ目のセルのように `check.get_obsparams(path)` 関数を使うと宣言されているobsparamを取得できます
- 8つ目のセルのように `check.params_extract([pattern], path)` 関数を使うと観測ファイルで使用されているparamを取得できます
  - keyが代入されていると抽出できない場合があります
