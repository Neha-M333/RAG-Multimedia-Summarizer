// src/pages/Chat.tsx - Enhanced functionality with original beautiful design

import { useState, useRef, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Copy, ThumbsUp, Loader2, AlertCircle, Filter, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { LanguageSelector } from "@/components/LanguageSelector";
import { api, type ChatResponse } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: any[];
  metadata?: {
    complexity?: string;
    confidence?: string;
    tokens_used?: number;
    query_understanding?: any;
  };
}

interface Document {
  id: number;
  file_name: string;
  file_type: string;
  upload_date: string;
}

const botEmojis = ["🤖", "🦾", "🧠", "⚡", "✨", "🔮"];
const getRandomBotEmoji = () => botEmojis[Math.floor(Math.random() * botEmojis.length)];

export const Chat = () => {
  // Generate consistent session ID
  const sessionId = useMemo(() => {
    const stored = sessionStorage.getItem('chat_session_id');
    if (stored) return stored;
    const newId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('chat_session_id', newId);
    return newId;
  }, []);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! 🤖 I'm your AI document assistant with enhanced understanding. I can now:\n\n✅ Understand questions even if you don't use exact words\n✅ Recognize dates in any format (2024-01-15, January 15, 2024, etc.)\n✅ Search specific documents or all documents\n✅ Provide more relevant and accurate answers\n\nWhat would you like to know?",
      timestamp: new Date(),
    },
  ]);
  
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [language, setLanguage] = useState("en");
  const [documentsCount, setDocumentsCount] = useState(0);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<string>("all");
  const [showFilters, setShowFilters] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { toast } = useToast();

  // Check for documents on mount
  useEffect(() => {
    checkDocuments();
  }, []);

  const checkDocuments = async () => {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
      setDocumentsCount(docs.length);
      if (docs.length === 0) {
        toast({
          title: "No documents found",
          description: "Please upload some documents first to chat about them.",
          variant: "default",
        });
      }
    } catch (error) {
      console.error("Error checking documents:", error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    try {
      // Map language code to full name
      const languageMap: Record<string, string> = {
        en: "English",
        hi: "Hindi",
        kn: "Kannada",
      };

      // Get selected document info for display
      const searchingDoc = selectedDocument === "all" 
        ? "all documents" 
        : documents.find(d => d.id.toString() === selectedDocument)?.file_name || "selected document";
      
      console.log(`🔍 SEARCHING IN: ${searchingDoc}`);
      console.log(`📄 Document ID: ${selectedDocument === "all" ? "ALL" : selectedDocument}`);

      // Include document filter in request
      const documentIdFilter = selectedDocument === "all" ? null : parseInt(selectedDocument);
      
      const response: ChatResponse = await api.sendChatMessage(
        userMessage.content,
        sessionId,
        languageMap[language] || "English",
        5,
        documentIdFilter // Pass document filter
      );

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        metadata: response.metadata,
      };

      setMessages((prev) => [...prev, botMessage]);

      // Enhanced feedback with document info
      if (response.metadata?.confidence) {
        const confidence = response.metadata.confidence;
        const emoji = confidence === "high" ? "🟢" : 
                     confidence === "medium" ? "🟡" : "🔴";
        
        const searchScope = selectedDocument === "all" 
          ? `${documentsCount} documents` 
          : "1 document";
        
        toast({
          title: `${emoji} Response from ${searchScope}`,
          description: `Confidence: ${confidence} | Sources: ${response.sources?.length || 0}`,
        });
      }

    } catch (error: any) {
      console.error("Chat error:", error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `I encountered an error: ${error.message}. Please try again or check if your documents are uploaded correctly.`,
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);

      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    toast({
      title: "Copied! 📋",
      description: "Message copied to clipboard",
    });
  };

  const getConfidenceColor = (confidence?: string) => {
    switch (confidence) {
      case "high": return "text-green-500";
      case "medium": return "text-yellow-500";
      case "low": return "text-red-500";
      default: return "text-muted-foreground";
    }
  };

  const getConfidenceEmoji = (confidence?: string) => {
    switch (confidence) {
      case "high": return "🟢";
      case "medium": return "🟡";
      case "low": return "🔴";
      default: return "⚪";
    }
  };

  return (
    <div className="min-h-screen pt-16 flex flex-col">
      {/* Enhanced Header with Document Selector */}
      <div className="max-w-4xl mx-auto w-full px-4 pt-4">
        <div className="flex flex-col gap-3 mb-4">
          {/* Top Row: Document Count & Language */}
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                📚 {documentsCount} document{documentsCount !== 1 ? 's' : ''} available
              </span>
              {documentsCount === 0 && (
                <a href="/upload" className="text-sm text-primary hover:underline">
                  Upload now →
                </a>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
                className="gap-2"
              >
                <Filter className="w-4 h-4" />
                {showFilters ? "Hide" : "Show"} Filters
              </Button>
              <LanguageSelector 
                selectedLanguage={language} 
                onLanguageChange={setLanguage} 
              />
            </div>
          </div>

          {/* Filter Panel - Collapsible */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="card-gradient border border-border/50 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <FileText className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-sm">Search Scope</h3>
                  </div>
                  
                  <div className="space-y-2">
                    {/* All Documents Option */}
                    <label className="flex items-center gap-3 p-3 rounded-lg border border-border hover:border-primary/50 cursor-pointer transition-all">
                      <input
                        type="radio"
                        name="document"
                        value="all"
                        checked={selectedDocument === "all"}
                        onChange={(e) => setSelectedDocument(e.target.value)}
                        className="w-4 h-4 text-primary"
                      />
                      <div className="flex-1">
                        <div className="font-medium text-sm">🌐 All Documents</div>
                        <div className="text-xs text-muted-foreground">
                          Search across all {documentsCount} uploaded documents
                        </div>
                      </div>
                    </label>

                    {/* Individual Documents */}
                    {documents.slice(0, 5).map((doc) => (
                      <label 
                        key={doc.id}
                        className="flex items-center gap-3 p-3 rounded-lg border border-border hover:border-primary/50 cursor-pointer transition-all"
                      >
                        <input
                          type="radio"
                          name="document"
                          value={doc.id.toString()}
                          checked={selectedDocument === doc.id.toString()}
                          onChange={(e) => setSelectedDocument(e.target.value)}
                          className="w-4 h-4 text-primary"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-sm truncate">
                            📄 {doc.file_name}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {doc.file_type.toUpperCase()} • {new Date(doc.upload_date).toLocaleDateString()}
                          </div>
                        </div>
                      </label>
                    ))}

                    {documents.length > 5 && (
                      <details className="text-xs text-muted-foreground">
                        <summary className="cursor-pointer hover:text-foreground">
                          Show {documents.length - 5} more documents...
                        </summary>
                        <div className="mt-2 space-y-2">
                          {documents.slice(5).map((doc) => (
                            <label 
                              key={doc.id}
                              className="flex items-center gap-3 p-3 rounded-lg border border-border hover:border-primary/50 cursor-pointer transition-all"
                            >
                              <input
                                type="radio"
                                name="document"
                                value={doc.id.toString()}
                                checked={selectedDocument === doc.id.toString()}
                                onChange={(e) => setSelectedDocument(e.target.value)}
                                className="w-4 h-4 text-primary"
                              />
                              <div className="flex-1 min-w-0">
                                <div className="font-medium text-sm truncate">
                                  📄 {doc.file_name}
                                </div>
                                <div className="text-xs text-muted-foreground">
                                  {doc.file_type.toUpperCase()} • {new Date(doc.upload_date).toLocaleDateString()}
                                </div>
                              </div>
                            </label>
                          ))}
                        </div>
                      </details>
                    )}
                  </div>

                  {/* Current Selection Display */}
                  <div className="mt-3 pt-3 border-t border-border/50">
                    <div className="text-xs text-muted-foreground">
                      Currently searching: {" "}
                      <span className="text-primary font-medium">
                        {selectedDocument === "all" 
                          ? `All ${documentsCount} documents` 
                          : documents.find(d => d.id.toString() === selectedDocument)?.file_name || "Selected document"
                        }
                      </span>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
      
      {/* Chat Container */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 py-8">
          <AnimatePresence initial={false}>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`mb-6 flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className={`flex gap-3 max-w-[85%] ${message.role === "user" ? "flex-row-reverse" : ""}`}>
                  {/* Avatar */}
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ${
                      message.role === "assistant"
                        ? "bg-gradient-to-br from-primary to-secondary"
                        : "bg-muted"
                    }`}
                  >
                    {message.role === "assistant" ? (
                      <span className="text-lg">{getRandomBotEmoji()}</span>
                    ) : (
                      <User className="w-5 h-5 text-muted-foreground" />
                    )}
                  </motion.div>

                  {/* Message Content */}
                  <div
                    className={`rounded-2xl p-4 ${
                      message.role === "assistant"
                        ? "card-gradient border border-border/50"
                        : "bg-primary text-primary-foreground"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    
                    {/* Enhanced Metadata for assistant messages */}
                    {message.role === "assistant" && message.metadata && (
                      <div className="flex items-center gap-3 mt-2 pt-2 border-t border-border/30 text-xs">
                        {message.metadata.confidence && (
                          <span className={`flex items-center gap-1 ${getConfidenceColor(message.metadata.confidence)}`}>
                            {getConfidenceEmoji(message.metadata.confidence)}
                            {message.metadata.confidence}
                          </span>
                        )}
                        {message.metadata.complexity && (
                          <span className="text-muted-foreground">
                            📊 {message.metadata.complexity}
                          </span>
                        )}
                        {message.sources && message.sources.length > 0 && (
                          <span className="text-muted-foreground">
                            📚 {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
                          </span>
                        )}
                        {/* NEW: Show if date match found */}
                        {message.sources?.some((s: any) => s.date_match) && (
                          <span className="flex items-center gap-1 text-green-500">
                            📅 Date match
                          </span>
                        )}
                      </div>
                    )}
                    
                    {/* Enhanced Sources Display */}
                    {message.sources && message.sources.length > 0 && (
                      <details className="mt-3 pt-3 border-t border-border/30">
                        <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground">
                          View {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
                        </summary>
                        <div className="mt-2 space-y-2">
                          {message.sources.slice(0, 3).map((source, idx) => (
                            <div key={idx} className="text-xs bg-muted/50 rounded-lg p-2">
                              <div className="font-medium text-foreground mb-1 flex items-center gap-2">
                                📄 {source.metadata?.file_name || 'Unknown source'}
                                {source.date_match && (
                                  <span className="px-2 py-0.5 bg-green-500/20 text-green-500 rounded-full text-xs">
                                    📅 Date Match
                                  </span>
                                )}
                              </div>
                              <div className="text-muted-foreground line-clamp-2">
                                {source.content?.substring(0, 150)}...
                              </div>
                              {source.relevance_score && (
                                <div className="mt-1 text-primary">
                                  Relevance: {source.relevance_score.toFixed(1)}%
                                </div>
                              )}
                              {source.retrieval_method && (
                                <div className="mt-1 text-xs text-muted-foreground">
                                  Method: {source.retrieval_method}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </details>
                    )}

                    {/* Message Actions */}
                    {message.role === "assistant" && (
                      <div className="flex gap-2 mt-3 pt-3 border-t border-border/30">
                        <button
                          onClick={() => copyMessage(message.content)}
                          className="p-1.5 rounded-lg hover:bg-muted transition-colors"
                          title="Copy message"
                        >
                          <Copy className="w-4 h-4 text-muted-foreground" />
                        </button>
                        <button 
                          className="p-1.5 rounded-lg hover:bg-muted transition-colors"
                          title="Helpful"
                        >
                          <ThumbsUp className="w-4 h-4 text-muted-foreground" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Typing Indicator */}
          <AnimatePresence>
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex items-center gap-3 mb-6"
              >
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                  <Bot className="w-5 h-5 text-primary-foreground" />
                </div>
                <div className="card-gradient border border-border/50 rounded-2xl px-4 py-3">
                  <div className="flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        className="w-2 h-2 bg-primary rounded-full"
                        animate={{ y: [0, -6, 0] }}
                        transition={{
                          duration: 0.6,
                          repeat: Infinity,
                          delay: i * 0.15,
                        }}
                      />
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-border/50 bg-background/80 backdrop-blur-xl p-4">
          <div className="max-w-4xl mx-auto">
            {documentsCount === 0 && (
              <div className="mb-3 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-yellow-600 dark:text-yellow-400">
                  <strong>No documents found.</strong> Upload documents first to chat about them.
                  <a href="/upload" className="ml-2 underline hover:no-underline">
                    Go to Upload →
                  </a>
                </div>
              </div>
            )}
            <div className="relative card-gradient rounded-2xl border border-border/50 p-2">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder={
                  documentsCount > 0 
                    ? "Ask anything... (I understand concepts, not just exact words!)" 
                    : "Please upload documents first..."
                }
                disabled={isTyping || documentsCount === 0}
                className="min-h-[60px] max-h-[200px] border-0 bg-transparent resize-none focus-visible:ring-0 focus-visible:ring-offset-0 pr-14"
                rows={1}
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isTyping || documentsCount === 0}
                variant="hero"
                size="icon"
                className="absolute right-2 bottom-2 h-10 w-10 rounded-xl"
              >
                {isTyping ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground text-center mt-2">
              Press Enter to send, Shift + Enter for new line • Enhanced with smart search
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;