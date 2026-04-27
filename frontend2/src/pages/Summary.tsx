import Navigation from "@/components/Navigation";
import { FileText, Video, Music, RefreshCw, Download, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { api, Document } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface DocumentSummary {
  document_id: number;
  document_name: string;
  summary: string;
  style: string;
  word_count: number;
  compression_ratio: number;
}

interface VideoResult {
  success: boolean;
  url?: string;
  thumbnail?: string;
  error?: string;
}

const Summary = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [summaries, setSummaries] = useState<Map<number, DocumentSummary>>(new Map());
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [summaryStyle, setSummaryStyle] = useState<string>("executive");
  const { toast } = useToast();

  // Add these state variables at the top of Summary component
  const [videoGenerating, setVideoGenerating] = useState(false);
  const [videoResults, setVideoResults] = useState<Map<number, VideoResult>>(new Map());
  const [videoLanguage, setVideoLanguage] = useState("english");
  const [videoDuration, setVideoDuration] = useState(60);
  const [includeSubtitles, setIncludeSubtitles] = useState(true);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
      
      // Load existing summaries from backend
      if (docs.length > 0) {
        await loadExistingSummaries(docs);
      }
    } catch (error) {
      console.error('Error loading documents:', error);
      toast({
        title: "Error",
        description: "Failed to load documents",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadExistingSummaries = async (docs: Document[]) => {
    // Try to get summaries that were generated during upload
    const summaryMap = new Map<number, DocumentSummary>();
    
    for (const doc of docs) {
      try {
        // Check if document has metadata with summary
        if (doc.metadata && typeof doc.metadata === 'object') {
          const metadata = typeof doc.metadata === 'string' 
            ? JSON.parse(doc.metadata) 
            : doc.metadata;
          
          if (metadata.summary) {
            summaryMap.set(doc.id, {
              document_id: doc.id,
              document_name: doc.file_name,
              summary: metadata.summary,
              style: 'executive',
              word_count: metadata.summary.split(' ').length,
              compression_ratio: 0
            });
          }
        }
      } catch (error) {
        console.error(`Error loading summary for doc ${doc.id}:`, error);
      }
    }
    
    setSummaries(summaryMap);
    
    // Auto-select first document
    if (docs.length > 0 && !selectedDocId) {
      setSelectedDocId(docs[0].id);
    }
  };

  const generateNewSummary = async () => {
    if (!selectedDocId) {
      toast({
        title: "No document selected",
        description: "Please select a document to summarize",
        variant: "destructive",
      });
      return;
    }

    setGenerating(true);
    try {
      const result = await api.summarizeDocument(selectedDocId, {
        style: summaryStyle,
        language: "English",
        targetLength: 300,
      });

      const selectedDoc = documents.find(d => d.id === selectedDocId);
      const newSummary: DocumentSummary = {
        document_id: selectedDocId,
        document_name: selectedDoc?.file_name || 'Unknown',
        summary: result.summary,
        style: result.style,
        word_count: result.word_count,
        compression_ratio: result.compression_ratio,
      };

      setSummaries(new Map(summaries.set(selectedDocId, newSummary)));

      toast({
        title: "Summary Generated",
        description: `${summaryStyle} summary created successfully`,
      });
    } catch (error) {
      console.error('Error generating summary:', error);
      toast({
        title: "Error",
        description: "Failed to generate summary",
        variant: "destructive",
      });
    } finally {
      setGenerating(false);
    }
  };

  // Add this function to generate video
  const generateVideo = async () => {
    if (!selectedDocId) {
      toast({
        title: "No document selected",
        description: "Please select a document to generate video",
        variant: "destructive",
      });
      return;
    }

    // Check if we have a summary first
    const currentSummary = summaries.get(selectedDocId);
    if (!currentSummary) {
      toast({
        title: "No summary available",
        description: "Please generate a text summary first",
        variant: "destructive",
      });
      return;
    }

    setVideoGenerating(true);
    try {
      toast({
        title: "Generating Video",
        description: "This may take 1-2 minutes...",
      });

      const result = await api.generateVideo(selectedDocId, {
        language: videoLanguage,
        target_duration: videoDuration,
        include_subtitles: includeSubtitles,
      });

      if (result.success) {
        setVideoResults(new Map(videoResults.set(selectedDocId, result)));
        
        toast({
          title: "Video Generated!",
          description: `${videoDuration}s video created successfully`,
        });
      } else {
        throw new Error(result.error || "Video generation failed");
      }
    } catch (error) {
      console.error('Video generation error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate video",
        variant: "destructive",
      });
    } finally {
      setVideoGenerating(false);
    }
  };

  const downloadSummary = (summary: DocumentSummary) => {
    const content = `# ${summary.document_name} - Summary\n\nStyle: ${summary.style}\nWord Count: ${summary.word_count}\nGenerated: ${new Date().toLocaleString()}\n\n---\n\n${summary.summary}\n`;

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `summary-${summary.document_name.replace(/\.[^/.]+$/, "")}.md`;
    link.click();
    URL.revokeObjectURL(url);

    toast({
      title: "Downloaded",
      description: "Summary saved to your device",
    });
  };

  const currentSummary = selectedDocId ? summaries.get(selectedDocId) : null;
  const currentVideo = selectedDocId ? videoResults.get(selectedDocId) : null;

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-background">
        <Navigation />
        <main className="container mx-auto px-6 pt-24 pb-12">
          <div className="flex items-center justify-center h-64">
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
              <p className="text-muted-foreground">Loading summaries...</p>
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
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-4xl font-bold gradient-text">Summary</h2>
              <p className="text-muted-foreground">
                View comprehensive outputs from your content analysis
              </p>
            </div>
            <Button
              onClick={loadDocuments}
              variant="outline"
              className="border-primary/50"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>

          {documents.length === 0 ? (
            <div className="glass rounded-2xl p-12 text-center">
              <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No Documents Yet</h3>
              <p className="text-muted-foreground mb-6">
                Upload some documents to generate summaries
              </p>
              <Button 
                onClick={() => window.location.href = '/upload'}
                className="bg-gradient-primary hover:opacity-90 transition-opacity"
              >
                Go to Upload
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Text Output - Now Connected */}
              <div className="glass rounded-2xl p-6 glass-hover animate-slide-up lg:col-span-2">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-primary/20 flex items-center justify-center">
                      <FileText className="w-6 h-6 text-primary" />
                    </div>
                    <h3 className="text-xl font-semibold">Text Summary</h3>
                  </div>
                  {currentSummary && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => downloadSummary(currentSummary)}
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                  )}
                </div>

                {/* Document Selector */}
                <div className="mb-4 space-y-3">
                  <div>
                    <label className="text-sm text-muted-foreground mb-2 block">
                      Select Document
                    </label>
                    <Select
                      value={selectedDocId?.toString()}
                      onValueChange={(value) => setSelectedDocId(parseInt(value))}
                    >
                      <SelectTrigger className="glass">
                        <SelectValue placeholder="Choose a document" />
                      </SelectTrigger>
                      <SelectContent>
                        {documents.map((doc) => (
                          <SelectItem key={doc.id} value={doc.id.toString()}>
                            {doc.file_name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex gap-3">
                    <div className="flex-1">
                      <label className="text-sm text-muted-foreground mb-2 block">
                        Summary Style
                      </label>
                      <Select
                        value={summaryStyle}
                        onValueChange={setSummaryStyle}
                      >
                        <SelectTrigger className="glass">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="executive">Executive</SelectItem>
                          <SelectItem value="technical">Technical</SelectItem>
                          <SelectItem value="academic">Academic</SelectItem>
                          <SelectItem value="bullet">Bullet Points</SelectItem>
                          <SelectItem value="narrative">Narrative</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex items-end">
                      <Button
                        onClick={generateNewSummary}
                        disabled={generating || !selectedDocId}
                        className="bg-gradient-primary hover:opacity-90 transition-opacity"
                      >
                        {generating ? (
                          <>
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            Generating...
                          </>
                        ) : (
                          'Generate'
                        )}
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Summary Display */}
                {currentSummary ? (
                  <div className="space-y-4">
                    <div className="bg-background/30 rounded-xl p-4 max-h-96 overflow-y-auto">
                      <div className="flex items-center justify-between mb-3 pb-3 border-b border-border/30">
                        <h4 className="font-medium text-sm text-muted-foreground capitalize">
                          {currentSummary.style} Summary
                        </h4>
                        <div className="flex gap-3 text-xs text-muted-foreground">
                          <span>{currentSummary.word_count} words</span>
                          {currentSummary.compression_ratio > 0 && (
                            <span>{(currentSummary.compression_ratio * 100).toFixed(0)}% of original</span>
                          )}
                        </div>
                      </div>
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">
                        {currentSummary.summary}
                      </p>
                    </div>

                    {/* Quick Actions */}
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          navigator.clipboard.writeText(currentSummary.summary);
                          toast({
                            title: "Copied",
                            description: "Summary copied to clipboard",
                          });
                        }}
                        className="border-primary/30"
                      >
                        📋 Copy
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => downloadSummary(currentSummary)}
                        className="border-primary/30"
                      >
                        💾 Download
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          // Share summary
                          if (navigator.share) {
                            navigator.share({
                              title: `Summary: ${currentSummary.document_name}`,
                              text: currentSummary.summary,
                            });
                          } else {
                            toast({
                              title: "Share not supported",
                              description: "Use copy or download instead",
                            });
                          }
                        }}
                        className="border-primary/30"
                      >
                        🔗 Share
                      </Button>
                    </div>
                  </div>
                ) : selectedDocId ? (
                  <div className="bg-background/30 rounded-xl p-8 text-center">
                    <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground mb-4">
                      No summary available for this document yet
                    </p>
                    <Button
                      onClick={generateNewSummary}
                      disabled={generating}
                      className="bg-gradient-primary hover:opacity-90 transition-opacity"
                    >
                      Generate Summary
                    </Button>
                  </div>
                ) : (
                  <div className="bg-background/30 rounded-xl p-8 text-center">
                    <p className="text-sm text-muted-foreground">
                      Select a document to view or generate its summary
                    </p>
                  </div>
                )}
              </div>

              {/* Video Output - Replaced with functional video controls */}
              <div className="glass rounded-2xl p-6 glass-hover animate-slide-up"
                style={{ animationDelay: "100ms" }}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-xl bg-accent/20 flex items-center justify-center">
                    <Video className="w-6 h-6 text-accent" />
                  </div>
                  <h3 className="text-xl font-semibold">Video Output</h3>
                </div>

                <div className="space-y-4">
                  <div className="bg-background/30 rounded-xl p-4">
                    <label className="text-xs text-muted-foreground mb-2 block">Language</label>
                    <Select value={videoLanguage} onValueChange={setVideoLanguage}>
                      <SelectTrigger className="glass">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="english">English</SelectItem>
                        <SelectItem value="hindi">Hindi</SelectItem>
                        <SelectItem value="spanish">Spanish</SelectItem>
                        <SelectItem value="french">French</SelectItem>
                      </SelectContent>
                    </Select>

                    <div className="mt-3 flex items-center gap-3">
                      <div className="flex-1">
                        <label className="text-xs text-muted-foreground block">Duration (seconds)</label>
                        <input
                          type="number"
                          min={10}
                          max={300}
                          value={videoDuration}
                          onChange={(e) => setVideoDuration(parseInt(e.target.value || '60'))}
                          className="w-full glass rounded-md p-2 mt-1"
                        />
                      </div>

                      <div className="flex items-center gap-2">
                        <input
                          id="subtitles"
                          type="checkbox"
                          checked={includeSubtitles}
                          onChange={() => setIncludeSubtitles(!includeSubtitles)}
                          className="w-4 h-4"
                        />
                        <label htmlFor="subtitles" className="text-xs text-muted-foreground">Include Subtitles</label>
                      </div>
                    </div>

                    <div className="mt-4 flex gap-2">
                      <Button
                        onClick={generateVideo}
                        disabled={videoGenerating || !selectedDocId}
                        className="bg-gradient-primary hover:opacity-90 transition-opacity"
                      >
                        {videoGenerating ? (
                          <>
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            Generating...
                          </>
                        ) : (
                          'Generate Video'
                        )}
                      </Button>

                      {currentVideo && currentVideo.success && currentVideo.url && (
                        <>
                          <a href={currentVideo.url} target="_blank" rel="noreferrer">
                            <Button variant="outline" size="sm" className="border-primary/30">
                              <Play className="w-4 h-4 mr-2" />
                              Play
                            </Button>
                          </a>
                          <a href={currentVideo.url} download>
                            <Button variant="outline" size="sm" className="border-primary/30">
                              <Download className="w-4 h-4 mr-2" />
                              Download
                            </Button>
                          </a>
                        </>
                      )}

                      {currentVideo && !currentVideo.success && (
                        <span className="text-sm text-destructive">{currentVideo.error || 'Failed to generate video'}</span>
                      )}
                    </div>
                  </div>

                  <div className="bg-background/30 rounded-xl p-3">
                    <p className="text-xs text-muted-foreground mb-1">Status</p>
                    <p className="text-sm font-medium">
                      {videoGenerating ? 'Generating video...' : currentVideo ? (currentVideo.success ? 'Video ready' : 'No video generated') : 'No video generated'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Audio Output - Placeholder */}
              <div className="glass rounded-2xl p-6 glass-hover animate-slide-up lg:col-span-2"
                style={{ animationDelay: "200ms" }}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                    <Music className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold">Audio Output</h3>
                </div>
                <div className="space-y-4">
                  <div className="bg-background/30 rounded-xl p-6 flex items-center justify-center">
                    <div className="flex gap-1">
                      {[...Array(20)].map((_, i) => (
                        <div
                          key={i}
                          className="w-1 bg-gradient-primary rounded-full animate-glow"
                          style={{
                            height: `${Math.random() * 40 + 20}px`,
                            animationDelay: `${i * 100}ms`,
                          }}
                        />
                      ))}
                    </div>
                  </div>
                  <div className="bg-background/30 rounded-xl p-3">
                    <p className="text-xs text-muted-foreground mb-1">Coming Soon</p>
                    <p className="text-sm font-medium">Audio summaries with text-to-speech will be available soon</p>
                  </div>
                </div>
              </div>

              {/* Summary Statistics */}
              <div className="glass rounded-2xl p-6 animate-slide-up"
                style={{ animationDelay: "300ms" }}>
                <h4 className="font-semibold mb-4">Summary Statistics</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Total Documents</span>
                    <span className="font-semibold">{documents.length}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Summaries Generated</span>
                    <span className="font-semibold">{summaries.size}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Available Styles</span>
                    <span className="font-semibold">5</span>
                  </div>
                  {currentSummary && (
                    <>
                      <div className="border-t border-border/30 pt-3 mt-3">
                        <p className="text-xs text-muted-foreground mb-2">Current Summary</p>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-muted-foreground">Words</span>
                            <span className="text-sm font-medium">{currentSummary.word_count}</span>
                          </div>
                          {currentSummary.compression_ratio > 0 && (
                            <div className="flex justify-between items-center">
                              <span className="text-xs text-muted-foreground">Compression</span>
                              <span className="text-sm font-medium">
                                {(currentSummary.compression_ratio * 100).toFixed(1)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Summary;
