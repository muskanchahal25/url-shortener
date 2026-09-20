# URL Shortener — Serverless on AWS

A serverless URL shortener built with **Python (boto3)** on **AWS Lambda**, exposed through **API Gateway**, with links stored in **DynamoDB**.

Built end-to-end by **Muskan Chahal** and developed with **AI coding tools (GitHub Copilot, Cursor, ChatGPT)** for scaffolding, refactoring, and debugging.

## Live Demo

**Base URL:** `https://3sd37v98af.execute-api.ap-south-1.amazonaws.com/prod`

Because this is a REST API (no web front-end), the base URL returns `{"message":"Missing Authentication Token"}` by design. Use the endpoints below.

### Create a short link

curl -X POST "https://3sd37v98af.execute-api.ap-south-1.amazonaws.com/prod/shorten" \
  -H "Content-Type: application/json" \
  -d '{"longUrl": "https://example.com/some/long/path"}'

**Response:**
{
  "shortUrl": "https://3sd37v98af.execute-api.ap-south-1.amazonaws.com/prod/c984d06a",
  "code": "c984d06a"
}

### Follow a short link

curl -i "https://3sd37v98af.execute-api.ap-south-1.amazonaws.com/prod/c984d06a"

**Response:** `HTTP 302` with `location: https://example.com/some/long/path`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/shorten` | Accepts a long URL, returns a generated short code |
| `GET`  | `/{code}` | Looks up the code and returns a `302` redirect to the original URL |

## Architecture

Client ──► API Gateway ──► AWS Lambda ──► DynamoDB
                │                            │
           POST /shorten               store code → long URL
           GET  /{code}                read  code → long URL

- **AWS Lambda** — request handling (`create-short-url`, `redirect-short-url`)
- **API Gateway** — routing and HTTP endpoints (Lambda Proxy integration)
- **DynamoDB** — link storage (`short-urls` table, partition key `shortCode`)
- **hashlib (MD5)** — short-code generation
- **IAM** — least-privilege role scoped to the DynamoDB table
- **CloudWatch** — logs and debugging

## What I Built

- Designed and implemented a serverless URL shortener converting long URLs into short, shareable links using hash-based short codes.
- Developed REST endpoints: `POST /shorten` to create links and `GET /{code}` to return a `302` redirect.
- Integrated AWS services end to end — Lambda for logic, DynamoDB for storage (data model + partition key), API Gateway for routing.
- Configured **Lambda Proxy integration** and a **least-privilege IAM policy** scoped to the DynamoDB table.
- Deployed and verified the app live in `ap-south-1`, and debugged real integration failures — a proxy-integration misconfiguration and an `AccessDeniedException` traced through the Lambda's error output and IAM policy.

## Tech Stack

`Python` · `boto3` · `AWS Lambda` · `API Gateway` · `DynamoDB` · `IAM` · `CloudWatch` · `Git`

## Deploying

1. Create a DynamoDB table named `short-urls` with partition key `shortCode` (String).
2. Create an IAM role allowing `dynamodb:PutItem` and `dynamodb:GetItem` on that table.
3. Deploy `create-short-url` and `redirect-short-url` as Lambda functions (Python 3.12) using that role.
4. Create an API Gateway REST API with `POST /shorten` and `GET /{code}`, both using **Lambda Proxy integration**.
5. Deploy to stage `prod` and copy the Invoke URL.

---

**Author:** Muskan Chahal — [GitHub](https://github.com/muskanchahal25) · [LinkedIn](https://linkedin.com/in/muskan-chahal2505)
