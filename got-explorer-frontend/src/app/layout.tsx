/**
 * Root Layout Component
 * 
 * This component serves as the foundational layout for the entire Game of Thrones Explorer
 * application. It wraps all pages rendered within the app and provides:
 *  - Global font configuration
 *  - HTML structure and language settings
 *  - Metadata for SEO and browser display
 * 
 * The layout uses Next.js App Router architecture to provide a consistent
 * experience across all pages without reloading the entire page when navigating.
 */
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

/**
 * Font Configuration
 * 
 * Sets up Geist Sans as the primary font and Geist Mono as the monospace font.
 * These fonts are loaded from Google Fonts via Next.js font optimization system,
 * which improves performance by:
 *  - Self-hosting font files
 *  - Eliminating layout shift with proper font loading
 *  - Optimizing font display
 */
const geistSans = Geist({
  variable: "--font-geist-sans", // CSS variable for use in Tailwind
  subsets: ["latin"],            // Only load Latin character subset for better performance
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono", // CSS variable for monospace font
  subsets: ["latin"],
});

/**
 * Metadata Configuration
 * 
 * Defines the application-wide metadata used for:
 *  - Browser tab title
 *  - Search engine descriptions
 *  - Social media sharing
 */
export const metadata: Metadata = {
  title: "Game of Thrones Explorer",
  description: "Explore the world of Game of Thrones through the books",
};

/**
 * Root Layout Component
 * 
 * This component wraps all pages in the application and provides
 * the basic HTML structure including:
 *  - HTML tag with language attribute
 *  - Body element with font configuration
 *  - Accessibility improvements with antialiased text
 * 
 * @param children - React components to be rendered within the layout
 * @returns The complete layout with wrapped children
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
