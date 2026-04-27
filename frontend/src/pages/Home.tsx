import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { ArrowDown, FileText, Video, MessageSquare, History, Upload, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Hero3D } from "@/components/Hero3D";
import { FeatureCard } from "@/components/FeatureCard";
import { Link } from "react-router-dom";
import { AnimatedText, GradientTextReveal, SlideUpText } from "@/components/AnimatedText";

export const Home = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });
  
  const heroOpacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.2], [1, 0.95]);
  
  const features = [
    {
      icon: Upload,
      title: "Easy Upload",
      description: "Drag and drop your files - videos, documents, or any content you want to summarize."
    },
    {
      icon: MessageSquare,
      title: "AI Chat",
      description: "Have intelligent conversations about your content with our advanced AI assistant."
    },
    {
      icon: FileText,
      title: "Text Summary",
      description: "Get concise, accurate text summaries that capture the essence of your documents."
    },
    {
      icon: Video,
      title: "Video Summary",
      description: "Transform lengthy videos into digestible summaries with key highlights."
    },
    {
      icon: History,
      title: "History Tracking",
      description: "Access all your past uploads, chats, and summaries anytime you need them."
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Powered by cutting-edge AI for instant results without compromising quality."
    }
  ];

  return (
    <div ref={containerRef} className="min-h-screen">
      {/* Hero Section */}
      <motion.section
        style={{ opacity: heroOpacity, scale: heroScale }}
        className="relative min-h-screen flex flex-col items-center justify-center px-4 pt-16"
      >
        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/5 rounded-full blur-3xl" />
        </div>

        <div className="relative z-10 text-center max-w-4xl mx-auto">
          <SlideUpText delay={0.1} className="mb-6">
            <h1 className="font-display text-4xl md:text-6xl font-bold">
              <GradientTextReveal 
                text="AI-Powered Multi-Modal Summarization" 
                className="text-4xl md:text-5xl lg:text-6xl"
                delay={0.3}
              />
            </h1>
          </SlideUpText>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.8 }}
          >
            <AnimatedText
              text="Upload any video, document, or text and get intelligent summaries in seconds. Chat with your content and unlock deeper understanding with our AI assistant."
              className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-8"
              delay={0.8}
              type="words"
              staggerChildren={0.02}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.2 }}
            className="flex flex-wrap gap-4 justify-center"
          >
            <Link to="/upload">
              <Button variant="hero" size="xl">
                Start Summarizing
              </Button>
            </Link>
            <Link to="/chat">
              <Button variant="glass" size="xl">
                Try AI Chat
              </Button>
            </Link>
          </motion.div>
        </div>

        {/* 3D Hero Element */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="mt-8"
        >
          <Hero3D />
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="flex flex-col items-center gap-2 text-muted-foreground"
          >
            <span className="text-sm">Scroll to explore</span>
            <ArrowDown className="w-5 h-5" />
          </motion.div>
        </motion.div>
      </motion.section>

      {/* Features Section */}
      <section className="py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <motion.span
              className="inline-block px-4 py-2 rounded-full bg-secondary/10 border border-secondary/20 text-secondary text-sm font-medium mb-4"
              initial={{ scale: 0, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ type: "spring", stiffness: 200, damping: 15 }}
            >
              Features
            </motion.span>
            <SlideUpText delay={0.1}>
              <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
                Everything You Need to
                <motion.span
                  className="gradient-text-secondary inline-block"
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.4, duration: 0.6 }}
                >
                  {" "}Summarize Smarter
                </motion.span>
              </h2>
            </SlideUpText>
            <AnimatedText
              text="Powerful tools designed to help you extract valuable insights from any content type."
              className="text-muted-foreground max-w-xl mx-auto"
              delay={0.3}
              type="words"
              staggerChildren={0.03}
            />
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <FeatureCard
                key={feature.title}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                delay={index * 0.1}
              />
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto"
        >
          <div className="relative card-gradient rounded-3xl border border-border/50 p-12 text-center overflow-hidden">
            {/* Background Glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-secondary/10" />
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent" />

            <div className="relative z-10">
              <SlideUpText>
                <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
                  Ready to Get Started?
                </h2>
              </SlideUpText>
              <AnimatedText
                text="Join thousands of users who are already saving time with intelligent summarization."
                className="text-muted-foreground max-w-xl mx-auto mb-8"
                delay={0.2}
                type="words"
                staggerChildren={0.02}
              />
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4 }}
              >
                <Link to="/upload">
                  <Button variant="hero" size="xl">
                    Upload Your First File
                  </Button>
                </Link>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </section>
    </div>
  );
};

export default Home;
