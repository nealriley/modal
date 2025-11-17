# Clipboard Workflows by Platform

Summaries focus on ensuring the backend can return a single text block while clients perform OS-specific clipboard operations.

## Android (Priority #1)
- **API**: `ClipboardManager` (API 11+). Requires `android.permission.POST_NOTIFICATIONS` only if showing status; clipboard write otherwise unrestricted but pasteboard data is cleared after some time on Android 13+ when app moves to background.
- **Workflow**:
  1. Foreground service or activity captures audio and mode, posts request to backend.
  2. On success, call `ClipboardManager.setPrimaryClip(ClipData.newPlainText(...))`.
  3. Optionally show heads-up notification or toast indicating text is ready.
- **Automation hooks**: Quick Settings tile or `MediaProjection` style overlay can trigger recording. Consider Wear OS complication later.
- **Edge cases**: Android 10+ restricts background clipboard reads but writes are allowed; ensure service stays foreground while writing to avoid `SecurityException` on future APIs.

## iOS / iPadOS
- **API**: `UIPasteboard.general`. Starting iOS 16, the OS prompts users when apps read clipboard but writes are silent.
- **Workflow**:
  1. Shortcut or SwiftUI app records audio, sends to backend.
  2. After response, call `UIPasteboard.general.string = text`.
  3. Use `UIPasteboard.detectPatterns` if we want to label data (optional).
- **Automation hooks**: Shortcuts app can orchestrate HTTP request + clipboard assignment without native app initially. Later, build app with `AVAudioRecorder` + background mic entitlement for better UX.
- **Edge cases**: Large strings OK but limit to <1 MB for reliability. Provide haptic/notification confirming clipboard update.

## macOS
- **API**: `NSPasteboard.general`. Set string data via `clearContents()` + `setString(_:forType:)` with `NSPasteboard.PasteboardType.string`.
- **Workflow**:
  1. Menu bar agent with global hotkey records audio using `AVAudioEngine`.
  2. After backend response, writes text to pasteboard and optionally simulates Cmd+V if user toggles automation (accessibility permission required).
- **Automation hooks**: LaunchAgent for background start, AppleScript/Shortcuts to trigger recording, Accessibility API for hotkeys.
- **Edge cases**: For terminal mode, consider automatically appending newline; ensure we do not clear user clipboard unexpectedly by storing previous contents if undo is desired.

## Windows
- **API**: `SetClipboardData` via Win32, or `Clipboard.SetText` within .NET / WinUI. Requires STA thread.
- **Workflow**:
  1. Tray app (WinUI 3 or WPF) captures audio via WASAPI.
  2. On completion, open clipboard (`OpenClipboard`), empty, set CF_UNICODETEXT.
  3. Toast notification informs user text is ready.
- **Automation hooks**: Global hotkey registered through `RegisterHotKey`. Optional PowerShell script for CLI usage.
- **Edge cases**: Clipboard is a singleton—must handle `ERROR_ACCESS_DENIED` by retrying when another process owns it. Respect corporate group-policy restrictions.

## Steam Deck / Linux (SteamOS)
- **API**: Wayland clipboard via portals (xdg-desktop-portal), or fallback to X11 `xclip`/`xsel` when running desktop mode.
- **Workflow**:
  1. Desktop utility (Qt/PySide or Rust + GTK) runs with microphone access and global shortcut (Steam Input binding).
  2. After response, call portal D-Bus method `org.freedesktop.portal.Clipboard.SetClipboard` (Wayland) or run `xclip -selection clipboard` when in X11 session.
- **Automation hooks**: Steam Deck performance overlay buttons can trigger scripts; also map back paddles to custom shortcuts.
- **Edge cases**: Wayland forbids background clipboard ownership without active surface; need to present minimal window or use portal request-callback to set clipboard.

## Testing Considerations
- Each platform should include automated tests or manual checklists verifying clipboard contents, including multi-line commands, Unicode, and large snippets (~50 KB).
- Build UI telemetry so backend can remain clipboard-agnostic while still monitoring success (clients can POST telemetry or include `client_version`).

Link platform-specific findings back to onboarding docs once implementations begin.
