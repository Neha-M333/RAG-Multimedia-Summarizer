// pages/History.tsx - UPDATED with real backend data
// Place this in: src/pages/History.tsx

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, MessageSquare, FileText, Clock, Filter, Search, Trash2, Eye, Loader2, AlertCircle, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { api, type Document, type Summary } from "@/lib/api";

export const History = () => {
  const [activeTab, setActiveTab] = useState("uploads");
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [chatSessions, setChatSessions] = useState<any[]>([]);
  const { toast } = useToast();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [docsData, summariesData] = await Promise.all([
        api.getDocuments(),
        api.getAllSummaries(),
      ]);
      
      setDocuments(docsData);
      setSummaries(summariesData);
      
      // Get unique chat sessions from summaries
      const sessions = summariesData
        .filter(s => s.summary)
        .map(s => ({
          id: `session_${s.document_id}`,
          title: `Chat about ${s.document_name}`,
          date: s.upload_date,
          document_id: s.document_id,
        }));
      setChatSessions(sessions);
      
    } catch (error: any) {
      toast({
        title: "Error loading history",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (documentId: number) => {
    try {
      await api.deleteDocument(documentId);
      toast({
        title: "Deleted successfully",
        description: "Document removed from history",
      });
      loadData();
    } catch (error: any) {
      toast({
        title: "Delete failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) return "Just now";
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffHours < 48) return "Yesterday";
    
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
  };

  const getFileIcon = (fileType: string) => {
    const icons: Record<string, string> = {
      pdf: "📄",
      word: "📝",
      powerpoint: "📊",
      excel: "📈",
      audio: "🎵",
      video: "🎬",
      image: "🖼️",
      text: "📃",
    };
    return icons[fileType] || "📄";
  };

  const filteredDocuments = documents.filter(doc =>
    doc.file_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredSummaries = summaries.filter(s =>
    s.document_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredChats = chatSessions.filter(chat =>
    chat.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading your history...</p>
        </div>
      </div>
    );
  }

  const tabConfig = [
    { value: "uploads", label: "Uploads", icon: Upload, count: documents.length },
    { value: "chats", label: "Chats", icon: MessageSquare, count: chatSessions.length },
    { value: "summaries", label: "Summaries", icon: FileText, count: summaries.length },
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <span className="inline-block px-4 py-2 rounded-full bg-accent/10 border border-accent/20 text-accent text-sm font-medium mb-4">
            📚 Activity History
          </span>
          <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
            Your History
          </h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Track all your uploads, chats, and summaries in one place.
          </p>
        </motion.div>

        {/* Search and Filter */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-col sm:flex-row gap-4 mb-8"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search history..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-muted/50 border-border/50"
            />
          </div>
          <Button variant="outline" onClick={loadData} className="gap-2">
            <RefreshCcw className="w-4 h-4" />
            Refresh
          </Button>
        </motion.div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <TabsList className="grid w-full max-w-lg mx-auto grid-cols-3 mb-8 bg-muted/50 p-1 rounded-xl">
              {tabConfig.map((tab) => (
                <TabsTrigger
                  key={tab.value}
                  value={tab.value}
                  className="rounded-lg data-[state=active]:bg-gradient-to-r data-[state=active]:from-primary data-[state=active]:to-secondary data-[state=active]:text-primary-foreground transition-all text-sm"
                >
                  <tab.icon className="w-4 h-4 mr-1.5" />
                  {tab.label}
                  <span className="ml-1.5 px-1.5 py-0.5 rounded-full bg-background/20 text-xs">
                    {tab.count}
                  </span>
                </TabsTrigger>
              ))}
            </TabsList>
          </motion.div>

          {/* Uploads History */}
          <TabsContent value="uploads">
            <AnimatePresence mode="wait">
              {filteredDocuments.length === 0 ? (
                <div className="text-center py-12">
                  <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50 text-muted-foreground" />
                  <p className="text-muted-foreground">
                    {searchQuery ? "No uploads found" : "No uploads yet"}
                  </p>
                </div>
              ) : (
                <motion.div
                  key="uploads"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-3"
                >
                  {filteredDocuments.map((item, index) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      whileHover={{ x: 4 }}
                      className="card-gradient rounded-xl border border-border/50 p-4 flex items-center justify-between hover:border-primary/30 transition-all group"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                          <span className="text-lg">{getFileIcon(item.file_type)}</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-foreground text-sm">{item.file_name}</h4>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5">
                            <span>{formatFileSize(item.file_size)}</span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatDate(item.upload_date)}
                            </span>
                            {item.processed && (
                              <span className="text-green-500">✓ Processed</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-8 w-8 p-0"
                          onClick={() => window.location.href = '/chat'}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                          onClick={() => handleDelete(item.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </TabsContent>

          {/* Chats History */}
          <TabsContent value="chats">
            <AnimatePresence mode="wait">
              {filteredChats.length === 0 ? (
                <div className="text-center py-12">
                  <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50 text-muted-foreground" />
                  <p className="text-muted-foreground">
                    {searchQuery ? "No chats found" : "No chat history yet"}
                  </p>
                </div>
              ) : (
                <motion.div
                  key="chats"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-3"
                >
                  {filteredChats.map((item, index) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      whileHover={{ x: 4 }}
                      className="card-gradient rounded-xl border border-border/50 p-4 flex items-center justify-between hover:border-secondary/30 transition-all group"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                          <span className="text-lg">🤖</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-foreground text-sm">{item.title}</h4>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatDate(item.date)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-8 w-8 p-0"
                          onClick={() => window.location.href = '/chat'}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </TabsContent>

          {/* Summaries History */}
          <TabsContent value="summaries">
            <AnimatePresence mode="wait">
              {filteredSummaries.length === 0 ? (
                <div className="text-center py-12">
                  <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50 text-muted-foreground" />
                  <p className="text-muted-foreground">
                    {searchQuery ? "No summaries found" : "No summaries yet"}
                  </p>
                </div>
              ) : (
                <motion.div
                  key="summaries"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-3"
                >
                  {filteredSummaries.map((item, index) => (
                    <motion.div
                      key={item.document_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      whileHover={{ x: 4 }}
                      className="card-gradient rounded-xl border border-border/50 p-4 flex items-center justify-between hover:border-accent/30 transition-all group"
                    >
                      <div className="flex items-center gap-4 flex-1 min-w-0">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                          <span className="text-lg">
                            {item.has_video ? "🎥" : "📝"}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-foreground text-sm truncate">
                            {item.document_name}
                          </h4>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5">
                            {item.summary && (
                              <span>{item.summary.word_count} words</span>
                            )}
                            {item.has_video && (
                              <span className="text-secondary">With Video</span>
                            )}
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatDate(item.upload_date)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-8 w-8 p-0"
                          onClick={() => window.location.href = '/summary'}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default History;