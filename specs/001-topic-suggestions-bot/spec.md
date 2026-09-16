# Feature Specification: Topic Suggestions Bot

**Feature Branch**: `001-topic-suggestions-bot`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description (product.md): "telegram bot. Аудитория предлагает темы для контента и
исследований текстом или голосом. Бот переводит голосовые в текст, сохраняет ответы, confirm
transcription and reciption with emoji thumbs up. author can ask summary of all suggestions."

## Clarifications

### Session 2026-09-16

- Q: Where does the audience send suggestions? → A: Private (direct) messages to the bot.
- Q: What does "confirm transcription and reception" mean? → A: A 👍 reaction on the viewer's
  message once it is saved; no text echo of the transcript.
- Q: Speech-to-text provider? → A: Groq whisper-large-v3 (planning-level decision).
- Q: Summary provider? → A: Groq LLM (planning-level decision).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Viewer suggests a topic by text (Priority: P1)

A viewer opens a private chat with the bot and writes a topic idea. The bot saves it and puts a 👍
reaction on the message so the viewer knows it was received.

**Why this priority**: Collecting suggestions is the core value; text is the simplest channel.

**Independent Test**: Send a text message to the bot from any account; the message gets 👍 and the
suggestion appears in storage with the sender and text.

**Acceptance Scenarios**:

1. **Given** the bot is running, **When** a viewer sends "Сделай видео про нейросети", **Then** the
   text is saved with the viewer's identity and time, and the message receives a 👍 reaction.
2. **Given** saving fails, **When** a viewer sends a text, **Then** no 👍 is set and the viewer gets a
   short "please try again" reply.

---

### User Story 2 - Viewer suggests a topic by voice (Priority: P2)

A viewer records a voice message. The bot turns speech into text, saves the transcript, and reacts
👍 once transcription and saving both succeed.

**Why this priority**: Voice is explicitly requested and lowers the barrier for viewers, but builds
on the text flow.

**Independent Test**: Send a voice message; it gets 👍 and storage contains a readable transcript
marked as voice.

**Acceptance Scenarios**:

1. **Given** the bot is running, **When** a viewer sends a clear voice message, **Then** its
   transcript is saved (marked as voice) and the voice message receives 👍.
2. **Given** transcription fails or returns empty text, **When** a viewer sends a voice message,
   **Then** nothing is saved, no 👍 is set, and the viewer gets a short "couldn't recognize, please
   retry or type it" reply.

---

### User Story 3 - Author requests a summary (Priority: P3)

The author sends a summary command to the bot and receives a digest of all collected suggestions,
grouped into themes with how often each theme came up.

**Why this priority**: Turns raw suggestions into actionable input, but needs suggestions to exist.

**Independent Test**: With several stored suggestions, the author sends the summary command and
receives a grouped digest; any other user sending the same command is refused.

**Acceptance Scenarios**:

1. **Given** stored suggestions exist, **When** the author sends the summary command, **Then** the
   author receives a themed summary covering all suggestions.
2. **Given** no suggestions exist, **When** the author sends the summary command, **Then** the
   author is told there are no suggestions yet.
3. **Given** a non-author, **When** they send the summary command, **Then** they are refused and
   no summary content is revealed.
4. **Given** a summary longer than one Telegram message, **When** it is sent, **Then** it arrives
   split across several messages with no content lost.

### Edge Cases

- Unsupported content (stickers, photos, video, files): not saved, no 👍, short hint "send text or voice".
- Messages in groups/channels: ignored (DM-only).
- Commands such as /start: reply with a short welcome explaining how to suggest; not saved as suggestions.
- The author's own non-command messages are saved like any viewer's.
- Summary service unavailable: author gets a short error; stored suggestions are untouched.
- Very long voice messages beyond the transcription provider's size limit: treated as a transcription failure.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept topic suggestions as text messages in private chats.
- **FR-002**: System MUST accept topic suggestions as voice messages in private chats and convert them to text.
- **FR-003**: System MUST persist each suggestion with sender id, sender display name/username, type (text/voice), text, message id and timestamp.
- **FR-004**: System MUST set a 👍 reaction on the original message only after the suggestion is persisted.
- **FR-005**: System MUST NOT set 👍 and MUST send a short retry hint when transcription or saving fails.
- **FR-006**: System MUST provide a summary command available only to the configured author.
- **FR-007**: The summary MUST cover all stored suggestions, grouping them into themes with counts.
- **FR-008**: System MUST split outputs exceeding Telegram's message length limit.
- **FR-009**: System MUST ignore messages outside private chats and non-text/non-voice content (with a hint in private chats).
- **FR-010**: System MUST never output secrets (bot token, API keys) in messages or logs.
- **FR-011**: User-facing bot replies MUST be in Russian.

### Key Entities

- **Suggestion**: one topic idea from a viewer — sender identity, kind (text/voice), text (original or transcript), source message reference, created time.
- **Author**: the single configured person allowed to request summaries.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A viewer sees 👍 on a text suggestion within 3 seconds of sending.
- **SC-002**: A viewer sees 👍 on a voice suggestion of up to 60 seconds within 10 seconds of sending.
- **SC-003**: 100% of acknowledged (👍) suggestions are present in storage; 0 unacknowledged failures are silent.
- **SC-004**: The author receives a summary of up to 500 suggestions within 30 seconds.
- **SC-005**: 0 occurrences of secrets in bot replies or logs during end-to-end testing.

## Assumptions

- Single author; identified by a numeric Telegram user id supplied via configuration.
- "Summary of all suggestions" means all suggestions ever stored (no date filter, no reset) in v1.
- Viewers need no registration; anyone who can DM the bot may suggest.
- One bot instance runs at a time on one host during streams; no horizontal scaling.
- No moderation, editing or deletion of suggestions in v1.
- Depends on external speech-to-text and text-summarization services being reachable.
