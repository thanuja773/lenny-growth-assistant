import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChatMessage } from "@/lib/types";
import { Copy, ThumbsUp, ThumbsDown, Bookmark, ArrowRight, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatAreaProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onFollowUp: (query: string) => void;
}

export function ChatArea({ messages, isLoading, onFollowUp }: ChatAreaProps) {
  // Safe helper to extract main points if we want to visually separate them, 
  // but for now, we just rely on markdown rendering to handle bolding and bullets beautifully.
  return (
    <div className="flex-1 overflow-y-auto px-4 py-8 sm:px-12 space-y-10 scrollbar-hide">
      <div className="max-w-4xl mx-auto w-full space-y-10 pb-8">
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className="flex gap-4 w-full"
          >
            {msg.role === "user" ? (
              <div className="w-8 h-8 rounded-full bg-primary flex flex-shrink-0 items-center justify-center text-primary-foreground font-semibold text-sm shadow-sm mt-1">
                T
              </div>
            ) : (
              <div className="w-8 h-8 rounded-full bg-teal-400 flex flex-shrink-0 items-center justify-center overflow-hidden shadow-sm mt-1">
                 <div className="w-4 h-4 bg-white rounded-tl-full rounded-br-full transform -rotate-45" />
              </div>
            )}
            
            <div className={cn(
              "flex-1",
              msg.role === "user" ? "pt-1" : ""
            )}>
              {msg.role === "user" ? (
                <div className="inline-block bg-muted px-5 py-3 rounded-2xl rounded-tl-sm text-foreground text-[15px] leading-relaxed max-w-[85%] shadow-sm border border-black/5">
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              ) : (
                <div className="w-full">
                  <div className="prose prose-slate max-w-none text-[15px] leading-[1.7] text-gray-800">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                  
                  {/* Assistant Actions Footer */}
                  <div className="flex items-center justify-between mt-4 text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <button className="p-2 hover:bg-muted rounded-md transition-colors"><Copy className="w-4 h-4" /></button>
                      <button className="p-2 hover:bg-muted rounded-md transition-colors"><ThumbsUp className="w-4 h-4" /></button>
                      <button className="p-2 hover:bg-muted rounded-md transition-colors"><ThumbsDown className="w-4 h-4" /></button>
                      <button className="p-2 hover:bg-muted rounded-md transition-colors"><Bookmark className="w-4 h-4" /></button>
                    </div>
                    <span className="text-xs uppercase tracking-wider font-medium opacity-60">
                      {new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}
                    </span>
                  </div>

                  {/* Follow ups & CTA - only show on the LAST assistant message for realism */}
                  {idx === messages.length - 1 && !isLoading && (
                    <div className="mt-6 space-y-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <button 
                          onClick={() => onFollowUp("Can you give a real-world example?")}
                          className="px-4 py-2 bg-background border border-border hover:border-primary/40 rounded-full text-sm text-foreground transition-colors shadow-sm"
                        >
                          Can you give a real-world example?
                        </button>
                        <button 
                          onClick={() => onFollowUp("How is this different from acquisition loops?")}
                          className="px-4 py-2 bg-background border border-border hover:border-primary/40 rounded-full text-sm text-foreground transition-colors shadow-sm"
                        >
                          How is this different from acquisition loops?
                        </button>
                      </div>
                      <button 
                        onClick={() => onFollowUp("Convert this to a Ship 30 for 30 essay")}
                        className="group flex items-center gap-2 px-4 py-2 bg-background border border-border hover:border-primary/50 hover:shadow-sm rounded-full text-sm font-medium text-foreground transition-all"
                      >
                        Convert this to a Ship 30 for 30 essay 
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                      </button>
                    </div>
                  )}

                  {/* Artifact Badge in Assistant Message */}
                  {msg.artifact_id && (
                    <div className="mt-4 flex items-center">
                      <div className="bg-primary/5 border border-primary/20 rounded-xl px-4 py-3 flex flex-col gap-1 w-64 shadow-sm relative overflow-hidden group cursor-pointer hover:bg-primary/10 transition-colors">
                        <div className="absolute top-0 left-0 w-1 h-full bg-primary/40"></div>
                        <div className="flex items-center gap-2 text-primary font-medium text-sm">
                           <FileText className="w-4 h-4" />
                           Ship 30 for 30 Essay
                        </div>
                        <p className="text-xs text-muted-foreground ml-6">
                           Artifact generated. Open panel to view.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex gap-4 w-full">
            <div className="w-8 h-8 rounded-full bg-teal-400 flex flex-shrink-0 items-center justify-center overflow-hidden shadow-sm mt-1">
                 <div className="w-4 h-4 bg-white rounded-tl-full rounded-br-full transform -rotate-45" />
            </div>
            <div className="flex-1 py-2 flex items-center gap-3">
              <div className="flex gap-1.5">
                <div className="w-2 h-2 rounded-full bg-primary/40 animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 rounded-full bg-primary/60 animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 rounded-full bg-primary/80 animate-bounce"></div>
              </div>
              <span className="text-sm font-medium text-muted-foreground animate-pulse">Searching transcripts and thinking...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
