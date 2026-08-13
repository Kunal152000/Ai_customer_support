# Frontend Code Flow — AI Support Streamlit App

> **Stack:** Streamlit · Pydantic · requests (HTTP)  
> **Entry point:** `frontend/app.py`

---

## 1. App Bootstrap

```
streamlit run app.py
        │
        ├─ st.set_page_config(title="AI Support", layout="wide", ...)
        │
        ├─ get_container()   [cached with @st.cache_resource]
        │       └─ Container.__init__()
        │               ├─ SessionManager()
        │               │       └─ Wraps st.session_state
        │               │               keys: access_token, user, authenticated
        │               │
        │               ├─ Settings()
        │               │       └─ Reads BACKEND_URL, REQUEST_TIMEOUT from .env
        │               │
        │               ├─ APIClient(settings, session_manager)
        │               │       └─ requests.Session() for HTTP calls
        │               │               Attaches Bearer token from SessionManager
        │               │
        │               ├─ AuthAPI(api_client)
        │               │       └─ Thin HTTP adapter for /auth/* endpoints
        │               │
        │               └─ AuthService(auth_api, session_manager)
        │                       └─ Business logic for auth + session management
        │
        └─ session_manager.initialize()
                └─ Sets defaults in st.session_state:
                        access_token = None
                        user         = None
                        authenticated = False
```

---

## 2. Authentication Routing Decision

Every Streamlit rerun starts here:

```
app.py (re-executes top-to-bottom on every interaction)
        │
        └─ session_manager.is_authenticated()
                │       └─ reads st.session_state["authenticated"]
                │
                ├─ False  →  show Auth pages (see §3, §4)
                └─ True   →  show Authenticated App (see §5)
```

---

## 3. User Lifetime — Registration Flow

```
[User visits app for the first time]
        │
        ▼
Login page is shown (default auth_page = "login")
        │
        ├─ User clicks "Create Account" button
        │       └─ st.session_state["auth_page"] = "signup"
        │       └─ st.rerun()   →  Streamlit re-runs app.py
        │
        ▼
AuthView.signup() renders signup form:
        Fields: name, email, password, confirm_password
        │
        ├─ Form submitted?
        │       │
        │       └─ _handle_signup(name, email, password, confirm_password)
        │               │
        │               ├─ passwords match check
        │               │       └─ Mismatch → st.error("Passwords do not match")
        │               │
        │               ├─ Pydantic validation
        │               │       RegisterRequest(name, email, password)
        │               │               └─ ValidationError → st.error(field message)
        │               │
        │               └─ AuthService.register(register_request)
        │                       │
        │                       └─ AuthAPI.register()
        │                               └─ APIClient.post("/auth/register", json)
        │                                       └─ POST http://backend/auth/register
        │                                               │
        │                                               ├─ HTTP 200 → UserResponse
        │                                               ├─ HTTP 409 → "Account already exists"
        │                                               ├─ HTTP 422 → "Check information entered"
        │                                               └─ HTTP 5xx → "Server error"
        │
        ├─ Success: st.success("Account created. Please login.")
        │           st.session_state["auth_page"] = "login"
        │           st.rerun()   →  back to Login page
        │
        └─ "Already have an account?" → Back to Login button
                └─ st.session_state["auth_page"] = "login"
                └─ st.rerun()
```

---

## 4. User Lifetime — Login Flow

