# nginx in front of the website

Requests go nginx (TLS) -> anubis (`unix:/run/anubis/wl-website/anubis.sock`)
-> gunicorn (`unix:/run/wl-website.socket`). gunicorn sees neither the client
address nor the scheme, so nginx has to pass both on in headers:

- `X-Real-IP`: the client address. Anubis needs it and passes it on unchanged.
- `X-Forwarded-Proto`: `https` or `http`. Anubis passes it on unchanged and
  never sets it itself. Django trusts it (`SECURE_PROXY_SSL_HEADER` in
  `mainpage/settings.py`); without it `request.is_secure()` is False and, for
  example, password reset mails link to `http://`.

`proxy_set_header` replaces a header of the same name sent by the client, so
both can be trusted. `X-Forwarded-For` cannot: its first entries come from the
client.

## Login throttling

Login POSTs are limited per client address: 10 attempts at once, then one
every 10 seconds. Too many attempts get a `429 Too Many Requests`. Requests
with an empty key are not counted, so everything else is not limited.

In the `http` context, e.g. `/etc/nginx/conf.d/wl-website-login-limit.conf`
(Ubuntu's `nginx.conf` includes `conf.d/*.conf` there):

```nginx
map "$request_method $uri" $wl_login_limit_key {
    "POST /accounts/login/" $binary_remote_addr;
    "POST /admin/login/"    $binary_remote_addr;
    default                 "";
}
limit_req_zone $wl_login_limit_key zone=wl_login:10m rate=6r/m;
```

## Proxy location

`/etc/nginx/conf.d/conf-anubis-wl-website.inc`, included by the
`www.widelands.org` server block:

```nginx
location / {
    limit_req zone=wl_login burst=10 nodelay;
    limit_req_status 429;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_pass http://anubis-wl-website;
}
```

Apply with `sudo nginx -t && sudo systemctl reload nginx`.
