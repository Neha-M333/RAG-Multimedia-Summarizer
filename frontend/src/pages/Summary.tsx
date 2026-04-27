// pages/Summary.tsx - FIXED: Displays full summary text

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, Video, Clock, Download, Share2, BookOpen, Film, Loader2, AlertCircle, Play, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LanguageSelector } from "@/components/LanguageSelector";
import { useToast } from "@/hooks/use-toast";
import { api, type Summary as SummaryType } from "@/lib/api";

export const Summary = () => {
  const [activeTab, setActiveTab] = useState("text");
  const [language, setLanguage] = useState("en");
  const [summaries, setSummaries] = useState<SummaryType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedSummary, setExpandedSummary] = useState<number | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    loadSummaries();
  }, []);

  const loadSummaries = async () => {
    try {
      setIsLoading(true);
      const data = await api.getAllSummaries();
      console.log('📥 Loaded summaries:', data); // Debug log
      setSummaries(data);
    } catch (error: any) {
      toast({
        title: "Error loading summaries",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // ✅ Filter summaries properly
  const textSummaries = summaries.filter(s => s.summary && s.summary.summary);
  const videoSummaries = summaries.filter(s => s.has_video);

  const getFileEmoji = (fileType: string) => {
    const emojiMap: Record<string, string> = {
      pdf: "📄",
      word: "📝",
      powerpoint: "📊",
      excel: "📈",
      audio: "🎵",
      video: "🎬",
      image: "🖼️",
      text: "📃",
    };
    return emojiMap[fileType] || "📄";
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

  const downloadSummary = (summary: SummaryType) => {
    if (!summary.summary?.summary) return;
    
    const content = `Summary of ${summary.document_name}\n\nGenerated: ${new Date(summary.summary.created_date).toLocaleString()}\nLanguage: ${summary.summary.language}\n\n${summary.summary.summary}`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${summary.document_name}_summary.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: "Downloaded! 📥",
      description: "Summary saved to your downloads",
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied! 📋",
      description: "Summary copied to clipboard",
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading your summaries...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex justify-end mb-4">
            <LanguageSelector selectedLanguage={language} onLanguageChange={setLanguage} />
          </div>
          <span className="inline-block px-4 py-2 rounded-full bg-secondary/10 border border-secondary/20 text-secondary text-sm font-medium mb-4">
            ✨ Your Summaries
          </span>
          <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
            Summary Library
          </h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            {summaries.length > 0 
              ? `View all your ${summaries.length} summaries in one place.`
              : "No summaries yet. Upload documents to get started!"
            }
          </p>
        </motion.div>

        {summaries.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <div className="w-20 h-20 rounded-2xl bg-muted/50 flex items-center justify-center mx-auto mb-4">
              <FileText className="w-10 h-10 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No summaries yet</h3>
            <p className="text-muted-foreground mb-6">Upload documents to generate summaries</p>
            <a href="/upload">
              <Button variant="hero">
                Upload Documents
              </Button>
            </a>
          </motion.div>
        ) : (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8 bg-muted/50 p-1 rounded-xl">
                <TabsTrigger
                  value="text"
                  className="rounded-lg data-[state=active]:bg-gradient-to-r data-[state=active]:from-primary data-[state=active]:to-secondary data-[state=active]:text-primary-foreground transition-all"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Text Summary
                  <span className="ml-2 px-2 py-0.5 rounded-full bg-background/20 text-xs">
                    {textSummaries.length}
                  </span>
                </TabsTrigger>
                <TabsTrigger
                  value="video"
                  className="rounded-lg data-[state=active]:bg-gradient-to-r data-[state=active]:from-secondary data-[state=active]:to-accent data-[state=active]:text-secondary-foreground transition-all"
                >
                  <Video className="w-4 h-4 mr-2" />
                  Video Summary
                  <span className="ml-2 px-2 py-0.5 rounded-full bg-background/20 text-xs">
                    {videoSummaries.length}
                  </span>
                </TabsTrigger>
              </TabsList>
            </motion.div>

            {/* Text Summaries */}
            <TabsContent value="text">
              <AnimatePresence mode="wait">
                <motion.div
                  key="text"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="space-y-4"
                >
                  {textSummaries.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                      <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>No text summaries yet</p>
                      <p className="text-sm mt-2">Enable "Generate Summary" when uploading</p>
                    </div>
                  ) : (
                    textSummaries.map((item, index) => {
                      const isExpanded = expandedSummary === item.document_id;
                      const summaryText = item.summary?.summary || "No summary available";
                      const previewText = summaryText.length > 200 
                        ? summaryText.substring(0, 200) + "..." 
                        : summaryText;

                      return (
                        <motion.div
                          key={item.document_id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          whileHover={{ y: -4 }}
                          className="card-gradient rounded-2xl border border-border/50 p-6 hover:border-primary/30 transition-all group"
                        >
                          <div className="flex items-start gap-4">
                            <motion.div
                              whileHover={{ scale: 1.1, rotate: 10 }}
                              className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0"
                            >
                              <span className="text-2xl">{getFileEmoji(item.file_type)}</span>
                            </motion.div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-2">
                                <h3 className="font-display font-semibold text-foreground">
                                  {item.document_name}
                                </h3>
                                <span className="flex items-center gap-1 text-xs text-muted-foreground">
                                  <Clock className="w-3 h-3" />
                                  {formatDate(item.upload_date)}
                                </span>
                              </div>

                              {/* ✅ FIXED: Display full summary with expand/collapse */}
                              <div className="mb-3">
                                <p className="text-muted-foreground text-sm leading-relaxed whitespace-pre-wrap">
                                  {isExpanded ? summaryText : previewText}
                                </p>
                                {summaryText.length > 200 && (
                                  <button
                                    onClick={() => setExpandedSummary(isExpanded ? null : item.document_id)}
                                    className="text-primary text-xs mt-2 hover:underline flex items-center gap-1"
                                  >
                                    <Eye className="w-3 h-3" />
                                    {isExpanded ? "Show less" : "Read full summary"}
                                  </button>
                                )}
                              </div>

                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                  <span className="flex items-center gap-1">
                                    <BookOpen className="w-3 h-3" />
                                    {item.summary?.word_count || 0} words
                                  </span>
                                  <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                                    {item.summary?.language?.toUpperCase() || 'EN'}
                                  </span>
                                </div>
                                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                  <Button 
                                    variant="ghost" 
                                    size="sm"
                                    onClick={() => copyToClipboard(summaryText)}
                                    title="Copy summary"
                                  >
                                    <Share2 className="w-4 h-4" />
                                  </Button>
                                  <Button 
                                    variant="ghost" 
                                    size="sm"
                                    onClick={() => downloadSummary(item)}
                                    title="Download summary"
                                  >
                                    <Download className="w-4 h-4" />
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      );
                    })
                  )}
                </motion.div>
              </AnimatePresence>
            </TabsContent>

            {/* Video Summaries */}
            <TabsContent value="video">
              <AnimatePresence mode="wait">
                <motion.div
                  key="video"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="grid md:grid-cols-2 gap-4"
                >
                  {videoSummaries.length === 0 ? (
                    <div className="col-span-2 text-center py-12 text-muted-foreground">
                      <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>No video summaries yet</p>
                      <p className="text-sm mt-2">Enable "Generate Video" when uploading documents</p>
                    </div>
                  ) : (
                    videoSummaries.map((item, index) => (
                      <motion.div
                        key={item.document_id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        whileHover={{ y: -4 }}
                        className="card-gradient rounded-2xl border border-border/50 overflow-hidden hover:border-secondary/30 transition-all group"
                      >
                        {/* Video Thumbnail */}
                        <div className="relative h-40 bg-gradient-to-br from-secondary/20 to-accent/20 flex items-center justify-center">
                          <motion.div
                            whileHover={{ scale: 1.1 }}
                            className="w-16 h-16 rounded-full bg-background/80 backdrop-blur-sm flex items-center justify-center cursor-pointer"
                            onClick={() => window.open(api.getVideoUrl(item.video_name!), '_blank')}
                          >
                            <Play className="w-8 h-8 text-primary" />
                          </motion.div>
                          <span className="absolute top-2 right-2 px-2 py-1 rounded-lg bg-background/80 backdrop-blur-sm text-xs font-medium">
                            {getFileEmoji(item.file_type)}
                          </span>
                          {item.video_name && (
                            <a
                              href={api.getVideoUrl(item.video_name)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="absolute bottom-2 right-2 px-2 py-1 rounded-lg bg-secondary/80 backdrop-blur-sm text-xs font-medium hover:bg-secondary transition-colors"
                            >
                              <Film className="w-3 h-3 inline mr-1" />
                              Watch
                            </a>
                          )}
                        </div>
                        
                        <div className="p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-display font-semibold text-foreground text-sm line-clamp-1">
                              {item.document_name}
                            </h3>
                          </div>
                          {item.summary?.summary && (
                            <p className="text-muted-foreground text-xs leading-relaxed mb-3 line-clamp-2">
                              {item.summary.summary}
                            </p>
                          )}
                          <div className="flex items-center justify-between">
                            <span className="flex items-center gap-1 text-xs text-muted-foreground">
                              <Clock className="w-3 h-3" />
                              {formatDate(item.upload_date)}
                            </span>
                            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                className="h-8 w-8 p-0"
                                onClick={() => window.open(api.getVideoUrl(item.video_name!), '_blank')}
                                title="Watch video"
                              >
                                <Play className="w-3 h-3" />
                              </Button>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                className="h-8 w-8 p-0"
                                onClick={() => item.summary && downloadSummary(item)}
                                title="Download summary"
                              >
                                <Download className="w-3 h-3" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  )}
                </motion.div>
              </AnimatePresence>
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  );
};

export default Summary;