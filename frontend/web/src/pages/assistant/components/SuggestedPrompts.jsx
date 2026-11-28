/**
 * Suggested starter questions for quick testing and user onboarding (Phase 5).
 */
const DEFAULT_PROMPTS = [
  'Is it safe for me to exercise outdoors right now?',
  'How can I reduce emissions from my daily commute?',
  'What precautions should sensitive groups take when PM2.5 is elevated?',
  'What do WHO guidelines recommend for PM2.5 exposure?',
];

export default function SuggestedPrompts({ onSelectPrompt, disabled }) {
  return (
    <div className="d-flex flex-wrap gap-2 mt-3">
      {DEFAULT_PROMPTS.map((prompt) => (
        <button
          key={prompt}
          type="button"
          className="btn btn-outline-secondary btn-sm"
          onClick={() => onSelectPrompt(prompt)}
          disabled={disabled}
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}
