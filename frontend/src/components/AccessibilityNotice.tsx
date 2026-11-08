export default function AccessibilityNotice() {
  return <details className="accessibility-notice">
    <summary>Keyboard, audio and reading options</summary>
    <p>Use Tab and Shift+Tab to move between controls, Enter to follow act links, and the arrow keys to change a language or recording. The first link skips to the main content.</p>
    <p>Ward boundaries support Enter or Space to select and Escape to dismiss a tooltip. Numerical ward and priority tables are available alongside the map; focus a scrollable table to move it with the arrow keys.</p>
    <p>Recordings play only when you start them. Each selected clip has supplied reference text, and available saved outputs remain readable without sound. Confirmation instructions remain text-only when approved voice audio is unavailable.</p>
    <p>Urdu and Arabic transcripts read right to left. System reduced-motion preferences are respected. Missing or untested results are labelled in text; map colour is accompanied by numerical values.</p>
  </details>;
}
