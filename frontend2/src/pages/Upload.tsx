import Navigation from "@/components/Navigation";
import { Upload as UploadIcon, File, CheckCircle, AlertCircle, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useCallback } from "react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const Upload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState<any[]>([]);
  const [generate_summary, setGenerateSummary] = useState(true);
  const [summary_style, setSummaryStyle] = useState("executive");
  const [extract_keywords, setExtractKeywords] = useState(true);
  const [enable_ocr, setEnableOcr] = useState(true);
  const [language, setLanguage] = useState("English");
  const [advanced_analysis, setAdvancedAnalysis] = useState(false);
  const { toast } = useToast();

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles(prev => [...prev, ...droppedFiles]);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles(prev => [...prev, ...selectedFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setUploadResults([]);
    
    const results = [];
    
    for (const file of files) {
      try {
        toast({
          title: "Processing",
          description: `Uploading ${file.name}...`,
        });

        const result = await api.uploadFile(file, {
          generateSummary: generate_summary,
          extractKeywords: extract_keywords,
        });

        results.push({
          ...result,
          status: 'success',
        });

        toast({
          title: "Success",
          description: `${file.name} processed successfully!`,
        });
      } catch (error) {
        console.error('Upload error:', error);
        results.push({
          file_name: file.name,
          status: 'error',
          error: error instanceof Error ? error.message : 'Upload failed',
        });

        toast({
          title: "Error",
          description: `Failed to process ${file.name}`,
          variant: "destructive",
        });
      }
    }

    setUploadResults(results);
    setUploading(false);
    setFiles([]);
  };

  return (
    <div className="min-h-screen bg-gradient-background">
      <Navigation />
      <main className="container mx-auto px-6 pt-24 pb-12">
        <div className="max-w-4xl mx-auto animate-fade-in">
          <h2 className="text-4xl font-bold mb-2 gradient-text">Upload Content</h2>
          <p className="text-muted-foreground mb-8">
            Upload your files to get started with AI-powered analysis
          </p>

          {/* Drop Zone */}
          <div
            className={`glass rounded-2xl p-12 transition-all ${
              isDragging ? "border-primary scale-105" : ""
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center justify-center text-center">
              <div className="w-24 h-24 rounded-full bg-gradient-primary/20 flex items-center justify-center mb-6">
                <UploadIcon className="w-12 h-12 text-primary" />
              </div>
              <h3 className="text-2xl font-semibold mb-2">Drop files here</h3>
              <p className="text-muted-foreground mb-6">
                or click to browse from your device
              </p>
              <input
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
                accept=".pdf,.docx,.xlsx,.csv,.mp3,.mp4,.jpg,.png"
              />
              <label htmlFor="file-upload">
                <Button 
                  className="bg-gradient-primary hover:opacity-90 transition-opacity"
                  type="button"
                  onClick={() => document.getElementById('file-upload')?.click()}
                >
                  Select Files
                </Button>
              </label>
            </div>
          </div>

          {/* Selected Files */}
          {files.length > 0 && (
            <div className="mt-8 glass rounded-2xl p-6">
              <h3 className="text-xl font-semibold mb-4">Selected Files ({files.length})</h3>
              <div className="space-y-3">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between glass rounded-xl p-4">
                    <div className="flex items-center gap-3">
                      <File className="w-5 h-5 text-primary" />
                      <div>
                        <p className="font-medium">{file.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(index)}
                      disabled={uploading}
                    >
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Processing Options */}
          {files.length > 0 && (
            <div className="mt-6 glass rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                <span>⚙️</span>
                Processing Options
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Column 1 */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium flex items-center gap-2">
                      <FileText className="w-4 h-4 text-primary" />
                      Generate Summary
                    </label>
                    <input
                      type="checkbox"
                      checked={generate_summary}
                      onChange={(e) => setGenerateSummary(e.target.checked)}
                      className="w-4 h-4 rounded border-primary/30 bg-background text-primary focus:ring-primary"
                    />
                  </div>
                  {generate_summary && (
                    <div className="ml-6">
                      <label className="text-xs text-muted-foreground mb-2 block">Summary Style</label>
                      <select
                        value={summary_style}
                        onChange={(e) => setSummaryStyle(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg glass text-sm border border-border/50 focus:border-primary/50 focus:outline-none"
                      >
                        <option value="executive">Executive</option>
                        <option value="technical">Technical</option>
                        <option value="academic">Academic</option>
                        <option value="bullet">Bullet Points</option>
                        <option value="narrative">Narrative</option>
                      </select>
                    </div>
                  )}
                </div>

                {/* Column 2 */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium flex items-center gap-2">
                      <span>🔑</span>
                      Extract Keywords
                    </label>
                    <input
                      type="checkbox"
                      checked={extract_keywords}
                      onChange={(e) => setExtractKeywords(e.target.checked)}
                      className="w-4 h-4 rounded border-primary/30 bg-background text-primary focus:ring-primary"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium flex items-center gap-2">
                      <span>👁️</span>
                      Enable OCR
                    </label>
                    <input
                      type="checkbox"
                      checked={enable_ocr}
                      onChange={(e) => setEnableOcr(e.target.checked)}
                      className="w-4 h-4 rounded border-primary/30 bg-background text-primary focus:ring-primary"
                    />
                  </div>
                </div>

                {/* Column 3 */}
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block flex items-center gap-2">
                      <span>🌍</span>
                      Language
                    </label>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg glass text-sm border border-border/50 focus:border-primary/50 focus:outline-none"
                    >
                      <option value="English">English</option>
                      <option value="Hindi">हिंदी (Hindi)</option>
                      <option value="Kannada">ಕನ್ನಡ (Kannada)</option>
                    </select>
                  </div>

                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium flex items-center gap-2">
                      <span>🔬</span>
                      Advanced Analysis
                    </label>
                    <input
                      type="checkbox"
                      checked={advanced_analysis}
                      onChange={(e) => setAdvancedAnalysis(e.target.checked)}
                      className="w-4 h-4 rounded border-primary/30 bg-background text-primary focus:ring-primary"
                    />
                  </div>
                </div>
              </div>

              <Button
                className="w-full mt-6 bg-gradient-primary hover:opacity-90 transition-opacity"
                onClick={uploadFiles}
                disabled={uploading}
              >
                {uploading ? 'Processing...' : 'Upload & Process All'}
              </Button>
            </div>
          )}

          {/* Upload Results */}
          {uploadResults.length > 0 && (
            <div className="mt-8 space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-2xl font-semibold gradient-text">Processing Results</h3>
                <span className="text-sm text-muted-foreground">
                  {uploadResults.filter(r => r.status === 'success').length} / {uploadResults.length} successful
                </span>
              </div>
              
              {uploadResults.map((result, index) => (
                <div
                  key={index}
                  className={`glass rounded-2xl overflow-hidden transition-all ${
                    result.status === 'success' 
                      ? 'border border-green-500/30 hover:border-green-500/50' 
                      : 'border border-red-500/30 hover:border-red-500/50'
                  }`}
                >
                  {/* Header */}
                  <div className={`px-6 py-4 ${
                    result.status === 'success' ? 'bg-green-500/10' : 'bg-red-500/10'
                  }`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {result.status === 'success' ? (
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-red-500" />
                        )}
                        <h4 className="font-semibold text-lg">{result.file_name}</h4>
                      </div>
                      {result.status === 'success' && (
                        <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium">
                          ✓ Processed
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-6 space-y-4">
                    {result.status === 'success' ? (
                      <>
                        {/* Metadata Grid */}
                        <div className="grid grid-cols-3 gap-4">
                          <div className="glass rounded-lg p-4 text-center">
                            <p className="text-2xl font-bold gradient-text">{result.id}</p>
                            <p className="text-xs text-muted-foreground mt-1">Document ID</p>
                          </div>
                          <div className="glass rounded-lg p-4 text-center">
                            <p className="text-2xl font-bold gradient-text">{result.chunks}</p>
                            <p className="text-xs text-muted-foreground mt-1">Chunks Created</p>
                          </div>
                          <div className="glass rounded-lg p-4 text-center">
                            <p className="text-2xl font-bold gradient-text">{result.file_type?.toUpperCase()}</p>
                            <p className="text-xs text-muted-foreground mt-1">File Type</p>
                          </div>
                        </div>

                        {/* Summary Section */}
                        {result.summary && (
                          <div className="glass rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3">
                              <FileText className="w-4 h-4 text-primary" />
                              <h5 className="font-semibold text-sm">Summary</h5>
                            </div>
                            <p className="text-sm leading-relaxed text-muted-foreground">
                              {result.summary}
                            </p>
                          </div>
                        )}

                        {/* Keywords Section */}
                        {result.keywords && result.keywords.length > 0 && (
                          <div className="glass rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3">
                              <span className="text-primary">🔑</span>
                              <h5 className="font-semibold text-sm">Keywords</h5>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {result.keywords.map((keyword: string, i: number) => (
                                <span
                                  key={i}
                                  className="px-3 py-1.5 bg-gradient-primary/20 text-primary rounded-full text-xs font-medium border border-primary/30 hover:bg-gradient-primary/30 transition-colors"
                                >
                                  {keyword}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="flex items-start gap-3 p-4 bg-red-500/10 rounded-lg border border-red-500/30">
                        <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="font-medium text-red-400 mb-1">Processing Failed</p>
                          <p className="text-sm text-red-300">{result.error}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Info Cards */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="glass rounded-xl p-6 glass-hover">
              <File className="w-8 h-8 text-primary mb-3" />
              <h4 className="font-semibold mb-2">Supported Formats</h4>
              <p className="text-sm text-muted-foreground">
                PDF, DOCX, XLSX, CSV, MP3, MP4, JPG, PNG, and more
              </p>
            </div>
            <div className="glass rounded-xl p-6 glass-hover">
              <div className="w-8 h-8 text-accent mb-3 flex items-center justify-center">
                <span className="text-2xl">⚡</span>
              </div>
              <h4 className="font-semibold mb-2">Fast Processing</h4>
              <p className="text-sm text-muted-foreground">
                AI-powered analysis completes in seconds
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Upload;