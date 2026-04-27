import Navigation from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Upload, History, MessageSquare, FileText, Video, Music } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useEffect, useRef, useState } from "react";

const Index = () => {
  const navigate = useNavigate();
  const [scrollProgress, setScrollProgress] = useState(0);
  const featuresRef = useRef<HTMLDivElement>(null);
  const howItWorksRef = useRef<HTMLDivElement>(null);
  const outputsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      const totalScroll = document.documentElement.scrollHeight - window.innerHeight;
      const currentProgress = (window.scrollY / totalScroll) * 100;
      setScrollProgress(currentProgress);

      // Parallax effect for sections
      const sections = [featuresRef.current, howItWorksRef.current, outputsRef.current];
      sections.forEach((section) => {
        if (section) {
          const rect = section.getBoundingClientRect();
          const isVisible = rect.top < window.innerHeight * 0.8;
          if (isVisible) {
            section.style.opacity = "1";
            section.style.transform = "translateY(0)";
          }
        }
      });
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-background">
      {/* Progress Bar */}
      <div className="fixed top-0 left-0 w-full h-1 z-50 bg-muted">
        <div
          className="h-full bg-gradient-primary transition-all duration-300"
          style={{ width: `${scrollProgress}%` }}
        />
      </div>

      <Navigation />

      {/* Hero Section */}
      <section className="min-h-screen flex items-center justify-center px-6 pt-20">
        <div className="max-w-6xl mx-auto text-center animate-fade-in">
          <div className="inline-block mb-6 px-6 py-2 glass rounded-full">
            <span className="text-primary font-semibold">AI-Powered Content Analysis</span>
          </div>
          <h1 className="text-6xl md:text-8xl font-bold mb-6 gradient-text leading-tight">
            AKHN
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
            Transform your documents, videos, and audio files into intelligent insights with our cutting-edge AI analysis platform
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              onClick={() => navigate("/upload")}
              className="bg-gradient-primary hover:opacity-90 transition-opacity text-lg px-8 py-6"
            >
              Get Started
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate("/chat")}
              className="border-primary/50 text-foreground hover:bg-primary/10 text-lg px-8 py-6"
            >
              Try Chat AI
            </Button>
          </div>
          <div className="mt-16 animate-bounce">
            <div className="w-6 h-10 border-2 border-primary rounded-full mx-auto flex items-start justify-center p-2">
              <div className="w-1 h-3 bg-primary rounded-full animate-glow" />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section
        ref={featuresRef}
        className="min-h-screen flex items-center justify-center px-6 py-20 opacity-0 translate-y-20 transition-all duration-1000"
      >
        <div className="max-w-6xl mx-auto">
          <h2 className="text-5xl font-bold mb-4 text-center gradient-text">
            Powerful Features
          </h2>
          <p className="text-center text-muted-foreground mb-16 text-lg">
            Everything you need to analyze and understand your content
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div
              className="glass rounded-2xl p-8 glass-hover cursor-pointer group"
              onClick={() => navigate("/upload")}
            >
              <div className="w-16 h-16 rounded-full bg-gradient-primary/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Upload className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Smart Upload</h3>
              <p className="text-muted-foreground">
                Drag & drop any file format. AI processes it instantly.
              </p>
            </div>

            <div
              className="glass rounded-2xl p-8 glass-hover cursor-pointer group"
              onClick={() => navigate("/history")}
            >
              <div className="w-16 h-16 rounded-full bg-gradient-accent/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <History className="w-8 h-8 text-accent" />
              </div>
              <h3 className="text-xl font-semibold mb-3">History</h3>
              <p className="text-muted-foreground">
                Track all your uploads in an organized timeline.
              </p>
            </div>

            <div
              className="glass rounded-2xl p-8 glass-hover cursor-pointer group"
              onClick={() => navigate("/chat")}
            >
              <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <MessageSquare className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">AI Chat</h3>
              <p className="text-muted-foreground">
                Ask questions and get instant answers about your content.
              </p>
            </div>

            <div
              className="glass rounded-2xl p-8 glass-hover cursor-pointer group"
              onClick={() => navigate("/summary")}
            >
              <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <FileText className="w-8 h-8 text-accent" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Summary</h3>
              <p className="text-muted-foreground">
                Get comprehensive summaries in multiple formats.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section
        ref={howItWorksRef}
        className="min-h-screen flex items-center justify-center px-6 py-20 opacity-0 translate-y-20 transition-all duration-1000"
      >
        <div className="max-w-6xl mx-auto">
          <h2 className="text-5xl font-bold mb-4 text-center gradient-text">
            How It Works
          </h2>
          <p className="text-center text-muted-foreground mb-16 text-lg">
            Simple, fast, and powerful
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center group">
              <div className="glass rounded-2xl p-8 mb-6 group-hover:scale-105 transition-transform">
                <div className="text-6xl font-bold text-primary mb-4">01</div>
                <h3 className="text-2xl font-semibold mb-3">Upload</h3>
                <p className="text-muted-foreground">
                  Drop your files into our secure platform. We support documents, videos, and audio.
                </p>
              </div>
            </div>

            <div className="text-center group">
              <div className="glass rounded-2xl p-8 mb-6 group-hover:scale-105 transition-transform">
                <div className="text-6xl font-bold text-primary mb-4">02</div>
                <h3 className="text-2xl font-semibold mb-3">Analyze</h3>
                <p className="text-muted-foreground">
                  Our AI processes your content in seconds, extracting key insights and information.
                </p>
              </div>
            </div>

            <div className="text-center group">
              <div className="glass rounded-2xl p-8 mb-6 group-hover:scale-105 transition-transform">
                <div className="text-6xl font-bold text-primary mb-4">03</div>
                <h3 className="text-2xl font-semibold mb-3">Interact</h3>
                <p className="text-muted-foreground">
                  Chat with your content, get summaries, and explore insights in multiple formats.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Outputs Section */}
      <section
        ref={outputsRef}
        className="min-h-screen flex items-center justify-center px-6 py-20 opacity-0 translate-y-20 transition-all duration-1000"
      >
        <div className="max-w-6xl mx-auto">
          <h2 className="text-5xl font-bold mb-4 text-center gradient-text">
            Multi-Format Outputs
          </h2>
          <p className="text-center text-muted-foreground mb-16 text-lg">
            Get your insights in the format that works best for you
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="glass rounded-2xl p-8 glass-hover">
              <div className="w-20 h-20 rounded-2xl bg-gradient-primary/20 flex items-center justify-center mb-6">
                <FileText className="w-10 h-10 text-primary" />
              </div>
              <h3 className="text-2xl font-semibold mb-4">Text Output</h3>
              <p className="text-muted-foreground mb-4">
                Detailed written summaries, key points, and transcriptions ready to copy and use.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">Summaries</span>
                <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">Transcripts</span>
                <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">Key Points</span>
              </div>
            </div>

            <div className="glass rounded-2xl p-8 glass-hover">
              <div className="w-20 h-20 rounded-2xl bg-gradient-accent/20 flex items-center justify-center mb-6">
                <Video className="w-10 h-10 text-accent" />
              </div>
              <h3 className="text-2xl font-semibold mb-4">Video Output</h3>
              <p className="text-muted-foreground mb-4">
                Visual summaries and highlight reels generated from your video content.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-accent/20 text-accent rounded-full text-sm">Highlights</span>
                <span className="px-3 py-1 bg-accent/20 text-accent rounded-full text-sm">Clips</span>
                <span className="px-3 py-1 bg-accent/20 text-accent rounded-full text-sm">Timeline</span>
              </div>
            </div>

            <div className="glass rounded-2xl p-8 glass-hover">
              <div className="w-20 h-20 rounded-2xl bg-primary/20 flex items-center justify-center mb-6">
                <Music className="w-10 h-10 text-primary" />
              </div>
              <h3 className="text-2xl font-semibold mb-4">Audio Output</h3>
              <p className="text-muted-foreground mb-4">
                Listen to AI-generated summaries and insights on the go.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">Voice Summary</span>
                <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">Podcast</span>
                <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">Audio Clips</span>
              </div>
            </div>
          </div>

          <div className="text-center mt-16">
            <Button
              onClick={() => navigate("/summary")}
              className="bg-gradient-accent hover:opacity-90 transition-opacity text-lg px-8 py-6"
            >
              Explore Outputs
            </Button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="min-h-[50vh] flex items-center justify-center px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <div className="glass rounded-3xl p-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 gradient-text">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Join thousands of users transforming their content with AI
            </p>
            <Button
              onClick={() => navigate("/upload")}
              className="bg-gradient-primary hover:opacity-90 transition-opacity text-lg px-8 py-6"
            >
              Start Analyzing Now
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
