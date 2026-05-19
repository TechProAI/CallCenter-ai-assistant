import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, History, Headphones, Sun, Moon, X } from 'lucide-react';
import { clsx } from 'clsx';
import { useTheme } from '../../contexts/ThemeContext';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/upload', icon: Upload, label: 'Analyze Call' },
  { to: '/history', icon: History, label: 'Call History' },
];

export default function Sidebar({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={onClose} />
      )}

      <aside className={clsx(
        'fixed left-0 top-0 bottom-0 w-64 cs-sidebar border-r cs-border z-50 flex flex-col transition-transform duration-300',
        'lg:translate-x-0',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        {/* Logo */}
        <div className="p-6 border-b cs-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <Headphones className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-display font-bold cs-heading tracking-tight">CallSense</h1>
                <p className="text-[10px] cs-muted font-medium tracking-widest uppercase">AI Intelligence</p>
              </div>
            </div>
            <button onClick={onClose} className="lg:hidden p-1 cs-muted hover:cs-text">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1.5">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              onClick={onClose}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/10 to-blue-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm shadow-cyan-500/10'
                    : 'cs-muted hover:cs-text cs-nav-hover'
                )
              }
            >
              <item.icon className="w-[18px] h-[18px]" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Theme Toggle + Footer */}
        <div className="p-4 border-t cs-border space-y-3">
          <button
            onClick={toggleTheme}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl cs-card-bg cs-border border text-sm font-medium cs-text transition-all hover:border-cyan-500/30"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-violet-400" />}
            {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
          </button>
          <div className="cs-card-bg rounded-xl p-3 text-center border cs-border">
            <p className="text-[10px] cs-muted font-medium">Powered by GPT-4o + LangGraph</p>
          </div>
        </div>
      </aside>
    </>
  );
}
