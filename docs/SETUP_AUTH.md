# ログイン機能（Supabase）セットアップ手順

このサイトのログイン・会員登録・メール認証・パスワード再設定・管理画面は **Supabase** を利用します。
以下の手順を一度だけ行えば、GitHub Pages のまま動作します。所要 15〜20 分ほどです。

---

## 0. 用語

- **Project URL / anon キー** … サイトから Supabase に接続するための公開情報。`config.js` に貼ります（公開して安全）。
- **service_role キー** … 全権限を持つ秘密鍵。**絶対にサイトやリポジトリに貼らないでください。**

---

## 1. Supabase プロジェクトを作成

1. https://supabase.com にアクセスし、サインアップ／ログイン。
2. **New project** を作成。
   - Name: 任意（例：drone-quiz）
   - Database Password: 控えておく
   - Region: **Northeast Asia (Tokyo)** 推奨
3. 作成完了まで1〜2分待つ。

## 2. 接続情報を取得して config.js に設定

1. ダッシュボード左下 **Project Settings → API** を開く。
2. **Project URL** と **Project API keys → `anon` `public`** をコピー。
3. リポジトリの `config.js` を開き、次の2行を実際の値に置き換える。

```js
window.SUPA_URL  = "https://xxxxxxxx.supabase.co";
window.SUPA_ANON = "eyJhbGciOi...(anon public キー)...";
```

## 3. データベースを作成

1. ダッシュボード **SQL Editor → New query**。
2. リポジトリの `db/schema.sql` の中身をすべて貼り付けて **Run**。
   （`profiles` テーブル・自動作成トリガ・権限ポリシー・管理画面用関数が作られます）

## 4. メール認証を有効化

1. **Authentication → Sign In / Providers → Email** を開く。
2. **Enable Email provider** をオン。
3. **Confirm email**（メール確認）を**オン**にする。
   → 新規登録時に確認メール（マジックリンク）が送られ、クリックで認証完了になります。
4. （任意）パスワード強度：**Authentication → Policies / Password** で
   最低文字数を **8**、必要文字種を有効にできます（サイト側でも 8文字・大文字・数字・記号を必須にしています）。

## 5. リダイレクトURLを設定

1. **Authentication → URL Configuration** を開く。
2. **Site URL** に公開URLを設定：
   ```
   https://technodronekurashiki.github.io/drone-license-workbook/
   ```
3. **Redirect URLs** に以下を追加（クイズ本体と管理画面）：
   ```
   https://technodronekurashiki.github.io/drone-license-workbook/
   https://technodronekurashiki.github.io/drone-license-workbook/index.html
   https://technodronekurashiki.github.io/drone-license-workbook/二等ドローン学科クイズ.html
   https://technodronekurashiki.github.io/drone-license-workbook/管理者画面.html
   ```
   ※ ローカル動作確認をする場合は `http://localhost:....` も追加。

## 6. メール文面を設定（任意・推奨）

**Authentication → Emails → Templates** で、各テンプレートを下記に置き換えると日本語の案内になります。
（`{{ .ConfirmationURL }}` `{{ .Email }}` はそのまま残してください）

### ■ Confirm signup（新規登録の確認）
- 件名：
  ```
  【二等ドローン学科クイズ】メールアドレスの確認
  ```
- 本文：
  ```html
  <p>{{ .Email }} 様</p>
  <p>二等ドローン学科クイズへのご登録ありがとうございます。<br>
  下のボタンからメールアドレスを確認すると、ログインできるようになります。</p>
  <p><a href="{{ .ConfirmationURL }}">メールアドレスを確認する</a></p>
  <p>このリンクの有効期限は24時間です。<br>
  心当たりがない場合は、このメールを破棄してください。</p>
  <p>— 二等ドローン学科クイズ 運営</p>
  ```

### ■ Reset password（パスワード再設定）
- 件名：
  ```
  【二等ドローン学科クイズ】パスワード再設定
  ```
- 本文：
  ```html
  <p>{{ .Email }} 様</p>
  <p>パスワード再設定のご依頼を受け付けました。<br>
  下のボタンから新しいパスワードを設定してください。</p>
  <p><a href="{{ .ConfirmationURL }}">パスワードを再設定する</a></p>
  <p>このリンクの有効期限は1時間です。<br>
  心当たりがない場合は、このメールを破棄してください。パスワードは変更されません。</p>
  <p>— 二等ドローン学科クイズ 運営</p>
  ```

### ■ Magic Link（任意）
- 件名：`【二等ドローン学科クイズ】ログイン用リンク`
- 本文：上記にならい `{{ .ConfirmationURL }}` を含めてください。

> ⚠️ Supabase 標準の送信メールには 1時間あたりの送信数制限があります。
> 受講者数が多い・本格運用する場合は **Authentication → Emails → SMTP Settings** で
> 独自のSMTP（SendGrid／Resend／Amazon SES 等）を設定してください。

## 7. 自分を管理者にする

1. まず通常どおり、サイトから自分のメールで**新規登録 → 確認メールで認証**しておく。
2. **SQL Editor** で次を実行（メールは自分の登録メールに置き換え）：
   ```sql
   update public.profiles set role = 'admin' where email = 'あなたの登録メール';
   ```
3. `管理者画面.html` を開いてログインすると、登録アカウント一覧が表示されます。

## 8. 反映・確認

1. `config.js` の変更をコミットして `main` にデプロイ。
2. 公開URLを開き、登録 → 確認メール → ログイン → クイズ利用 までを確認。
3. 管理画面で登録者が一覧表示されることを確認。

---

## トラブルシュート

| 症状 | 対処 |
|---|---|
| 「セットアップが未完了です」と出る | `config.js` の URL/anon キーが未設定。手順2を確認。 |
| 確認メールが届かない | 迷惑メールを確認／SMTP制限（手順6の注意）／メールアドレス誤り。 |
| ログイン時「メール未確認」 | 確認メールのリンクを未クリック。再送ボタンで再送可能。 |
| 管理画面で「権限がありません」 | 手順7で `role='admin'` を設定したか確認。 |
| 認証リンクで別画面に飛ぶ | 手順5の Redirect URLs に該当ページを追加。 |
