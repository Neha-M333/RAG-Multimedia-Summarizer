import Navigation from "@/components/Navigation";
import { Clock, FileText, Video, Music, Trash2, Download, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { api, Document } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";

const History = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { toast } = useToast();

  const sessionId = localStorage.getItem('glassvault_session_id') || '';

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadDocuments(),
        loadChatHistory(),
        loadAnalytics(),
      ]);
    } catch (error) {
      console.error('Error loading data:', error);
      toast({
        title: "Error",
        description: "Failed to load history data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadDocuments = async () => {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
    }
  };

  const loadChatHistory = async () => {
    try {
      if (sessionId) {
        const { messages } = await api.getChatHistory(sessionId, 100);
        setChatHistory(messages);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const data = await api.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadAllData();
    setRefreshing(false);
    toast({
      title: "Refreshed",
      description: "History data has been updated",
    });
  };

  const handleDeleteDocument = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
      await api.deleteDocument(id);
      toast({
        title: "Deleted",
        description: `${name} has been deleted`,
      });
      await loadDocuments();
      await loadAnalytics();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete document",
        variant: "destructive",
      });
    }
  };

  const exportChatHistory = () => {
    const dataStr = JSON.stringify(chatHistory, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `chat-history-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: "Exported",
      description: "Chat history downloaded",
    });
  };

  const getFileIcon = (type: string) => {
    const iconMap: Record<string, any> = {
      pdf: FileText,
      excel: FileText,
      audio: Music,
      video: Video,
      text: FileText,
    };
    return iconMap[type] || FileText;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-background">
        <Navigation />
        <main className="container mx-auto px-6 pt-24 pb-12">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center justify-center h-64">
              <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                <p className="text-muted-foreground">Loading history...</p>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-background">
      <Navigation />
      <main className="container mx-auto px-6 pt-24 pb-12">
        <div className="max-w-6xl mx-auto animate-fade-in">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-4xl font-bold gradient-text">History</h2>
              <p className="text-muted-foreground">
                View your documents, conversations, and analytics
              </p>
            </div>
            <Button
              onClick={handleRefresh}
              disabled={refreshing}
              variant="outline"
              className="border-primary/50"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>

          {/* Analytics Overview */}
          {analytics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <Card className="glass border-primary/20">
                <CardHeader className="pb-3">
                  <CardDescription>Total Documents</CardDescription>
                  <CardTitle className="text-3xl gradient-text">
                    {analytics.documents?.total || 0}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {(analytics.documents?.total_size_mb || 0).toFixed(1)} MB total
                  </p>
                </CardContent>
              </Card>

              <Card className="glass border-accent/20">
                <CardHeader className="pb-3">
                  <CardDescription>Chat Messages</CardDescription>
                  <CardTitle className="text-3xl gradient-text">
                    {analytics.chat?.total_messages || 0}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {(analytics.chat?.avg_response_time || 0).toFixed(2)}s avg response
                  </p>
                </CardContent>
              </Card>

              <Card className="glass border-primary/20">
                <CardHeader className="pb-3">
                  <CardDescription>Cache Hit Rate</CardDescription>
                  <CardTitle className="text-3xl gradient-text">
                    {((analytics.performance?.cache_hit_rate || 0) * 100).toFixed(0)}%
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {analytics.performance?.queries_executed || 0} queries
                  </p>
                </CardContent>
              </Card>

              <Card className="glass border-accent/20">
                <CardHeader className="pb-3">
                  <CardDescription>Total Cost</CardDescription>
                  <CardTitle className="text-3xl gradient-text">
                    ${(analytics.chat?.total_cost || 0).toFixed(2)}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {(analytics.chat?.total_tokens || 0).toLocaleString()} tokens
                  </p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Tabs for different views */}
          <Tabs defaultValue="documents" className="space-y-6">
            <TabsList className="glass">
              <TabsTrigger value="documents">
                <FileText className="w-4 h-4 mr-2" />
                Documents ({documents.length})
              </TabsTrigger>
              <TabsTrigger value="chat">
                <Clock className="w-4 h-4 mr-2" />
                Conversations ({chatHistory.length})
              </TabsTrigger>
              <TabsTrigger value="analytics">
                📊 Analytics
              </TabsTrigger>
            </TabsList>

            {/* Documents Tab */}
            <TabsContent value="documents" className="space-y-4">
              {documents.length === 0 ? (
                <Card className="glass">
                  <CardContent className="pt-6">
                    <div className="text-center py-12">
                      <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-xl font-semibold mb-2">No documents yet</h3>
                      <p className="text-muted-foreground">
                        Upload your first document to get started
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                documents.map((doc, index) => {
                  const Icon = getFileIcon(doc.file_type);
                  return (
                    <div
                      key={doc.id}
                      className="glass rounded-xl p-6 glass-hover animate-slide-up"
                      style={{ animationDelay: `${index * 50}ms` }}
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-lg bg-gradient-primary/20 flex items-center justify-center flex-shrink-0">
                          <Icon className="w-6 h-6 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-lg truncate">{doc.file_name}</h3>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                            <span className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              {formatDate(doc.upload_date)}
                            </span>
                            <span className="capitalize px-2 py-0.5 rounded-full glass text-xs">
                              {doc.file_type}
                            </span>
                            {doc.processed ? (
                              <span className="text-green-500 text-xs">✓ Processed</span>
                            ) : (
                              <span className="text-yellow-500 text-xs">⏳ Processing...</span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteDocument(doc.id, doc.file_name)}
                            className="hover:bg-destructive/20 hover:text-destructive"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </TabsContent>

            {/* Chat History Tab */}
            <TabsContent value="chat" className="space-y-4">
              <div className="flex justify-end mb-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={exportChatHistory}
                  disabled={chatHistory.length === 0}
                  className="border-primary/50"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export Chat History
                </Button>
              </div>

              {chatHistory.length === 0 ? (
                <Card className="glass">
                  <CardContent className="pt-6">
                    <div className="text-center py-12">
                      <Clock className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-xl font-semibold mb-2">No conversations yet</h3>
                      <p className="text-muted-foreground">
                        Start chatting with your documents to see history here
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                chatHistory.map((item, index) => (
                  <div
                    key={index}
                    className="glass rounded-xl p-6 space-y-4 animate-slide-up"
                    style={{ animationDelay: `${index * 30}ms` }}
                  >
                    <div className="flex items-start gap-3">
                      <div className="text-sm text-muted-foreground">
                        {new Date(item.timestamp).toLocaleString()}
                      </div>
                      {item.language && (
                        <span className="px-2 py-0.5 rounded-full glass text-xs capitalize">
                          {item.language}
                        </span>
                      )}
                    </div>

                    {/* User Message */}
                    <div className="pl-4 border-l-2 border-accent">
                      <p className="text-sm font-medium text-accent mb-1">You asked:</p>
                      <p className="text-sm">{item.user_message}</p>
                    </div>

                    {/* Assistant Response */}
                    <div className="pl-4 border-l-2 border-primary">
                      <p className="text-sm font-medium text-primary mb-1">AI responded:</p>
                      <p className="text-sm line-clamp-3">{item.assistant_message}</p>
                    </div>

                    {/* Metadata */}
                    {(item.query_complexity || item.confidence_level || item.source_documents) && (
                      <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2 border-t border-border/30">
                        {item.query_complexity && (
                          <span>Complexity: {item.query_complexity}</span>
                        )}
                        {item.confidence_level && (
                          <span className="flex items-center gap-1">
                            Confidence: 
                            <span className={`w-2 h-2 rounded-full ${
                              item.confidence_level === 'high' ? 'bg-green-500' :
                              item.confidence_level === 'medium' ? 'bg-yellow-500' :
                              'bg-red-500'
                            }`} />
                            {item.confidence_level}
                          </span>
                        )}
                        {item.source_documents && (
                            <span>
                              📚 {Array.isArray(item.source_documents)
                                ? item.source_documents.length
                                : (() => {
                                    try {
                                      return JSON.parse(item.source_documents).length;
                                    } catch {
                                      return 0;
                                    }
                                  })()} sources
                            </span>
                          )}

                        {item.response_time && (
                          <span>⏱️ {item.response_time.toFixed(2)}s</span>
                        )}
                      </div>
                    )}
                  </div>
                ))
              )}
            </TabsContent>

            {/* Analytics Tab */}
            <TabsContent value="analytics" className="space-y-6">
              {analytics ? (
                <>
                  {/* Document Analytics */}
                  <Card className="glass">
                    <CardHeader>
                      <CardTitle>Document Analytics</CardTitle>
                      <CardDescription>Breakdown of your uploaded documents</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {analytics.documents?.by_type && Object.entries(analytics.documents.by_type).map(([type, count]: [string, any]) => (
                          <div key={type} className="flex items-center justify-between">
                            <span className="capitalize">{type}</span>
                            <div className="flex items-center gap-3">
                              <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-gradient-primary"
                                  style={{
                                    width: `${(count / analytics.documents.total) * 100}%`
                                  }}
                                />
                              </div>
                              <span className="text-sm font-medium w-12 text-right">{count}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Query Complexity */}
                  {analytics.chat?.complexity_distribution && (
                    <Card className="glass">
                      <CardHeader>
                        <CardTitle>Query Complexity Distribution</CardTitle>
                        <CardDescription>How complex your questions have been</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {Object.entries(analytics.chat.complexity_distribution).map(([level, count]: [string, any]) => (
                            <div key={level} className="flex items-center justify-between">
                              <span className="capitalize">{level}</span>
                              <div className="flex items-center gap-3">
                                <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                                  <div
                                    className="h-full bg-gradient-accent"
                                    style={{
                                      width: `${(count / analytics.chat.total_messages) * 100}%`
                                    }}
                                  />
                                </div>
                                <span className="text-sm font-medium w-12 text-right">{count}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Performance Metrics */}
                  <Card className="glass">
                    <CardHeader>
                      <CardTitle>System Performance</CardTitle>
                      <CardDescription>Cache efficiency and query statistics</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-6">
                        <div>
                          <p className="text-sm text-muted-foreground mb-2">Cache Hit Rate</p>
                          <div className="flex items-center gap-3">
                            <div className="flex-1 h-3 bg-muted rounded-full overflow-hidden">
                              <div
                                className="h-full bg-green-500"
                                style={{
                                  width: `${(analytics.performance?.cache_hit_rate || 0) * 100}%`
                                }}
                              />
                            </div>
                            <span className="text-lg font-bold">
                              {((analytics.performance?.cache_hit_rate || 0) * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground mb-2">Total Queries</p>
                          <p className="text-3xl font-bold gradient-text">
                            {analytics.performance?.queries_executed || 0}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </>
              ) : (
                <Card className="glass">
                  <CardContent className="pt-6">
                    <div className="text-center py-12">
                      <p className="text-muted-foreground">No analytics data available</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
};

export default History;