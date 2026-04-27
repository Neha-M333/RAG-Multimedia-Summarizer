import Navigation from "@/components/Navigation";
import { Send, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState, useEffect, useRef } from "react";
import { api, ChatMessage } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const Chat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("English");
  const [sessionId] = useState(() => {
    // Get or create session ID
    const stored = localStorage.getItem('glassvault_session_id');
    if (stored) return stored;
    const newId = crypto.randomUUID();
    localStorage.setItem('glassvault_session_id', newId);
    return newId;
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Load chat history on mount
  useEffect(() => {
    loadChatHistory();
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const { messages: history } = await api.getChatHistory(sessionId, 50);
      
      // Convert to our message format
      const formattedMessages: ChatMessage[] = [];
      history.forEach(item => {
        formattedMessages.push({
          role: 'user',
          content: item.user_message,
          timestamp: item.timestamp,
        });
        formattedMessages.push({
          role: 'assistant',
          content: item.assistant_message,
          timestamp: item.timestamp,
          sources: item.source_documents,
        });
      });
      
      setMessages(formattedMessages);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await api.sendMessage(input, sessionId, {
        language: language,
        topK: 5,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        confidence: response.confidence,
        complexity: response.complexity,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
      
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to send message",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    toast({
      title: "Chat Cleared",
      description: "Your conversation has been cleared locally",
    });
  };

  return (
    <div className="min-h-screen bg-gradient-background">
      <Navigation />
      <main className="container mx-auto px-6 pt-24 pb-12">
        <div className="max-w-4xl mx-auto h-[calc(100vh-12rem)] flex flex-col animate-fade-in">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-4xl font-bold gradient-text">Chat</h2>
              <p className="text-muted-foreground">
                Ask questions about your uploaded content
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={clearChat}
              className="border-primary/50"
            >
              Clear Chat
            </Button>
          </div>

          {/* Messages */}
          <div className="flex-1 glass rounded-2xl p-6 overflow-y-auto mb-4 space-y-4">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <Bot className="w-16 h-16 text-primary/50 mb-4" />
                <h3 className="text-xl font-semibold mb-2">Start a Conversation</h3>
                <p className="text-muted-foreground max-w-md">
                  Ask me anything about your uploaded documents. I can summarize, answer questions, and help you find information.
                </p>
                
                <div className="grid grid-cols-2 gap-3 mt-8">
                  <Button
                    variant="outline"
                    className="text-left border-primary/30"
                    onClick={() => setInput("Summarize all documents")}
                  >
                    📄 Summarize all documents
                  </Button>
                  <Button
                    variant="outline"
                    className="text-left border-primary/30"
                    onClick={() => setInput("What are the main topics?")}
                  >
                    🔍 What are the main topics?
                  </Button>
                  <Button
                    variant="outline"
                    className="text-left border-primary/30"
                    onClick={() => setInput("Extract key findings")}
                  >
                    📊 Extract key findings
                  </Button>
                  <Button
                    variant="outline"
                    className="text-left border-primary/30"
                    onClick={() => setInput("Generate important questions")}
                  >
                    ❓ Generate questions
                  </Button>
                </div>
              </div>
            ) : (
              <>
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex gap-4 ${
                      message.role === "user" ? "flex-row-reverse" : ""
                    }`}
                  >
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.role === "assistant"
                          ? "bg-gradient-primary"
                          : "bg-gradient-accent"
                      }`}
                    >
                      {message.role === "assistant" ? (
                        <Bot className="w-5 h-5" />
                      ) : (
                        <User className="w-5 h-5" />
                      )}
                    </div>
                    <div
                      className={`flex-1 glass rounded-xl p-4 ${
                        message.role === "user" ? "bg-secondary/50" : ""
                      }`}
                    >
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">
                        {message.content}
                      </p>
                      
                      {/* Show metadata for assistant messages */}
                      {message.role === "assistant" && (message.confidence || message.sources) && (
                        <div className="mt-3 pt-3 border-t border-border/50">
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            {message.confidence && (
                              <span className="flex items-center gap-1">
                                <span className={`w-2 h-2 rounded-full ${
                                  message.confidence === 'high' ? 'bg-green-500' :
                                  message.confidence === 'medium' ? 'bg-yellow-500' :
                                  'bg-red-500'
                                }`} />
                                Confidence: {message.confidence}
                              </span>
                            )}
                            {message.sources && message.sources.length > 0 && (
                              <span>📚 {message.sources.length} sources</span>
                            )}
                          </div>
                          
                          {/* Show sources */}
                          {message.sources && message.sources.length > 0 && (
                            <details className="mt-2">
                              <summary className="text-xs text-primary cursor-pointer hover:underline">
                                View Sources
                              </summary>
                              <div className="mt-2 space-y-2">
                                {message.sources.slice(0, 3).map((source, i) => (
                                  <div key={i} className="text-xs glass rounded p-2">
                                    <p className="font-medium text-primary mb-1">
                                      {source.metadata.file_name || 'Unknown'}
                                      {source.relevance_score && (
                                        <span className="ml-2 text-muted-foreground">
                                          ({source.relevance_score.toFixed(0)}% relevant)
                                        </span>
                                      )}
                                    </p>
                                    <p className="text-muted-foreground line-clamp-2">
                                      {source.content}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            </details>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex gap-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-primary flex items-center justify-center">
                      <Bot className="w-5 h-5" />
                    </div>
                    <div className="flex-1 glass rounded-xl p-4">
                      <div className="flex gap-2">
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input */}
          <div className="glass rounded-2xl p-4 flex gap-2">
            <Input
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              className="flex-1 bg-background/50 border-border/50"
            />
            <Button 
              className="bg-gradient-primary hover:opacity-90 transition-opacity"
              onClick={sendMessage}
              disabled={loading || !input.trim()}
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Chat;