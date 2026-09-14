interface EmptyStateProps {
  onPromptSelect: (prompt: string) => void;
}

export function EmptyState({ onPromptSelect }: EmptyStateProps) {
  const prompts = [
    "What makes a great growth team?",
    "How should founders prioritize product ideas?",
    "What did Lenny's guests say about product-market fit?",
    "How do you approach user research in early stage startups?"
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center w-full max-w-3xl mx-auto">
      <div className="w-16 h-16 rounded-2xl bg-teal-50 flex items-center justify-center mb-6 shadow-sm border border-teal-100">
        <div className="w-8 h-8 bg-teal-500 rounded-tl-full rounded-br-full transform -rotate-45" />
      </div>
      <h2 className="text-3xl font-bold mb-3 text-foreground tracking-tight">Lenny Growth Assistant</h2>
      <p className="text-muted-foreground mb-12 max-w-md text-[15px] leading-relaxed">
        Research smarter. Ground decisions in Lenny's best growth conversations.
      </p>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
        {prompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => onPromptSelect(prompt)}
            className="p-5 rounded-2xl border border-border bg-white hover:border-primary/30 hover:shadow-sm text-left transition-all flex flex-col justify-between min-h-[100px] group"
          >
            <span className="text-[14px] font-medium text-foreground leading-snug group-hover:text-primary transition-colors">{prompt}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
