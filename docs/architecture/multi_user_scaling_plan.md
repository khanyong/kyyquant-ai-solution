# Multi-User SaaS Scaling Plan (Single-Server Model)

## 1. Executive Summary
The goal is to scale the current **KyyQuant AI** platform from a single Admin-user system to a Multi-User SaaS platform supporting 10-20 concurrent users. 
**Crucially**, we can achieve this **without** provisioning separate AWS servers for each user. 

By leveraging the existing **REST API** architecture (which currently proxies Kiwoom/KIS), we can turn the Backend into a Multi-Tenant Trading Engine that "impersonates" users sequentially or in parallel using their stored API credentials.

---

## 2. Core Architecture: "Centralized Brain, Decentralized Keys"

### Concept
*   **The Brain (Server)**: A single high-performance AWS instance running 24/7. It holds the "Strategy Logic" (e.g., "RSI < 30").
*   ** The Market Data (Feeder)**: The Server fetches market prices *once* using a master account (Admin) or a dedicated data feed.
*   **The Users (Keys)**: Users do not need running software. They simply provide their **API Key, Secret, and Account Number** via the Web UI.
*   **The Hands (Execution)**: When the Brain says "Buy Samsung", the Server looks up *who is subscribed* to this strategy, retrieves specific API Keys, and sends orders for them.

### Why This Works
The current `KiwoomAPIClient` communicates via HTTP/REST. Unlike old-school COM/OCX automation which binds a whole machine to one login session, REST APIs allow us to switch contexts simply by changing the `Authorization` header or `AppKey` in the request body.

---

## 3. Database Updates (Schema)
*(Already partially prepared by your recent Multi-Account Work)*

1.  **`user_api_keys` (Enhanced)**:
    *   Currently stores `account_number`, `account_password`, `app_key`, `app_secret`.
    *   **Action**: Ensure `user_id` is indexed for fast lookup.

2.  **`strategy_subscriptions` (New Table)**:
    *   Links `user_id` -> `strategy_id`.
    *   Columns: `status` (active/paused), `allocated_budget` (how much money to use), `created_at`.
    *   *Purpose*: Allows 20 users to follow "Strategy A" with different budget amounts.

3.  **`execution_logs` (RLS)**:
    *   Ensure strict **Row Level Security** so User A can only see the logs of their own orders.

---

## 4. Backend Logic Refactoring

### A. The "Broadcaster" Pattern
Currently, `BrainService` likely looks at the Admin's account. We will change the loop:

**Current (Admin Only):**
```python
if strategy_signal == "BUY":
    kiwoom_client(admin_ctx).order(stock, ... )
```

**New (Multi-User):**
```python
if strategy_signal == "BUY":
    # 1. Find all active subscribers
    subscribers = db.query("SELECT * FROM strategy_subscriptions WHERE strategy_id = ?", strategy_id)
    
    # 2. Parallel Execution (Async)
    tasks = []
    for sub in subscribers:
        user_keys = decrypt_keys(sub.user_id)
        client = KiwoomAPIClient(context=user_keys) # Ephemeral Client
        tasks.append(client.order_stock(stock, quantity=calc_qty(sub.budget), ...))
    
    await asyncio.gather(*tasks) # Execute all 20 orders simultaneously
```

### B. Token Management Upgrade
*   **Challenge**: Managing 20+ OAuth Tokens in local files (`token_cache.json`) might cause race conditions.
*   **Solution**: Move token storage to **Redis** or the **Database**.
    *   Key: `token:{user_id}:{mode}`
    *   This ensures scale and robustness.

---

## 5. Security Model (Critical)
Since we store user API keys, security is paramount.
1.  **Encryption**: Keys MUST be encrypted at rest (AES-256). You are already doing this.
2.  **Isolation**: The execution logic for User A must never accidentally use User B's token. The `KiwoomAPIClient` instantiation must be strictly scoped.
3.  **User Consent**: Disclaimer that "Server will execute trades on your behalf".

---

## 6. Development Roadmap

### Phase 1: Subscription Foundation (Week 1)
*   Create `strategy_subscriptions` table.
*   Update UI to allow users to "Subscribe" to a strategy (instead of just viewing it).

### Phase 2: Execution Engine Upgrade (Week 2)
*   Modify `BrainService` to fetch subscribers.
*   Implement the `async` broadcasting loop.
*   Test with 2 internal accounts (Your Real + Your Mock).

### Phase 3: Beta Launch (Week 3)
*   Onboard 1-3 trusted users.
*   Monitor "Rate Limits" (Ensure KIS API limits are per-user, not per-IP. Usually per-AppKey, so it's safe).

## 7. Limitations & Solutions
*   **Latency**: Execution loop for 20 users might take 1-2 seconds total. For Swing/Trend logic, this is fine. For Scalping, we might need distributed workers (Celery).
*   **Error Handling**: If User B's API Key expires/fails, it shouldn't stop User C's order. Wrap each execution in a `try/except` block.

**Verdict**: This plan allows you to scale to 10-20 users (and even 100+) using your **existing AWS server**, basically turning your project into a mini-Hedge Fund platform.
