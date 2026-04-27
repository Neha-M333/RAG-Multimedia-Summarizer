import { motion, useMotionValue, useTransform, useSpring } from "framer-motion";
import { Sparkles, Zap, Brain, FileText, Video, MessageSquare } from "lucide-react";
import { useState } from "react";

export const Hero3D = () => {
  const [isHovered, setIsHovered] = useState(false);
  
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  
  const rotateX = useSpring(useTransform(mouseY, [-150, 150], [15, -15]), { stiffness: 300, damping: 30 });
  const rotateY = useSpring(useTransform(mouseX, [-150, 150], [-15, 15]), { stiffness: 300, damping: 30 });
  
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    mouseX.set(e.clientX - centerX);
    mouseY.set(e.clientY - centerY);
  };
  
  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
    setIsHovered(false);
  };

  return (
    <div 
      className="relative w-full h-[500px] perspective cursor-pointer"
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
    >
      {/* Main 3D Card */}
      <motion.div
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-80 preserve-3d"
        style={{ rotateX, rotateY }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, ease: "easeOut" }}
      >
        {/* Front Face */}
        <motion.div
          className="absolute inset-0 card-gradient rounded-3xl border border-border/50 p-6 flex flex-col items-center justify-center glow animate-float overflow-hidden"
          style={{ transform: "translateZ(40px)" }}
          whileHover={{ scale: 1.02 }}
        >
          {/* Animated gradient overlay on hover */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-br from-primary/20 via-transparent to-secondary/20 opacity-0"
            animate={{ opacity: isHovered ? 1 : 0 }}
            transition={{ duration: 0.3 }}
          />
          
          {/* Shine effect */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full"
            animate={{ x: isHovered ? "200%" : "-100%" }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
          />
          
          <motion.div
            className="relative w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center mb-4"
            animate={{ 
              rotate: isHovered ? [0, 10, -10, 0] : [0, 5, -5, 0],
              scale: isHovered ? 1.1 : 1
            }}
            transition={{ duration: isHovered ? 0.5 : 4, repeat: isHovered ? 0 : Infinity, ease: "easeInOut" }}
          >
            {/* Icon glow effect */}
            <motion.div
              className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary to-secondary blur-xl"
              animate={{ opacity: isHovered ? 0.6 : 0.3, scale: isHovered ? 1.2 : 1 }}
              transition={{ duration: 0.3 }}
            />
            <Brain className="relative w-10 h-10 text-primary-foreground" />
          </motion.div>
          
          <motion.h3 
            className="font-display text-xl font-bold gradient-text text-center"
            animate={{ scale: isHovered ? 1.05 : 1 }}
            transition={{ duration: 0.3 }}
          >
            AI-Powered
          </motion.h3>
          <p className="text-muted-foreground text-sm text-center mt-2">
            Multi-Modal Summarization
          </p>
          
          {/* Bottom glow line */}
          <motion.div
            className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary to-transparent"
            animate={{ opacity: isHovered ? 1 : 0.3, scaleX: isHovered ? 1 : 0.5 }}
            transition={{ duration: 0.3 }}
          />
        </motion.div>

        {/* Back reflection */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-primary/30 to-secondary/30 rounded-3xl blur-2xl"
          style={{ transform: "translateZ(-40px) scale(0.9)" }}
          animate={{ opacity: isHovered ? 0.6 : 0.3 }}
        />
      </motion.div>

      {/* Floating Elements with enhanced hover */}
      <FloatingCard
        className="left-[15%] top-[20%] w-16 h-16"
        icon={<FileText className="w-8 h-8 text-primary" />}
        delay={0.3}
        floatDuration={3}
        isParentHovered={isHovered}
      />

      <FloatingCard
        className="right-[15%] top-[15%] w-14 h-14"
        icon={<Video className="w-7 h-7 text-secondary" />}
        delay={0.5}
        floatDuration={2.5}
        isParentHovered={isHovered}
      />

      <FloatingCard
        className="left-[20%] bottom-[20%] w-12 h-12"
        icon={<MessageSquare className="w-6 h-6 text-accent" />}
        delay={0.7}
        floatDuration={2}
        isParentHovered={isHovered}
      />

      <FloatingCard
        className="right-[18%] bottom-[25%] w-14 h-14"
        icon={<Zap className="w-7 h-7 text-primary" />}
        delay={0.9}
        floatDuration={2.8}
        isParentHovered={isHovered}
      />

      {/* Sparkle Effects */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute pointer-events-none"
          style={{
            left: `${15 + Math.random() * 70}%`,
            top: `${15 + Math.random() * 70}%`,
          }}
          initial={{ opacity: 0, scale: 0 }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0, 1.2, 0],
            rotate: [0, 180],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: i * 0.4,
            ease: "easeInOut",
          }}
        >
          <Sparkles className="w-4 h-4 text-primary/60" />
        </motion.div>
      ))}

      {/* Gradient Orbs with animation */}
      <motion.div 
        className="absolute left-[10%] top-[30%] w-32 h-32 bg-primary/10 rounded-full blur-3xl"
        animate={{ 
          scale: isHovered ? 1.3 : [1, 1.2, 1],
          opacity: isHovered ? 0.3 : 0.2
        }}
        transition={{ duration: isHovered ? 0.5 : 4, repeat: isHovered ? 0 : Infinity }}
      />
      <motion.div 
        className="absolute right-[10%] bottom-[30%] w-40 h-40 bg-secondary/10 rounded-full blur-3xl"
        animate={{ 
          scale: isHovered ? 1.3 : [1.2, 1, 1.2],
          opacity: isHovered ? 0.3 : 0.2
        }}
        transition={{ duration: isHovered ? 0.5 : 4, repeat: isHovered ? 0 : Infinity }}
      />
      
      {/* Additional particle ring */}
      <motion.div
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full border border-primary/10"
        animate={{ rotate: 360, scale: isHovered ? 1.1 : 1 }}
        transition={{ rotate: { duration: 20, repeat: Infinity, ease: "linear" }, scale: { duration: 0.5 } }}
      />
      <motion.div
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] rounded-full border border-secondary/10"
        animate={{ rotate: -360, scale: isHovered ? 1.15 : 1 }}
        transition={{ rotate: { duration: 15, repeat: Infinity, ease: "linear" }, scale: { duration: 0.5 } }}
      />
    </div>
  );
};

