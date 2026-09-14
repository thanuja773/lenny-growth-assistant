import { useState } from "react";
import { SourceCitation, Artifact } from "@/lib/types";
import { SourceCard } from "../sources/SourceCard";
import { ArrowRight, Share2, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

interface InsightsPanelProps {
  sources: SourceCitation[];
  artifacts: Artifact[];
  onOpenArtifact: (id: string) => void;
}

export function InsightsPanel({ sources, artifacts, onOpenArtifact }: InsightsPanelProps) {
  const [activeTab, setActiveTab] = useState<"sources" | "summary" | "related" | "artifacts">("sources");

  const tabs = [
    { id: "sources", label: "Sources" },
    { id: "summary", label: "Summary" },
    { id: "related", label: "Related" },
    { id: "artifacts", label: "Artifacts" },
  ] as const;

  const relatedTopics = [
    "growth loops", "network effects", "product engagement",
    "habit formation", "PLG", "user onboarding"
  ];

  return (
    <div className="w-[340px] border-l border-border bg-white flex flex-col h-full shrink-0 hidden lg:flex shadow-sm z-10">
      <div className="h-16 border-b border-border flex items-center px-4 shrink-0">
        <div className="flex w-full gap-4">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "text-[13px] font-medium py-4 transition-colors relative",
                activeTab === tab.id ? "text-primary" : "text-muted-foreground hover:text-foreground"
              )}
            >
              {tab.label}
              {activeTab === tab.id && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-t-full" />
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-5 scrollbar-hide">
        {activeTab === "sources" && (
          <div className="space-y-8">
            <div>
              {sources.length > 0 ? (
                <>
                  <h3 className="text-sm font-semibold text-foreground mb-4">Top sources ({sources.length})</h3>
                  <div className="space-y-3">
                    {sources.map((source, idx) => (
                      <SourceCard key={`${source.chunk_id}-${idx}`} source={source} />
                    ))}
                  </div>
                  <button className="w-full mt-4 py-3 flex items-center justify-center gap-2 text-sm font-medium text-primary hover:text-indigo-700 transition-colors border border-border rounded-xl">
                    View all sources <ArrowRight className="w-4 h-4" />
                  </button>
                </>
              ) : (
                <div className="text-center py-12">
                  <p className="text-sm text-muted-foreground">No sources yet.</p>
                  <p className="text-xs text-muted-foreground mt-1">Ask a question to see the retrieved transcripts.</p>
                </div>
              )}
            </div>

            <div>
              <div className="flex items-center gap-2 mb-4 text-primary">
                <Share2 className="w-4 h-4" />
                <h3 className="text-sm font-semibold text-foreground">Related topics</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {relatedTopics.map((topic, i) => (
                  <button 
                    key={i}
                    className="px-3 py-1.5 bg-white border border-border hover:border-primary/30 rounded-full text-[13px] text-muted-foreground hover:text-foreground transition-colors shadow-sm"
                  >
                    {topic}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "summary" && (
          <div className="text-center py-12">
             <p className="text-sm text-muted-foreground">Summary not available</p>
          </div>
        )}

        {activeTab === "related" && (
           <div className="text-center py-12">
             <p className="text-sm text-muted-foreground">See related topics in the Sources tab.</p>
           </div>
        )}

        {activeTab === "artifacts" && (
          <div className="space-y-4">
            {artifacts.length > 0 ? (
              <>
                <h3 className="text-sm font-semibold text-foreground mb-4">Session Artifacts ({artifacts.length})</h3>
                <div className="space-y-3">
                  {artifacts.map((art) => (
                    <div 
                      key={art.artifact_id}
                      onClick={() => onOpenArtifact(art.artifact_id)}
                      className="bg-white border border-border rounded-xl p-3.5 hover:shadow-md hover:border-primary/40 transition-all cursor-pointer group"
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded bg-primary/10 flex items-center justify-center text-primary shrink-0">
                          <FileText className="w-5 h-5" />
                        </div>
                        <div>
                          <h4 className="text-[13px] font-semibold text-foreground line-clamp-2 leading-snug group-hover:text-primary transition-colors">
                            {art.title}
                          </h4>
                          <p className="text-[11px] text-muted-foreground mt-1">
                            {art.word_count || 0} words • {new Date(art.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <p className="text-sm font-medium text-foreground">No artifacts yet</p>
                <p className="text-[13px] text-muted-foreground mt-2 px-4 leading-relaxed">Turn a conversation into a polished Ship 30 for 30 essay.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
