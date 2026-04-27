import { NavLink } from "@/components/NavLink";
import { Home, Upload, History, MessageSquare, FileText } from "lucide-react";

const Navigation = () => {
  const navItems = [
    { to: "/", label: "Home", icon: Home },
    { to: "/upload", label: "Upload", icon: Upload },
    { to: "/history", label: "History", icon: History },
    { to: "/chat", label: "Chat", icon: MessageSquare },
    { to: "/summary", label: "Summary", icon: FileText },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-glass-border">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold gradient-text">GlassVault</h1>
          <div className="flex gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className="flex items-center gap-2 px-4 py-2 rounded-xl glass-hover transition-all"
                activeClassName="bg-gradient-primary text-primary-foreground"
              >
                <item.icon className="w-4 h-4" />
                <span className="hidden sm:inline">{item.label}</span>
              </NavLink>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
