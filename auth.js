/* =========================================================================
   二等ドローン学科クイズ — 認証（Supabase）
   - メール/パスワード/氏名で登録 → 確認メール（マジックリンク）で認証
   - ログイン / パスワード再設定
   - 認証が完了するまでクイズ本体（#app）は表示しない
   ========================================================================= */
(function () {
  "use strict";

  var gate = document.getElementById("authgate");
  var app = document.getElementById("app");
  var acctbar = document.getElementById("acctbar");
  var acct = document.getElementById("acct");
  var logoutBtn = document.getElementById("logout");

  // ---- 設定チェック ----
  if (!window.SUPA_URL || /ここに/.test(window.SUPA_URL)) {
    app.style.display = "none";
    gate.innerHTML =
      '<div class="card" style="margin-top:24px">' +
      '<h2 style="margin-top:0">⚙️ セットアップが未完了です</h2>' +
      '<p>Supabase の接続情報が設定されていません。<code>config.js</code> に Project URL と anon キーを設定し、' +
      '<code>docs/SETUP_AUTH.md</code> の手順を完了してください。</p></div>';
    return;
  }

  // Supabase クライアントはライブラリ読込後に生成（下部の初期化処理で設定）
  var sb = null;
  function notReady() {
    msg("読み込み中です。数秒後にもう一度お試しください。", "err");
  }

  var PW_RE = /^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;
  var pwHint = "8文字以上で、英数字・大文字・記号をそれぞれ1つ以上含めてください。";

  function esc(s) { var d = document.createElement("div"); d.textContent = s == null ? "" : s; return d.innerHTML; }
  function redirectBase() { return location.origin + location.pathname; }

  function shell(title, bodyHtml) {
    return (
      '<div class="card" style="max-width:440px;margin:34px auto 0">' +
      '<h2 style="margin-top:0">' + title + "</h2>" +
      '<div id="authmsg"></div>' +
      bodyHtml +
      "</div>"
    );
  }
  function field(id, label, type, ph) {
    var lab = '<label style="display:block;font-size:.82rem;color:var(--mut);margin:12px 0 5px">' + label + "</label>";
    // 自動入力（パスワードマネージャ）が正しく機能するよう適切な autocomplete を付与
    var ac;
    if (type === "email") ac = "username";
    else if (type === "password") ac = /^(rg_|rs_)/.test(id) ? "new-password" : "current-password";
    else if (id === "rg_name") ac = "name";
    else ac = "off";
    if (type === "password") {
      // 初期はマスク。「表示」ボタンを押したときだけ平文表示（再度押すと隠す）
      var toggle = '<button type="button" tabindex="-1" onclick="' +
        "var i=this.parentNode.querySelector('input'); var p=i.type==='password'; i.type=p?'text':'password'; this.textContent=p?'隠す':'表示';" +
        '" style="position:absolute;right:6px;top:50%;transform:translateY(-50%);border:none;background:transparent;color:var(--accent);font-size:.78rem;font-weight:700;cursor:pointer;padding:4px 8px">表示</button>';
      return (
        lab +
        '<div style="position:relative">' +
        '<input id="' + id + '" type="password" placeholder="' + (ph || "") + '" autocomplete="' + ac + '" ' +
        'style="width:100%;padding:11px 52px 11px 12px;border:1px solid var(--line);border-radius:10px;font:inherit;background:#fff;color:var(--ink)">' +
        toggle +
        '</div>'
      );
    }
    return (
      lab +
      '<input id="' + id + '" type="' + type + '" placeholder="' + (ph || "") + '" autocomplete="' + ac + '" ' +
      'style="width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:10px;font:inherit;background:#fff;color:var(--ink)">'
    );
  }
  function linkRow(html) {
    return '<div style="margin-top:14px;font-size:.85rem;text-align:center;color:var(--mut)">' + html + "</div>";
  }
  function msg(text, kind) {
    var m = document.getElementById("authmsg");
    if (!m) { alert(text); return; }
    var col = kind === "err" ? "var(--ng)" : kind === "ok" ? "var(--ok)" : "var(--mut)";
    var bg = kind === "err" ? "#fef2f2" : kind === "ok" ? "#f0fdf4" : "#f1f5f9";
    m.innerHTML = '<div style="margin:6px 0 2px;padding:10px 12px;border-radius:9px;background:' + bg + ';color:' + col + ';font-size:.86rem">' + esc(text) + "</div>";
  }
  function show(html) { app.style.display = "none"; acctbar.style.display = "none"; gate.style.display = "block"; gate.innerHTML = html; }

  // ---------- 画面：ログイン ----------
  function renderLogin() {
    window.__user = null;
    var al = document.getElementById("adminLink");
    if (al) al.style.display = "none";
    show(shell("ログイン",
      field("li_email", "メールアドレス", "email", "you@example.com") +
      field("li_pw", "パスワード", "password", "") +
      '<button class="btn" id="li_btn">ログイン</button>' +
      linkRow('<a href="#" id="to_register">新規登録</a> ／ <a href="#" id="to_forgot">パスワードを忘れた方</a>')
    ));
    document.getElementById("li_btn").onclick = doLogin;
    document.getElementById("to_register").onclick = function (e) { e.preventDefault(); renderRegister(); };
    document.getElementById("to_forgot").onclick = function (e) { e.preventDefault(); renderForgot(); };
  }
  function doLogin() {
    var email = document.getElementById("li_email").value.trim();
    var pw = document.getElementById("li_pw").value;
    if (!email || !pw) { msg("メールアドレスとパスワードを入力してください。", "err"); return; }
    if (!sb) { notReady(); return; }
    msg("確認中…");
    attemptLogin(email, pw, false);
  }
  function attemptLogin(email, pw, triedTrim) {
    sb.auth.signInWithPassword({ email: email, password: pw }).then(function (r) {
      if (r.error) {
        var m = r.error.message || "";
        var st = r.error.status;
        if (/confirm/i.test(m)) { renderAwait(email, true); return; }
        if (st === 429 || /rate|too many/i.test(m)) {
          msg("試行回数が多すぎます。1分ほど待ってから、もう一度お試しください。", "err"); return;
        }
        if (/invalid login credentials/i.test(m)) {
          // コピー時の前後空白・改行を自動で除いて1回だけ再試行
          var pwt = pw.replace(/^[\s　]+|[\s　]+$/g, "");
          if (!triedTrim && pwt !== pw) { attemptLogin(email, pwt, true); return; }
          var hint = "";
          if (/[０-９Ａ-Ｚａ-ｚ　]/.test(pw)) {
            hint = "（全角の数字・英字・スペースが含まれています。半角で入力してください）";
          }
          msg("メールアドレスまたはパスワードが正しくありません。" + hint +
              "［表示］ボタンで入力内容を確認できます。", "err");
          return;
        }
        msg("ログインに失敗しました：" + m, "err");
        return;
      }
      enterApp(r.data.user);
    }, function () {
      msg("通信エラーが発生しました。ネットワーク接続をご確認のうえ再度お試しください。", "err");
    });
  }

  // ---------- 画面：新規登録 ----------
  function renderRegister() {
    show(shell("新規登録",
      field("rg_name", "氏名", "text", "山田 太郎") +
      field("rg_email", "メールアドレス", "email", "you@example.com") +
      field("rg_pw", "パスワード", "password", "") +
      '<div style="font-size:.76rem;color:var(--mut);margin-top:5px">' + pwHint + "</div>" +
      field("rg_pw2", "パスワード（確認）", "password", "") +
      '<button class="btn" id="rg_btn">登録して確認メールを送る</button>' +
      linkRow('すでにアカウントをお持ちの方は <a href="#" id="to_login">ログイン</a>')
    ));
    document.getElementById("rg_btn").onclick = doRegister;
    document.getElementById("to_login").onclick = function (e) { e.preventDefault(); renderLogin(); };
  }
  function doRegister() {
    var name = document.getElementById("rg_name").value.trim();
    var email = document.getElementById("rg_email").value.trim();
    var pw = document.getElementById("rg_pw").value;
    var pw2 = document.getElementById("rg_pw2").value;
    if (!name) { msg("氏名を入力してください。", "err"); return; }
    if (!email) { msg("メールアドレスを入力してください。", "err"); return; }
    if (!PW_RE.test(pw)) { msg("パスワードの条件を満たしていません。" + pwHint, "err"); return; }
    if (pw !== pw2) { msg("確認用パスワードが一致しません。", "err"); return; }
    if (!sb) { notReady(); return; }
    msg("登録中…");
    sb.auth.signUp({
      email: email, password: pw,
      options: { data: { full_name: name }, emailRedirectTo: redirectBase() }
    }).then(function (r) {
      if (r.error) {
        if (/registered|exist/i.test(r.error.message)) { msg("このメールアドレスは既に登録されています。ログインまたはパスワード再設定をご利用ください。", "err"); }
        else { msg("登録に失敗しました：" + r.error.message, "err"); }
        return;
      }
      renderAwait(email, false);
    });
  }

  // ---------- 画面：確認メール待ち ----------
  function renderAwait(email, alreadyRegistered) {
    show(shell("メールを確認してください",
      '<p style="font-size:.9rem">' + esc(email) + ' 宛に' + (alreadyRegistered ? "確認メールを再送できます。" : "確認メールを送信しました。") +
      'メール内のリンクをクリックすると認証が完了し、ログインできるようになります。</p>' +
      '<button class="btn sec" id="aw_resend">確認メールを再送する</button>' +
      '<button class="btn" id="aw_login">ログイン画面へ</button>'
    ));
    document.getElementById("aw_resend").onclick = function () {
      if (!sb) { notReady(); return; }
      msg("再送中…");
      sb.auth.resend({ type: "signup", email: email, options: { emailRedirectTo: redirectBase() } }).then(function (r) {
        msg(r.error ? ("再送に失敗しました：" + r.error.message) : "確認メールを再送しました。", r.error ? "err" : "ok");
      });
    };
    document.getElementById("aw_login").onclick = renderLogin;
  }

  // ---------- 画面：パスワードを忘れた ----------
  function renderForgot() {
    show(shell("パスワード再設定",
      '<p style="font-size:.88rem;color:var(--mut)">ご登録のメールアドレスに、再設定用のリンクをお送りします。</p>' +
      field("fg_email", "メールアドレス", "email", "you@example.com") +
      '<button class="btn" id="fg_btn">再設定メールを送る</button>' +
      linkRow('<a href="#" id="to_login2">ログインに戻る</a>')
    ));
    document.getElementById("fg_btn").onclick = function () {
      var email = document.getElementById("fg_email").value.trim();
      if (!email) { msg("メールアドレスを入力してください。", "err"); return; }
      if (!sb) { notReady(); return; }
      msg("送信中…");
      sb.auth.resetPasswordForEmail(email, { redirectTo: redirectBase() }).then(function (r) {
        msg(r.error ? ("送信に失敗しました：" + r.error.message) : "再設定メールを送信しました。メールのリンクから新しいパスワードを設定してください。", r.error ? "err" : "ok");
      });
    };
    document.getElementById("to_login2").onclick = function (e) { e.preventDefault(); renderLogin(); };
  }

  // ---------- 画面：新しいパスワードの設定（再設定リンク経由）----------
  function renderReset() {
    show(shell("新しいパスワードの設定",
      field("rs_pw", "新しいパスワード", "password", "") +
      '<div style="font-size:.76rem;color:var(--mut);margin-top:5px">' + pwHint + "</div>" +
      field("rs_pw2", "新しいパスワード（確認）", "password", "") +
      '<button class="btn" id="rs_btn">パスワードを変更する</button>'
    ));
    document.getElementById("rs_btn").onclick = function () {
      var pw = document.getElementById("rs_pw").value;
      var pw2 = document.getElementById("rs_pw2").value;
      if (!PW_RE.test(pw)) { msg("パスワードの条件を満たしていません。" + pwHint, "err"); return; }
      if (pw !== pw2) { msg("確認用パスワードが一致しません。", "err"); return; }
      if (!sb) { notReady(); return; }
      msg("変更中…");
      sb.auth.updateUser({ password: pw }).then(function (r) {
        if (r.error) { msg("変更に失敗しました：" + r.error.message, "err"); return; }
        msg("パスワードを変更しました。", "ok");
        setTimeout(function () { sb.auth.getUser().then(function (u) { enterApp(u.data.user); }); }, 800);
      });
    };
  }

  // ---------- アプリ表示 ----------
  function enterApp(user) {
    window.__user = user;
    if (typeof window.DQonAuth === "function") { try { window.DQonAuth(user); } catch (e) {} }
    gate.style.display = "none";
    gate.innerHTML = "";
    app.style.display = "block";
    acctbar.style.display = "flex";
    var nm = (user && user.user_metadata && user.user_metadata.full_name) || (user && user.email) || "";
    acct.textContent = nm + " さん";
    // 管理者だけに「管理者画面」リンクを表示
    var al = document.getElementById("adminLink");
    if (al) {
      al.style.display = "none";
      sb.from("profiles").select("role").eq("id", user.id).maybeSingle().then(function (r) {
        if (r && r.data && r.data.role === "admin") al.style.display = "inline-block";
      });
    }
    // 履歴に残った認証トークンを URL から除去
    if (location.hash && /access_token|type=/.test(location.hash)) {
      history.replaceState(null, "", redirectBase());
    }
  }

  logoutBtn.onclick = function () {
    if (!sb) { renderLogin(); return; }
    sb.auth.signOut().then(function () { renderLogin(); });
  };

  // ---- まずログイン画面を即時表示（ライブラリ読込を待たない）----
  renderLogin();

  // ---- Supabase ライブラリの読み込みを待ってから初期化 ----
  (function waitSupabase(n) {
    if (window.supabase) {
      sb = window.supabase.createClient(window.SUPA_URL, window.SUPA_ANON);
      window.__sb = sb;
      sb.auth.onAuthStateChange(function (event, session) {
        if (event === "PASSWORD_RECOVERY") { renderReset(); return; }
        if (event === "SIGNED_OUT") { renderLogin(); return; }
        if (session && session.user) { enterApp(session.user); }
      });
      sb.auth.getSession().then(function (r) {
        if (r.data.session && r.data.session.user) { enterApp(r.data.session.user); }
      });
      return;
    }
    if (n > 300) { return; } // 約30秒で諦める（ログイン画面は表示済み）
    setTimeout(function () { waitSupabase(n + 1); }, 100);
  })(0);
})();
