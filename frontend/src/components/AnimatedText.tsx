import { motion, Variants } from "framer-motion";

interface AnimatedTextProps {
  text: string;
  className?: string;
  delay?: number;
  type?: "chars" | "words" | "lines";
  tag?: "h1" | "h2" | "h3" | "p" | "span";
  staggerChildren?: number;
}

export const AnimatedText = ({
  text,
  className = "",
  delay = 0,
  type = "words",
  tag = "p",
  staggerChildren = 0.03,
}: AnimatedTextProps) => {
  const items = type === "chars" 
    ? text.split("") 
    : type === "words" 
    ? text.split(" ") 
    : [text];

  const container: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren,
        delayChildren: delay,
      },
    },
  };

  const child: Variants = {
    hidden: {
      opacity: 0,
      y: 20,
      rotateX: -90,
    },
    visible: {
      opacity: 1,
      y: 0,
      rotateX: 0,
      transition: {
        type: "spring",
        damping: 12,
        stiffness: 100,
      },
    },
  };

  const Tag = tag;

  return (
    <Tag className={className}>
      <motion.span
        className="inline-flex flex-wrap justify-center"
        variants={container}
        initial="hidden"
        animate="visible"
        style={{ perspective: "1000px" }}
      >
        {items.map((item, index) => (
          <motion.span
            key={index}
            variants={child}
            className="inline-block"
            style={{ transformOrigin: "bottom" }}
          >
            {item}
            {type === "words" && index < items.length - 1 && "\u00A0"}
          </motion.span>
        ))}
      </motion.span>
    </Tag>
  );
};

interface GradientTextRevealProps {
  text: string;
  className?: string;
  delay?: number;
}

export const GradientTextReveal = ({
  text,
  className = "",
  delay = 0,
}: GradientTextRevealProps) => {
  return (
    <motion.span
      className={`relative inline-block ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay, duration: 0.5 }}
    >
      <motion.span
        className="absolute inset-0 gradient-text"
        initial={{ clipPath: "inset(0 100% 0 0)" }}
        animate={{ clipPath: "inset(0 0% 0 0)" }}
        transition={{ delay: delay + 0.2, duration: 0.8, ease: "easeOut" }}
      >
        {text}
      </motion.span>
      <span className="opacity-0">{text}</span>
    </motion.span>
  );
};

interface TypewriterTextProps {
  text: string;
  className?: string;
  delay?: number;
  speed?: number;
}

export const TypewriterText = ({
  text,
  className = "",
  delay = 0,
  speed = 0.05,
}: TypewriterTextProps) => {
  const chars = text.split("");

  return (
    <motion.span
      className={className}
      initial={{ opacity: 1 }}
      animate={{ opacity: 1 }}
    >
      {chars.map((char, index) => (
        <motion.span
          key={index}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: delay + index * speed, duration: 0.1 }}
        >
          {char}
        </motion.span>
      ))}
      <motion.span
        className="inline-block w-0.5 h-[1em] bg-primary ml-1"
        animate={{ opacity: [1, 0] }}
        transition={{ duration: 0.5, repeat: Infinity, repeatType: "reverse", delay: delay + chars.length * speed }}
      />
    </motion.span>
  );
};

interface SlideUpTextProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

export const SlideUpText = ({
  children,
  className = "",
  delay = 0,
}: SlideUpTextProps) => {
  return (
    <div className={`overflow-hidden ${className}`}>
      <motion.div
        initial={{ y: "100%", opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{
          delay,
          duration: 0.6,
          ease: [0.33, 1, 0.68, 1],
        }}
      >
        {children}
      </motion.div>
    </div>
  );
};
