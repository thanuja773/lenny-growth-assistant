"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { InsightsPanel } from "@/components/layout/InsightsPanel";
import { ChatArea } from "@/components/chat/ChatArea";
import { Composer } from "@/components/chat/Composer";
import { EmptyState } from "@/components/chat/EmptyState";
import { ChatMessage, SourceCitation, Artifact } from "@/lib/types";
import { sendChatMessage, createSession, getSessionMessages, getArtifact, getSessionArtifacts } from "@/lib/api";
import { ArtifactViewer } from "@/components/artifacts/ArtifactViewer";

export default function Home() {
  const [provider, setProvider] = useState("ollama");
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sources, setSources] = useState<SourceCitation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(null);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);

  const loadArtifacts = async (sessionId: string) => {
    try {
      const data = await getSessionArtifacts(sessionId);
      setArtifacts(data);
    } catch (e) {
      console.error("Failed to load artifacts", e);
    }
  };

  useEffect(() => {
    if (activeArtifactId) {
      const found = artifacts.find(a => a.artifact_id === activeArtifactId);
      if (found) {
        setActiveArtifact(found);
      } else {
        getArtifact(activeArtifactId).then(art => {
          setActiveArtifact(art);
          setArtifacts(prev => [art, ...prev]);
        }).catch(console.error);
      }
    } else {
      setActiveArtifact(null);
    }
  }, [activeArtifactId, artifacts]);

  // Load session if needed (stubbed for future local storage persistence if desired, 
  // but for now we rely on the backend. We start fresh on reload).
  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    setSources([]);
    setArtifacts([]);
    setActiveArtifactId(null);
    setError(null);
  };

  const handleSend = async (query: string) => {
    setError(null);
    setIsLoading(true);
    
    // Optimistic user message
    const userMsg: ChatMessage = { role: "user", content: query };
    setMessages((prev) => [...prev, userMsg]);

    try {
      let currentSessionId = activeSessionId;
      
      // If no session exists, create one implicitly or rely on backend to create it.
      // We will let the backend create it and return the session ID.
      
      const response = await sendChatMessage(query, provider, currentSessionId || undefined);
      
      if (!currentSessionId && response.session_id) {
        setActiveSessionId(response.session_id);
      }

      setSources(response.sources || []);
      
      const assistantMsg: ChatMessage = { 
        role: "assistant", 
        content: response.answer,
        artifact_id: response.artifact_id
      };
      
      setMessages((prev) => [...prev, assistantMsg]);
      
      if (response.artifact_id) {
        setActiveArtifactId(response.artifact_id);
        if (currentSessionId || response.session_id) {
          loadArtifacts(currentSessionId || response.session_id!);
        }
      }
    } catch (err: any) {
      console.error(err);
      let errorMessage = "An unexpected error occurred.";
      if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
        errorMessage = "Backend unavailable. Check that FastAPI is running and try again.";
      } else if (err.message.includes("timed out") || err.message.includes("Ollama provider error")) {
        errorMessage = "Ollama isn't available right now or timed out. Check that Ollama is running and try again.";
      } else {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden text-foreground">
      <Sidebar 
        onNewChat={handleNewChat}
        recentSessions={activeSessionId ? [{ id: activeSessionId, title: "Current Conversation" }] : []}
        activeSessionId={activeSessionId}
      />
      
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">
        <Topbar provider={provider} setProvider={setProvider} />
        
        {error && (
          <div className="bg-red-500/10 border-b border-red-500/20 px-6 py-3 flex items-center justify-center text-sm text-red-500">
            {error}
          </div>
        )}

        {messages.length === 0 ? (
          <EmptyState onPromptSelect={handleSend} />
        ) : (
          <ChatArea messages={messages} isLoading={isLoading} onFollowUp={handleSend} />
        )}
        
        <div className="p-4 bg-background z-10 border-t border-border/40 relative">
          <Composer onSend={handleSend} disabled={isLoading} />
        </div>
      </div>

      {activeArtifact ? (
        <ArtifactViewer 
          artifact={activeArtifact} 
          onClose={() => setActiveArtifactId(null)} 
        />
      ) : (
        <InsightsPanel 
          sources={sources} 
          artifacts={artifacts} 
          onOpenArtifact={setActiveArtifactId}
        />
      )}
    </div>
  );
}
