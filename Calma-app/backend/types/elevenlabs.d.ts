// Type declarations for ElevenLabs Conversational AI Web Component

declare namespace JSX {
  interface IntrinsicElements {
    'elevenlabs-convai': React.DetailedHTMLProps<
      React.HTMLAttributes<HTMLElement> & {
        'agent-id': string
      },
      HTMLElement
    >
  }
}
