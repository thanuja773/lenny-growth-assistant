import { SourceCitation } from "@/lib/types";
import { ExternalLink, Mic, FileText } from "lucide-react";

interface SourceCardProps {
  source: SourceCitation;
}

export function SourceCard({ source }: SourceCardProps) {
  const isPodcast = source.source_type.toLowerCase() === "podcast";

  return (
    <div className="bg-white border border-border rounded-xl p-3.5 hover:shadow-md transition-shadow cursor-pointer group">
      <div className="flex items-start gap-3">
        {/* Mock Thumbnail Image/Icon */}
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center shrink-0 ${isPodcast ? 'bg-orange-100 text-orange-600' : 'bg-blue-100 text-blue-600'}`}>
          {isPodcast ? <Mic className="w-6 h-6" /> : <FileText className="w-6 h-6" />}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className="text-[13px] font-semibold text-foreground line-clamp-2 leading-snug">
              {source.transcript_title}
            </h4>
            <ExternalLink className="w-3.5 h-3.5 text-muted-foreground shrink-0 mt-0.5 opacity-50 group-hover:opacity-100 transition-opacity" />
          </div>
          
          <p className="text-[13px] text-muted-foreground line-clamp-2 leading-relaxed mt-1">
            "{source.text}"
          </p>
          
          <div className="mt-2 inline-flex items-center">
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider ${isPodcast ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
              {source.source_type}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
