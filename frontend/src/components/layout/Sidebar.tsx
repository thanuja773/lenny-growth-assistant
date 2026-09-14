import { Plus, Home, Compass, Bookmark, FileText, Settings, MessageSquare, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  onNewChat: () => void;
  recentSessions: { id: string; title: string }[];
  activeSessionId?: string | null;
}

export function Sidebar({ onNewChat, recentSessions, activeSessionId }: SidebarProps) {
  return (
    <div className="w-[260px] bg-[var(--sidebar-bg)] text-[var(--sidebar-fg)] flex flex-col h-full shrink-0 border-r border-[var(--sidebar-border)]">
      <div className="p-5">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-7 h-7 rounded-full bg-teal-400 flex items-center justify-center overflow-hidden shrink-0">
            {/* Simple logo approximation */}
            <div className="w-4 h-4 bg-white rounded-tl-full rounded-br-full transform -rotate-45" />
          </div>
          <div>
            <h1 className="font-bold text-base tracking-tight leading-none text-white">Lenny</h1>
            <p className="text-[11px] text-[var(--sidebar-muted-fg)] mt-1 tracking-wide uppercase">Growth Assistant</p>
          </div>
        </div>

        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2.5 rounded-lg font-medium transition-colors text-sm shadow-sm"
        >
          <Plus className="w-4 h-4" />
          New Conversation
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-2 sidebar-scroll">
        <div className="space-y-0.5 mb-8">
          <NavItem icon={<Home className="w-4 h-4" />} label="Home" active />
          <NavItem icon={<Compass className="w-4 h-4" />} label="Explore" />
          <NavItem icon={<Bookmark className="w-4 h-4" />} label="Saved" />
          <NavItem icon={<FileText className="w-4 h-4" />} label="Artifacts" />
          <NavItem icon={<Settings className="w-4 h-4" />} label="Settings" />
        </div>

        {recentSessions.length > 0 && (
          <div className="mb-4">
            <h2 className="text-[10px] font-semibold text-[var(--sidebar-muted-fg)] uppercase tracking-wider mb-2 px-3">Recent Conversations</h2>
            <div className="space-y-0.5">
              {recentSessions.map(session => (
                <button
                  key={session.id}
                  className={cn(
                    "w-full text-left px-3 py-2 rounded-md text-sm truncate flex items-center gap-3 transition-colors group",
                    activeSessionId === session.id 
                      ? "bg-[var(--sidebar-muted)] text-white" 
                      : "text-[var(--sidebar-muted-fg)] hover:bg-[var(--sidebar-muted)] hover:text-white"
                  )}
                >
                  <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-70 group-hover:opacity-100" />
                  <span className="truncate">{session.title}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="p-5 border-t border-[var(--sidebar-border)] space-y-4">
        {/* Quote Block */}
        <div className="bg-[var(--sidebar-muted)] rounded-xl p-4 text-[12px] leading-relaxed text-[var(--sidebar-muted-fg)] shadow-inner">
          <p className="italic mb-2">"Ship things, learn fast, and stay close to users."</p>
          <p className="font-medium">— Lenny Rachitsky</p>
        </div>

        {/* User Profile */}
        <button className="w-full flex items-center justify-between group pt-2">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xs font-bold border border-primary/30">
              TG
            </div>
            <span className="text-sm font-medium text-[var(--sidebar-fg)] group-hover:text-white transition-colors">Thanuja</span>
          </div>
          <ChevronRight className="w-4 h-4 text-[var(--sidebar-muted-fg)] group-hover:text-white transition-colors" />
        </button>
      </div>
    </div>
  );
}

function NavItem({ icon, label, active }: { icon: React.ReactNode; label: string; active?: boolean }) {
  return (
    <button className={cn(
      "w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
      active ? "bg-[var(--sidebar-muted)] text-white" : "text-[var(--sidebar-muted-fg)] hover:bg-[var(--sidebar-muted)] hover:text-white"
    )}>
      <span className={cn("shrink-0", active ? "text-primary" : "")}>{icon}</span>
      {label}
    </button>
  );
}
