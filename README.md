# URL Shortener — Serverless + AI on AWS

A serverless URL shortener built with **Python (boto3)** on **AWS Lambda**, exposed through **API Gateway**, with links stored in **DynamoDB**. Each new link is enriched by the **Gemini API**, which auto-generates a title, category, and tags.

Built end-to-end by **Muskan Chahal** and developed with **AI coding tools (GitHub Copilot, Cursor, ChatGPT)**.

## Live Demo

**Base URL:** `https://3sd37v98af.execute-api.ap-south-1.amazonaws.com/prod`

Because this is a REST API (no web front-end), the base URL returns `{"message":"Missing Authentication Token"}` by design. Use the endpoints below.

### Create a short link (with AI enrichment)

```bash
curl -X POST "https://3sd37v98af.execute-api.ap-south-1.amazonaws.com/prod/shorten" \
  -H "Content-Type: application/json" \
  -d '{"longUrl": "https://www.bbc.com/news"}'
```

**Response:**
```json
{
  "shortUrl": "https://3sd37v98af.execute-api.ap-south-1.amazonaws.com/prod/41627412",
  "code": "41627412",
  "title": "BBC News",
  "category": "News",
  "tags": ["news", "world", "uk"]
}
```

### Follow a short link

```bash
curl -i "https://3sd37v98af.execute-api.ap-south-1.amazonaws.com/prod/41627412"
```

**Response:** `HTTP 302` with `location:` set to the original URL

## The AI Feature

Every time a link is created, the Lambda calls the **Gemini API** (`generateContent`) with a structured-output prompt and asks for:

- **title** — a short, human-readable name for the link
- **category** — a single word (Dev, News, Social, Docs, …)
- **tags** — 2–4 lowercase keywords

Results are stored in DynamoDB alongside the link and returned in the API response.

**Engineering considerations:**

- **Structured output** — `responseMimeType: "application/json"` constrains the model to valid JSON, so no fragile text parsing.
- **Model fallback chain** — the code tries `gemini-flash-latest`, then `gemini-3.5-flash`, then `gemini-flash-lite-latest`. If a model is overloaded (`503`) or retired (`404`), the next one is used.
- **Graceful degradation** — AI enrichment is wrapped in `try/except`; if the model is unavailable, the short link is still created. The AI enhances the app but never blocks it.
- **Zero extra dependencies** — uses `urllib` from the Python standard library, so no Lambda layer or package bundle is required.
- **Secret handling** — the API key is read from an environment variable and never committed to the repository.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/shorten` | Accepts a long URL, returns a short code + AI-generated title, category and tags |
| `GET`  | `/{code}` | Looks up the code and returns a `302` redirect to the original URL |

## Architecture

```
Client ──► API Gateway ──► AWS Lambda ──► DynamoDB
                              │
                              └──────────► Gemini API
                                           (title / category / tags)
```

- **AWS Lambda** — request handling and AI orchestration (`create-short-url`, `redirect-short-url`)
- **API Gateway** — routing and HTTP endpoints (Lambda Proxy integration)
- **DynamoDB** — link storage (`short-urls` table, partition key `shortCode`)
- **Gemini API** — LLM enrichment of each link
- **hashlib (MD5)** — short-code generation
- **IAM** — least-privilege role scoped to the DynamoDB table
- **CloudWatch** — logs and debugging

## What I Built

- Designed and implemented a serverless URL shortener converting long URLs into short, shareable links using hash-based short codes.
- **Integrated the Gemini API to auto-generate link titles, categories, and tags** using structured JSON output, with a multi-model fallback chain for resilience.
- Developed REST endpoints: `POST /shorten` to create links and `GET /{code}` to return a `302` redirect.
- Integrated AWS services end to end — Lambda for logic, DynamoDB for storage (data model + partition key), API Gateway for routing.
- Configured **Lambda Proxy integration** and a **least-privilege IAM policy** scoped to the DynamoDB table.
- Deployed and verified the app live in `ap-south-1`, debugging real integration failures — a proxy-integration misconfiguration, an `AccessDeniedException` traced through the Lambda's error output, and a retired LLM model name.

## Tech Stack

`Python` · `boto3` · `AWS Lambda` · `API Gateway` · `DynamoDB` · `IAM` · `CloudWatch` · `Gemini API` · `Git`

## Deploying

1. Create a DynamoDB table named `short-urls` with partition key `shortCode` (String).
2. Create an IAM role allowing `dynamodb:PutItem` and `dynamodb:GetItem` on that table.
3. Deploy `create-short-url` and `redirect-short-url` as Lambda functions (Python 3.12) using that role.
4. Set `GEMINI_API_KEY` as an environment variable on `create-short-url` (free key from Google AI Studio). Set the function timeout to 15 seconds.
5. Create an API Gateway REST API with `POST /shorten` and `GET /{code}`, both using **Lambda Proxy integration**.
6. Deploy to stage `prod` and copy the Invoke URL.

---

**Author:** Muskan Chahal — [GitHub](https://github.com/muskanchahal25) · [LinkedIn](https://linkedin.com/in/muskan-chahal2505)
