import React, { useMemo } from 'react';
import { FaBook, FaUserAlt } from 'react-icons/fa';
import { RiSwordLine } from 'react-icons/ri';
import { GiWolfHead, GiLion, GiDragonHead } from 'react-icons/gi';

/**
 * ChatMessage Component
 * 
 * Renders a single message in the chat interface with styling based on:
 * 1. Whether the message is from the user or the AI
 * 2. Which Game of Thrones house is mentioned in the content
 * 
 * Features:
 * - Dynamic styling based on house mentions (Stark, Lannister, etc.)
 * - Source highlighting for book references
 * - Accessibility support with ARIA attributes
 * - House-specific icons for visual distinction
 */
export default function ChatMessage({ 
  message, 
  isUser 
}: { 
  message: string, 
  isUser: boolean 
}) {
  /**
   * Detects mentions of Game of Thrones houses in the message content
   * to apply appropriate styling and iconography.
   * 
   * @returns The detected house name or null if no house is mentioned
   */
  const detectedHouse = useMemo(() => {
    if (isUser) return null;
    
    const lowerMsg = message.toLowerCase();
    if (lowerMsg.includes('stark')) return 'stark';
    if (lowerMsg.includes('lannister')) return 'lannister';
    if (lowerMsg.includes('targaryen')) return 'targaryen';
    if (lowerMsg.includes('baratheon')) return 'baratheon';
    return null;
  }, [message, isUser]);
  
  /**
   * Formats the message content by highlighting book sources.
   * Uses regex to identify and style text patterns like "From [Book Name]:"
   * 
   * @returns Formatted React elements with highlighted source text
   */
  const formattedMessage = useMemo(() => {
    if (!isUser) {
      // Use regex to split the message by source citations
      const parts = message.split(/(From [^:]+:)/g);
      
      return (
        <>
          {parts.map((part, index) => {
            if (part.match(/From [^:]+:/)) {
              return <span key={index} className="text-amber-400 font-semibold">{part}</span>;
            }
            return <span key={index}>{part}</span>;
          })}
        </>
      );
    }
    return message;
  }, [message, isUser]);

  /**
   * Selects an appropriate icon based on message content and sender.
   * User messages have a user icon, while AI messages have icons
   * representing the mentioned house or a default book icon.
   * 
   * @returns A React icon element appropriate for the message content
   */
  const getMessageIcon = () => {
    if (isUser) {
      return <FaUserAlt size={16} color="#9CA3AF" />;
    }
    
    switch(detectedHouse) {
      case 'stark':
        return <GiWolfHead size={16} color="#D1D5DB" />;
      case 'lannister':
        return <GiLion size={16} color="#F59E0B" />;
      case 'targaryen':
        return <GiDragonHead size={16} color="#EF4444" />;
      case 'baratheon':
        return <RiSwordLine size={16} color="#FBBF24" />;
      default:
        return <FaBook size={16} color="#F59E0B" />;
    }
  };

  /**
   * Generates CSS classes for styling the message bubble based on
   * user status and detected house references.
   * 
   * @returns A string of CSS classes for the message container
   */
  const getHouseStyling = () => {
    if (isUser) return 'bg-got-primary text-got-text';
    
    switch(detectedHouse) {
      case 'stark':
        return 'bg-gray-700 text-gray-100 border-l-4 border-gray-400';
      case 'lannister':
        return 'bg-got-secondary text-got-text border-l-4 border-yellow-600';
      case 'targaryen':
        return 'bg-gray-900 text-got-text border-l-4 border-red-800';
      case 'baratheon':
        return 'bg-gray-800 text-got-text border-l-4 border-yellow-500';
      default:
        return 'bg-got-secondary text-got-text border-l-4 border-amber-700';
    }
  };

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] p-4 rounded-lg mb-4 ${getHouseStyling()}`}
           role="article"
           aria-label={isUser ? "Your message" : "Maester's response"}>
        {!isUser && (
          <div className="flex items-center mb-2 text-xs text-amber-400/80">
            <span className="mr-1">{getMessageIcon()}</span>
            <span className="ml-1">
              {detectedHouse 
                ? `House ${detectedHouse.charAt(0).toUpperCase() + detectedHouse.slice(1)} Knowledge` 
                : "Maester's Knowledge"}
            </span>
          </div>
        )}
        <div className="whitespace-pre-line">
          {formattedMessage}
        </div>
      </div>
    </div>
  );
} 