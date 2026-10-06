
import json, ssl, sys, urllib.parse, urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Mobile Safari/537.36"

EPS = json.loads(sys.argv[1])
out = []
for ep in EPS:
    name = ep.get("name", "?")
    url = ep["url"]
    hdr = {"User-Agent": UA}
    hdr.update(ep.get("headers") or {})
    rec = {"name": name, "url": url}
    try:
        if ep.get("head"):
            r = urllib.request.Request(url, headers=hdr, method="HEAD")
        else:
            r = urllib.request.Request(url, headers=hdr)
        with urllib.request.urlopen(r, timeout=25, context=CTX) as resp:
            rec["status"] = resp.status
            rec["ctype"] = resp.headers.get("Content-Type", "")
            if not ep.get("head"):
                body = resp.read(4000)
                rec["len"] = len(body)
                try:
                    j = json.loads(body.decode("utf-8", "ignore"))
                    rec["json"] = True
                    rec["keys"] = list(j.keys())[:14] if isinstance(j, dict) else "array(%d)" % len(j)
                    rec["snippet"] = json.dumps(j, ensure_ascii=False)[:900]
                except Exception:
                    rec["json"] = False
                    rec["snippet"] = body[:300].decode("utf-8", "ignore")
    except Exception as e:
        rec["status"] = getattr(e, "code", "ERR")
        rec["err"] = str(e)[:180]
    out.append(rec)
    print("=" * 60, flush=True)
    print("[%s] status=%s  %s" % (rec["name"], rec.get("status"), rec.get("ctype", "")), flush=True)
    if rec.get("json"):
        print("  keys:", rec.get("keys"), flush=True)
        print("  body:", rec.get("snippet", "")[:880], flush=True)
    elif rec.get("err"):
        print("  ERR:", rec.get("err"), flush=True)
    else:
        print("  raw:", rec.get("snippet", "")[:280], flush=True)

with open("result.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("PROBE_DONE", flush=True)
