# iOS Shortcut: Record → Transcribe → Clipboard

Create a native Shortcut that captures audio, uploads it to the Codespaces backend, and copies the transcript to the iOS clipboard in under 10 seconds.

## Prerequisites
- iPhone or iPad running iOS/iPadOS 17+
- Latest Shortcuts app (built-in)
- Backend URL (e.g., `https://bookish-engine-...app.github.dev/v1/transcriptions`)
- Audio mode to request (`terminal`, `code`, or `creative`)
- Optional: API key/headers if the endpoint becomes authenticated (not required now)

## Build the Shortcut
1. **Create actions stack**
   - Open *Shortcuts → + → Add Action*.
   - Add **Dictate Text** (or **Record Audio**) if you want voice capture directly in Shortcuts. For highest fidelity, choose **Record Audio**, set *Audio Quality* to *High*, and *Stop Recording* action to *On Tap*.
   - Add **Get File from Recording** (Shortcuts automatically outputs an `audio.m4a` file).
2. **Prepare POST payload**
   - Add **Dictionary** action called `Form Fields` with keys:
     - `mode` → Text (e.g., `terminal`)
   - Add **File** action `Form File`:
     - Key: `audio`
     - Value: select *Provided Input* → *Recording*.
   - Combine using **Get Contents of URL**:
     - URL: your backend `https://…/v1/transcriptions`
     - Method: POST
     - Request Body: *Form*
     - Add the dictionary items (Shortcuts lets you add multiple form entries; attach the audio file field as one entry, `mode` as another).
3. **Handle response**
   - In **Get Contents of URL**, set *Response* to *JSON*.
   - Add **Get Dictionary Value** → Key `clipboard`.
   - Add another **Get Dictionary Value** → Key `text`.
   - Add **Copy to Clipboard** with the retrieved text and enable *Show When Run* for quick confirmation.
   - Optionally show a notification with the mode/provider from the returned payload.
4. **Error handling**
   - Wrap the network call in **Otherwise** branch:
     - Use **If** action: `Get Contents of URL` → *Provided Input* → *Has Value*.
     - In the *Otherwise* block, add **Show Result** with `Error: {Provided Input}` to surface backend errors (e.g., ffmpeg/whisper diagnostics).

## Usage
1. Tap the Shortcut or trigger via Siri (“Hey Siri, Transcribe Terminal”).
2. Speak or record until done; Shortcuts saves the clip as `.m4a`.
3. Shortcut performs the POST multipart upload, receives JSON, and copies `clipboard.text` into the system clipboard.
4. Paste immediately in any app; clipboard also syncs via iCloud if enabled.

## Tips
- Duplicate the Shortcut per `mode` or add a **Choose from Menu** at the start to select mode dynamically.
- If you move the backend URL, store it in Shortcuts → *Settings → Environment Variables* (or use a **Text** action at the top) so you only edit once.
- For debugging, log the full JSON by inserting **Quick Look** before copying to the clipboard.