```
[Auth page = "login"]
        │
        ▼
AuthView.login() renders login form:
        Fields: email, password
        │
        ├─ Form submitted?
        │       │
        │       └─ _handle_login(email, password)
        │               │
        │               ├─ Pydantic validation
        │               │       LoginRequest(email, password)
        │               │               └─ ValidationError → st.error(field message)
        │               │
        │               ├─ AuthService.login(login_request)
        │               │       │
        │               │       └─ AuthAPI.login()
        │               │               └─ APIClient.post("/auth/login", json)
        │               │                       └─ POST http://backend/auth/login
        │               │                               │
        │               │                               ├─ HTTP 200 → TokenResponse { access_token }
        │               │                               └─ HTTP 401 → "Invalid email or password"
        │               │
        │               │       On success:
        │               │       SessionManager.login(access_token)
        │               │               └─ st.session_state["access_token"] = token
        │               │               └─ st.session_state["authenticated"]  = True
        │               │
        │               ├─ AuthService.get_current_user()
        │               │       │
        │               │       └─ AuthAPI.get_current_user()
        │               │               └─ APIClient.get("/auth/me")
        │               │                       └─ GET http://backend/auth/me
        │               │                               Returns user dict
        │               │
        │               │       SessionManager.set_user(user_response)
        │               │               └─ st.session_state["user"] = user_response
        │               │
        │               ├─ st.success("Login successful!")
        │               ├─ st.session_state["auth_page"] = "dashboard"
        │               └─ st.rerun()   →  app re-executes, now authenticated = True
        │
        └─ "Don't have an account?" → Create Account button
                └─ st.session_state["auth_page"] = "signup"
                └─ st.rerun()
```

---

## 5. User Lifetime — Authenticated Session

```
[session_manager.is_authenticated() == True]
        │
        ▼
app.py  authenticated branch:
        │
        ├─ user = session_manager.get_user()
        │       └─ reads st.session_state["user"]
        │
        ├─ st.title("AI Support")
        ├─ st.write(f"Welcome, {user.name}!")    (or "Welcome!" if user is None)
        ├─ st.success("You are successfully authenticated.")
        │
        └─ Logout Button
                │
                └─ st.button("Logout") clicked?
                        │
                        └─ AuthService.logout()
                                └─ SessionManager.logout()
                                        ├─ st.session_state["access_token"]  = None
                                        ├─ st.session_state["user"]          = None
                                        └─ st.session_state["authenticated"] = False
                        │
                        ├─ st.session_state["auth_page"] = "login"
                        └─ st.rerun()   →  back to unauthenticated Login page
```

---

## 6. HTTP Layer — How Frontend Talks to Backend

```
All API calls flow through:

APIClient
  ├─ _headers()
  │       ├─ Content-Type: application/json (always)
  │       └─ Authorization: Bearer <token>  (if token in session)
  │
  ├─ post(endpoint, json)
  │       └─ requests.Session.post(BACKEND_URL + endpoint, headers, json, timeout)
  │               └─ response.raise_for_status()  →  raises HTTPError on 4xx/5xx
  │               └─ return response.json()
  │
  ├─ get(endpoint, params)
  │       └─ requests.Session.get(...)
  │
  ├─ put(endpoint, json)
  └─ delete(endpoint)
```

Error handling in views:
| Exception | Handler | User sees |
|---|---|---|
| `ValidationError` | `_display_validation_error()` | Field-level Pydantic errors |
| `HTTPError` 401 | `_display_api_error()` | "Invalid email or password" |
| `HTTPError` 409 | `_display_api_error()` | "Account with this email already exists" |
| `HTTPError` 422 | `_display_api_error()` | "Check the information you entered" |
| `HTTPError` 5xx | `_display_api_error()` | "Server encountered an error" |
| Any other | generic `except` | "Something went wrong. Please try again." |

---

## 7. Dependency Injection — Container

```
Container (cached singleton via @st.cache_resource)
  │
  ├─ SessionManager        — st.session_state wrapper (auth state)
  ├─ Settings              — BACKEND_URL, REQUEST_TIMEOUT from env
  ├─ APIClient             — HTTP client (uses Settings + SessionManager)
  ├─ AuthAPI               — Backend auth endpoint adapter (uses APIClient)
  └─ AuthService           — Login/Register/Logout logic (uses AuthAPI + SessionManager)
```

The `Container` is instantiated once per Streamlit app process (cached with `@st.cache_resource`) and injected into views at startup.

---

## 8. Complete User Lifetime Summary

```
First Visit
    │
    ▼
[Unauthenticated]
    ├─ /signup   →  Fill form → POST /auth/register → success → redirect to /login
    └─ /login    →  Fill form → POST /auth/login    → JWT stored in session
                                        │
                                        └─ GET /auth/me → user stored in session
                                                │
                                                ▼
                                    [Authenticated Dashboard]
                                        ├─ Welcome message shown
                                        ├─ (Future: documents, chat UI)
                                        └─ Logout → clear session → back to /login
```
