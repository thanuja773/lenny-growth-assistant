import { Search, Sun, BookOpen, HelpCircle, User, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface TopbarProps {
  provider: string;
  setProvider: (val: string) => void;
}

export function Topbar({ provider, setProvider }: TopbarProps) {
  return (
    <header className="h-16 border-b border-border bg-background flex items-center justify-between px-6 shrink-0 z-10 relative">
      <div className="flex-1 max-w-2xl">
        <div className="relative w-full hidden sm:block group">
          <Search className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" />
          <input 
            type="text" 
            placeholder="Search transcripts, topics, or ask anything..." 
            className="w-full bg-muted/50 hover:bg-muted border border-transparent focus:border-border rounded-xl pl-10 pr-12 py-2 text-sm focus:outline-none focus:ring-4 focus:ring-primary/5 text-foreground transition-all"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
            <kbd className="hidden md:inline-flex items-center gap-1 px-1.5 py-0.5 rounded border border-border bg-background text-[10px] font-medium text-muted-foreground shadow-sm">
              <span className="text-xs">⌘</span> K
            </kbd>
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-5 ml-4">
        {/* Provider Dropdown (simulated) */}
        <div className="relative flex items-center">
          <button 
            className="flex items-center gap-2 px-3 py-1.5 bg-card border border-border rounded-full hover:bg-muted transition-colors text-sm font-medium"
            onClick={() => setProvider(provider === "ollama" ? "anthropic" : "ollama")}
          >
            <div className={cn("w-2 h-2 rounded-full", provider === "ollama" ? "bg-green-500" : "bg-primary")} />
            {provider === "ollama" ? "Ollama (Local)" : "Anthropic"}
            <ChevronDown className="w-3.5 h-3.5 text-muted-foreground ml-1" />
          </button>
        </div>

        {/* Utility Icons */}
        <div className="flex items-center gap-3 text-muted-foreground">
          <button className="hover:text-foreground transition-colors p-1"><Sun className="w-5 h-5" /></button>
          <button className="hover:text-foreground transition-colors p-1"><BookOpen className="w-5 h-5" /></button>
          <button className="hover:text-foreground transition-colors p-1"><HelpCircle className="w-5 h-5" /></button>
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-sm font-semibold shadow-sm ml-2">
            TG
          </div>
        </div>
      </div>
    </header>
  );
}
