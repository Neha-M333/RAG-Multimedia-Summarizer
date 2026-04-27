// pages/Upload.tsx - FIXED: Language selection and subtitle control

import { useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload as UploadIcon, FileText, Video, Image, Music, File, X, CloudUpload, Loader2, CheckCircle, XCircle, AlertCircle, Wifi, WifiOff, Eye, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";

const fileTypes = [
  { icon: FileText, label: "Documents", extensions: "PDF, DOC, TXT", color: "text-primary" },
  { icon: Video, label: "Videos", extensions: "MP4, AVI, MOV", color: "text-secondary" },
  { icon: Image, label: "Images", extensions: "PNG, JPG, GIF", color: "text-accent" },
  { icon: Music, label: "Audio", extensions: "MP3, WAV, M4A", color: "text-primary" },
];

interface UploadedFile {
  file: File;
  name: string;
  size: string;
  type: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  result?: any;
  error?: string;
  progress?: number;
}

export const Upload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  
  // ✅ FIX: Use language codes that backend expects
  const [language, setLanguage] = useState("english");  // "english", "hindi", or "kannada"
  const [summaryStyle, setSummaryStyle] = useState("executive");
  const [generateVideo, setGenerateVideo] = useState(false);
  const [includeSubtitles, setIncludeSubtitles] = useState(false);
  
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [isCheckingConnection, setIsCheckingConnection] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    setIsCheckingConnection(true);
    try {
      const connected = await api.testConnection();
      setIsConnected(connected);
      
      if (!connected) {
        toast({
          title: "⚠️ Backend not connected",
          description: "Make sure your Python backend is running on http://localhost:8000",
          variant: "destructive",
          duration: 10000,
        });
      } else {
        toast({
          title: "✅ Connected to backend",
          description: "Ready to upload files",
        });
      }
    } catch (error) {
      setIsConnected(false);
      console.error('Connection check failed:', error);
    } finally {
      setIsCheckingConnection(false);
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      handleFiles(files);
    }
  };

  const handleFiles = (files: File[]) => {
    const newFiles: UploadedFile[] = files.map((file) => ({
      file,
      name: file.name,
      size: formatFileSize(file.size),
      type: getFileType(file.name),
      status: 'pending',
      progress: 0,
    }));

    setUploadedFiles((prev) => [...prev, ...newFiles]);
    toast({
      title: "Files added! 📁",
      description: `${files.length} file(s) ready for upload`,
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const getFileType = (name: string) => {
    const ext = name.split(".").pop()?.toLowerCase();
    if (["pdf", "doc", "docx", "txt", "md"].includes(ext || "")) return "document";
    if (["mp4", "avi", "mov", "mkv"].includes(ext || "")) return "video";
    if (["png", "jpg", "jpeg", "gif"].includes(ext || "")) return "image";
    if (["mp3", "wav", "m4a"].includes(ext || "")) return "audio";
    return "file";
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case "document": return FileText;
      case "video": return Video;
      case "image": return Image;
      case "audio": return Music;
      default: return File;
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (!isConnected) {
      toast({
        title: "❌ Not connected to backend",
        description: "Please make sure your Python backend is running and try reconnecting.",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    
    for (let i = 0; i < uploadedFiles.length; i++) {
      const fileData = uploadedFiles[i];
      
      if (fileData.status !== 'pending') continue;
      
      setUploadedFiles(prev => {
        const updated = [...prev];
        updated[i] = { ...updated[i], status: 'uploading', progress: 10 };
        return updated;
      });

      try {
        const progressInterval = setInterval(() => {
          setUploadedFiles(prev => {
            const updated = [...prev];
            if (updated[i].progress !== undefined && updated[i].progress! < 90) {
              updated[i] = { ...updated[i], progress: updated[i].progress! + 10 };
            }
            return updated;
          });
        }, 300);

        console.log('🚀 Starting upload for:', fileData.name);
        console.log('   Language:', language);
        console.log('   Include Subtitles:', includeSubtitles);

        // ✅ CRITICAL FIX: Pass language and includeSubtitles correctly
        const result = await api.uploadFile(fileData.file, {
          generateSummary: true,
          summaryStyle,
          language,              // ✅ Pass the language ("english", "hindi", or "kannada")
          generateVideo,
          includeSubtitles,      // ✅ Pass subtitle setting
        });

        clearInterval(progressInterval);

        console.log('✅ Upload completed:', result);
        console.log('   Summary language:', result.summary?.language);
        console.log('   Video info:', result.video_info);

        setUploadedFiles(prev => {
          const updated = [...prev];
          updated[i] = { ...updated[i], status: 'success', result, progress: 100 };
          return updated;
        });

        // Show language-specific toast
        const languageNames = {
          english: "English",
          hindi: "Hindi (हिंदी)",
          kannada: "Kannada (ಕನ್ನಡ)"
        };

        if (result.summary?.text) {
          toast({
            title: `✅ ${fileData.name} processed!`,
            description: `${languageNames[language as keyof typeof languageNames]} summary: ${result.summary.text.substring(0, 80)}...`,
            duration: 5000,
          });
        } else {
          toast({
            title: `✅ ${fileData.name} processed!`,
            description: `Processed ${result.chunks_count} chunks in ${languageNames[language as keyof typeof languageNames]}`,
          });
        }

      } catch (error: any) {
        console.error('❌ Upload failed for:', fileData.name, error);

        setUploadedFiles(prev => {
          const updated = [...prev];
          updated[i] = { 
            ...updated[i], 
            status: 'error',
            error: error.message,
            progress: 0
          };
          return updated;
        });

        toast({
          title: `❌ Error: ${fileData.name}`,
          description: error.message,
          variant: "destructive",
          duration: 8000,
        });

        if (error.message.includes('Failed to fetch') || error.message.includes('Cannot connect')) {
          setIsConnected(false);
        }
      }
    }

    setIsUploading(false);
    
    const successCount = uploadedFiles.filter(f => f.status === 'success').length;
    if (successCount > 0) {
      toast({
        title: "🎉 Upload complete!",
        description: `Successfully processed ${successCount} file(s). Check Summary page to view results.`,
        duration: 5000,
      });
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Connection Status */}
        {!isCheckingConnection && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`mb-6 p-4 rounded-xl border flex items-center justify-between ${
              isConnected 
                ? "bg-green-500/10 border-green-500/20" 
                : "bg-red-500/10 border-red-500/20"
            }`}
          >
            <div className="flex items-center gap-3">
              {isConnected ? (
                <>
                  <Wifi className="w-5 h-5 text-green-500" />
                  <div>
                    <p className="text-sm font-medium text-green-500">Backend Connected</p>
                    <p className="text-xs text-muted-foreground">Ready to upload files</p>
                  </div>
                </>
              ) : (
                <>
                  <WifiOff className="w-5 h-5 text-red-500" />
                  <div>
                    <p className="text-sm font-medium text-red-500">Backend Not Connected</p>
                    <p className="text-xs text-muted-foreground">
                      Make sure Python backend is running on http://localhost:8000
                    </p>
                  </div>
                </>
              )}
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={checkBackendConnection}
              disabled={isCheckingConnection}
            >
              {isCheckingConnection ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                "Check Connection"
              )}
            </Button>
          </motion.div>
        )}

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <span className="inline-block px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-4">
            📂 Upload Center
          </span>
          <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
            Upload Your Content
          </h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Select language, then drag and drop your files. AI will generate summaries and videos in your chosen language.
          </p>
        </motion.div>

        {/* ✅ FIXED: Language Selector with clear visual indicator */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6 space-y-4"
        >
          {/* Language Selection - More Prominent */}
          <div className="card-gradient rounded-xl border border-border/50 p-4">
            <div className="flex items-center gap-3 mb-3">
              <Globe className="w-5 h-5 text-primary" />
              <h3 className="font-semibold text-foreground">Select Language</h3>
              <span className="text-xs text-muted-foreground">(for summary & video)</span>
            </div>
            
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: "english", label: "English", flag: "🇬🇧" },
                { value: "hindi", label: "हिंदी", flag: "🇮🇳" },
                { value: "kannada", label: "ಕನ್ನಡ", flag: "🇮🇳" }
              ].map((lang) => (
                <button
                  key={lang.value}
                  onClick={() => setLanguage(lang.value)}
                  disabled={isUploading}
                  className={`p-3 rounded-lg border-2 transition-all flex flex-col items-center gap-2 ${
                    language === lang.value
                      ? "border-primary bg-primary/10 shadow-lg shadow-primary/20"
                      : "border-border hover:border-primary/50 hover:bg-muted/50"
                  }`}
                >
                  <span className="text-2xl">{lang.flag}</span>
                  <span className={`text-sm font-medium ${
                    language === lang.value ? "text-primary" : "text-foreground"
                  }`}>
                    {lang.label}
                  </span>
                  {language === lang.value && (
                    <CheckCircle className="w-4 h-4 text-primary" />
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Other Options */}
          <div className="flex flex-wrap gap-3 items-center">
            <select
              value={summaryStyle}
              onChange={(e) => setSummaryStyle(e.target.value)}
              disabled={isUploading}
              className="px-4 py-2 rounded-lg bg-muted border border-border text-sm font-medium"
            >
              <option value="executive">📋 Executive</option>
              <option value="technical">🔧 Technical</option>
              <option value="academic">🎓 Academic</option>
              <option value="bullet">• Bullet Points</option>
              <option value="narrative">📖 Narrative</option>
            </select>
            
            <label className="flex items-center gap-2 px-4 py-2 rounded-lg bg-muted border border-border text-sm cursor-pointer hover:bg-muted/80">
              <input
                type="checkbox"
                checked={generateVideo}
                onChange={(e) => {
                  setGenerateVideo(e.target.checked);
                  if (!e.target.checked) setIncludeSubtitles(false);
                }}
                disabled={isUploading}
                className="w-4 h-4"
              />
              <span className="font-medium">🎬 Generate Video</span>
            </label>

            {/* ✅ Subtitle Toggle - Only when video enabled */}
            {generateVideo && (
              <label className="flex items-center gap-2 px-4 py-2 rounded-lg bg-muted border border-border text-sm cursor-pointer hover:bg-muted/80">
                <input
                  type="checkbox"
                  checked={includeSubtitles}
                  onChange={(e) => setIncludeSubtitles(e.target.checked)}
                  disabled={isUploading}
                  className="w-4 h-4"
                />
                <span className="font-medium">📝 Add Subtitles</span>
              </label>
            )}
          </div>

          {/* Current Settings Display */}
          <div className="flex flex-wrap gap-2 text-xs">
            <span className="px-3 py-1 rounded-full bg-primary/10 text-primary border border-primary/20">
              Language: {language === "english" ? "English" : language === "hindi" ? "हिंदी" : "ಕನ್ನಡ"}
            </span>
            <span className="px-3 py-1 rounded-full bg-muted text-muted-foreground">
              Style: {summaryStyle}
            </span>
            {generateVideo && (
              <>
                <span className="px-3 py-1 rounded-full bg-secondary/10 text-secondary border border-secondary/20">
                  Video: Enabled
                </span>
                <span className={`px-3 py-1 rounded-full ${
                  includeSubtitles 
                    ? "bg-accent/10 text-accent border border-accent/20" 
                    : "bg-muted text-muted-foreground"
                }`}>
                  Subtitles: {includeSubtitles ? "Yes" : "No"}
                </span>
              </>
            )}
          </div>
        </motion.div>

        {/* File Types */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          {fileTypes.map((type, index) => (
            <motion.div
              key={type.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.05 }}
              whileHover={{ y: -4 }}
              className="card-gradient rounded-xl border border-border/50 p-4 text-center hover:border-primary/30 transition-colors"
            >
              <type.icon className={`w-8 h-8 mx-auto mb-2 ${type.color}`} />
              <h3 className="font-medium text-foreground text-sm">{type.label}</h3>
              <p className="text-xs text-muted-foreground mt-1">{type.extensions}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Upload Zone */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`relative rounded-2xl border-2 border-dashed transition-all duration-300 ${
            isDragging
              ? "border-primary bg-primary/5 scale-[1.02]"
              : "border-border/50 hover:border-primary/50"
          }`}
        >
          <input
            type="file"
            multiple
            onChange={handleFileSelect}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={isUploading || !isConnected}
            accept=".pdf,.docx,.doc,.pptx,.xlsx,.xls,.csv,.mp3,.mp4,.jpg,.jpeg,.png,.txt,.md"
          />
          <div className="p-12 text-center">
            <motion.div
              animate={isDragging ? { scale: 1.1, y: -10 } : { scale: 1, y: 0 }}
              className="inline-flex"
            >
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center mb-4 mx-auto">
                <CloudUpload className={`w-10 h-10 ${isDragging ? "text-primary" : "text-muted-foreground"}`} />
              </div>
            </motion.div>
            <h3 className="font-display text-xl font-semibold text-foreground mb-2">
              {isDragging ? "Drop your files here!" : "Drag & Drop your files"}
            </h3>
            <p className="text-muted-foreground mb-4">or click to browse from your computer</p>
            <Button variant="outline" disabled={isUploading || !isConnected}>
              <UploadIcon className="w-4 h-4 mr-2" />
              Browse Files
            </Button>
          </div>
        </motion.div>

        {/* Uploaded Files List */}
        <AnimatePresence>
          {uploadedFiles.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-8"
            >
              <h3 className="font-display text-lg font-semibold text-foreground mb-4">
                Files ({uploadedFiles.length})
              </h3>
              <div className="space-y-3">
                {uploadedFiles.map((file, index) => {
                  const FileIcon = getFileIcon(file.type);
                  return (
                    <motion.div
                      key={`${file.name}-${index}`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      className="card-gradient rounded-xl border border-border/50 p-4"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <FileIcon className="w-5 h-5 text-primary" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-foreground text-sm truncate">{file.name}</p>
                            <p className="text-xs text-muted-foreground">{file.size}</p>
                            
                            {file.status === 'uploading' && file.progress !== undefined && (
                              <div className="mt-2">
                                <div className="flex justify-between text-xs mb-1">
                                  <span className="text-muted-foreground">Processing...</span>
                                  <span className="text-primary">{file.progress}%</span>
                                </div>
                                <div className="h-1 bg-muted rounded-full overflow-hidden">
                                  <motion.div
                                    className="h-full bg-primary"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${file.progress}%` }}
                                    transition={{ duration: 0.3 }}
                                  />
                                </div>
                              </div>
                            )}
                            
                            {file.result?.summary?.text && (
                              <details className="mt-2">
                                <summary className="text-xs text-primary cursor-pointer hover:underline">
                                  ✨ View {file.result.summary.language} Summary ({file.result.summary.word_count} words)
                                </summary>
                                <div className="mt-2 p-3 bg-muted/50 rounded-lg text-xs text-foreground leading-relaxed max-h-32 overflow-y-auto">
                                  {file.result.summary.text}
                                </div>
                              </details>
                            )}
                            
                            {file.error && (
                              <p className="text-xs text-destructive mt-1 flex items-center gap-1">
                                <XCircle className="w-3 h-3" />
                                {file.error}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 ml-2 flex-shrink-0">
                          {file.status === 'uploading' && (
                            <Loader2 className="w-5 h-5 text-primary animate-spin" />
                          )}
                          {file.status === 'success' && (
                            <div className="w-8 h-8 rounded-full bg-green-500/10 flex items-center justify-center">
                              <CheckCircle className="w-5 h-5 text-green-500" />
                            </div>
                          )}
                          {file.status === 'error' && (
                            <div className="w-8 h-8 rounded-full bg-destructive/10 flex items-center justify-center">
                              <XCircle className="w-5 h-5 text-destructive" />
                            </div>
                          )}
                          {file.status === 'pending' && (
                            <button
                              onClick={() => removeFile(index)}
                              disabled={isUploading}
                              className="w-8 h-8 rounded-full hover:bg-destructive/10 flex items-center justify-center transition-colors disabled:opacity-50"
                            >
                              <X className="w-4 h-4 text-muted-foreground hover:text-destructive" />
                            </button>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-6 flex gap-4"
              >
                <Button 
                  variant="hero" 
                  className="flex-1"
                  onClick={uploadFiles}
                  disabled={isUploading || !uploadedFiles.some(f => f.status === 'pending') || !isConnected}
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Processing {uploadedFiles.filter(f => f.status === 'uploading').length} file(s)...
                    </>
                  ) : (
                    `Process ${uploadedFiles.filter(f => f.status === 'pending').length} file(s) in ${
                      language === "english" ? "English" : language === "hindi" ? "हिंदी" : "ಕನ್ನಡ"
                    }`
                  )}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setUploadedFiles([])}
                  disabled={isUploading}
                >
                  Clear All
                </Button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Upload;