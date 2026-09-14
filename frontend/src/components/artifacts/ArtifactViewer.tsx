import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Artifact } from "@/lib/types";
import { X, Copy, Download, FileText } from "lucide-react";
import { SourceCard } from "../sources/SourceCard";

interface ArtifactViewerProps {
  artifact: Artifact;
  onClose: () => void;
}

export function ArtifactViewer({ artifact, onClose }: ArtifactViewerProps) {
  return (
    <div className="flex-1 flex flex-col h-full bg-white border-l border-border shadow-2xl z-20">
      {/* Header */}
      <div className="h-16 border-b border-border flex items-center justify-between px-6 shrink-0 bg-background">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-foreground">{artifact.title}</h2>
            <div className="flex items-center gap-2 text-[11px] text-muted-foreground mt-0.5">
              <span className="uppercase tracking-wider font-semibold">Ship 30 for 30</span>
              <span>•</span>
              <span>{artifact.word_count || 0} words</span>
              <span>•</span>
              <span>{new Date(artifact.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-md transition-colors" title="Copy Content">
            <Copy className="w-4 h-4" />
          </button>
          <button className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-md transition-colors" title="Download">
            <Download className="w-4 h-4" />
          </button>
          <div className="w-px h-4 bg-border mx-1"></div>
          <button onClick={onClose} className="p-2 text-muted-foreground hover:text-red-500 hover:bg-red-50 rounded-md transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-8 lg:p-12 scrollbar-hide flex flex-col lg:flex-row gap-8">
        
        {/* Rendered Markdown */}
        <div className="flex-1 max-w-3xl">
          <div className="prose prose-slate max-w-none text-[15px] leading-[1.8] text-gray-800">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {artifact.content}
            </ReactMarkdown>
          </div>
        </div>

        {/* Sources Sidebar */}
        <div className="w-full lg:w-80 shrink-0">
          <h3 className="text-sm font-semibold text-foreground mb-4">Grounded Sources ({artifact.sources?.length || 0})</h3>
          <div className="space-y-3">
            {artifact.sources?.map((source, idx) => (
              <SourceCard key={idx} source={source} />
            ))}
            {(!artifact.sources || artifact.sources.length === 0) && (
              <p className="text-xs text-muted-foreground italic">No specific sources cited for this artifact.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
