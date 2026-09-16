# Data Model: Topic Suggestions Bot

## Suggestion (table `suggestions`)

| Field | Type | Rules |
|-------|------|-------|
| id | INTEGER PK AUTOINCREMENT | |
| user_id | INTEGER NOT NULL | Telegram sender id |
| username | TEXT NULL | @username or full name |
| kind | TEXT NOT NULL | `text` or `voice` (CHECK constraint) |
| text | TEXT NOT NULL | non-empty after strip |
| chat_id | INTEGER NOT NULL | |
| message_id | INTEGER NOT NULL | original message |
| created_at | TEXT NOT NULL | ISO-8601 UTC |

Lifecycle: insert-only in v1 (no update/delete). A row existing ⇔ 👍 may be set.

## Author (config only)

`AUTHOR_USER_ID` integer; not persisted.
