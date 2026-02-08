import { ThemeProvider } from '@/providers/ThemeProvider';
import '@/styles/globals.css';
import type { Metadata } from 'next';
import FloatingChatWidget from '@/components/FloatingChatWidget';

export const metadata: Metadata = {
  title: 'Todo App',
  description: 'A premium todo application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <FloatingChatWidget />
        </ThemeProvider>
      </body>
    </html>
  );
}