interface FloatingCardProps {
  className: string;
  icon: React.ReactNode;
  delay: number;
  floatDuration: number;
  isParentHovered: boolean;
}

const FloatingCard = ({ className, icon, delay, floatDuration, isParentHovered }: FloatingCardProps) => {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <motion.div
      className={`absolute ${className} rounded-xl card-gradient border border-border/50 flex items-center justify-center cursor-pointer`}
      initial={{ opacity: 0, scale: 0 }}
      animate={{ 
        opacity: 1, 
        scale: isHovered ? 1.2 : 1,
        boxShadow: isHovered ? "0 0 30px hsl(var(--primary) / 0.4)" : "none"
      }}
      transition={{ delay, duration: 0.8, scale: { duration: 0.3 } }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      whileHover={{ rotate: 10 }}
    >
      <motion.div
        animate={{ 
          y: isHovered ? 0 : [-5, 5, -5],
          rotate: isHovered ? [0, -10, 10, 0] : 0,
          scale: isParentHovered && !isHovered ? 1.1 : 1
        }}
        transition={{ 
          y: { duration: floatDuration, repeat: Infinity, ease: "easeInOut" },
          rotate: { duration: 0.5 },
          scale: { duration: 0.3 }
        }}
      >
        {icon}
      </motion.div>
      
      {/* Glow effect on hover */}
      <motion.div
        className="absolute inset-0 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20"
        animate={{ opacity: isHovered ? 1 : 0 }}
        transition={{ duration: 0.2 }}
      />
    </motion.div>
  );
};
