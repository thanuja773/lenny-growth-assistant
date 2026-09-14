import { useState, KeyboardEvent } from "react";
import { Send, Paperclip } from "lucide-react";
import { cn } from "@/lib/utils";

interface ComposerProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export function Composer({ onSend, disabled }: ComposerProps) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-6 pt-2 bg-background">
      <div className="relative flex items-center gap-3 bg-white border border-border rounded-2xl shadow-sm px-4 py-3 focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all">
        <button className="p-2 text-muted-foreground hover:text-foreground transition-colors shrink-0 rounded-full hover:bg-muted">
          <Paperclip className="w-5 h-5" />
        </button>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Ask anything about Lenny's podcast..."
          className="w-full max-h-32 min-h-[24px] bg-transparent border-none resize-none focus:outline-none text-foreground py-2 placeholder:text-muted-foreground text-[15px] scrollbar-hide flex-1"
          rows={1}
        />
        <div className="flex items-center gap-3 shrink-0">
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-green-50 rounded-full border border-green-100">
            <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
            <span className="text-[11px] font-medium text-green-700">Grounded Q&A</span>
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || disabled}
            className={cn(
              "p-2.5 rounded-xl flex items-center justify-center transition-colors shadow-sm",
              input.trim() && !disabled
                ? "bg-primary text-white hover:bg-indigo-600"
                : "bg-muted text-muted-foreground cursor-not-allowed"
            )}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
      <div className="flex items-center justify-between mt-3 px-2">
        <p className="text-[11px] text-muted-foreground flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full border border-muted-foreground/30 flex items-center justify-center text-[8px]">i</span>
          The assistant uses Lenny's transcripts. Answers are grounded in source material.
        </p>
        <p className="text-[11px] font-medium text-muted-foreground/60 hidden sm:block">
          Shift + Enter for newline
        </p>
      </div>
    </div>
  );
}
