'use client';
import { useState, useEffect } from 'react';
import ChatMessage from '@/components/ChatMessage';

/**
 * Game of Thrones Explorer - Main Application
 * 
 * This is the primary interface for the Game of Thrones knowledge explorer.
 * It provides a chat-like interface where users can ask questions about
 * the Game of Thrones books and receive responses based on the actual
 * content of the novels using RAG (Retrieval Augmented Generation).
 * 
 * Features:
 * - Real-time chat interface with user and bot messages
 * - API integration with backend knowledge base
 * - Dynamic suggested follow-up questions
 * - Loading state management
 * - Responsive design
 */
export default function Home() {
 /**
  * State Management
  * 
  * messages: Array of conversation history (both user and AI responses)
  * input: Current text in the input field
  * isLoading: Loading state during API calls
  */
 const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean }>>([]);
 const [input, setInput] = useState('');
 const [isLoading, setIsLoading] = useState(false);

 /**
  * Handles form submission when a user sends a question.
  * 
  * This function:
  * 1. Prevents default form submission
  * 2. Validates the input
  * 3. Updates the UI with the user's message
  * 4. Makes an API call to the backend
  * 5. Updates the UI with the response
  * 6. Handles any errors
  * 
  * @param e - The form submission event
  */
 const handleSubmit = async (e: React.FormEvent) => {
   e.preventDefault();
   if (!input.trim() || isLoading) return;
   
   // Add user message to the chat
   setMessages(prev => [...prev, { text: input, isUser: true }]);
   setIsLoading(true);
   
   try {
     // First try the RAG endpoint
     try {
       const ragResponse = await fetch('/api/rag/ask', {
         method: 'POST',
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify({ text: input }),
         signal: AbortSignal.timeout(10000) // 10 second timeout
       });
       
       if (ragResponse.ok) {
         const data = await ragResponse.json();
         const botResponse = data.response || "No response received";
         setMessages(prev => [...prev, { text: botResponse, isUser: false }]);
         setIsLoading(false);
         setInput('');
         return;
       }
     } catch (ragError) {
       console.log("RAG endpoint failed, falling back to local:", ragError);
     }

     // If RAG fails, fall back to local
     const fallbackResponse = await fetch('/api/ask', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({ text: input }),
     });

     const data = await fallbackResponse.json();
     const botResponse = data.response || "No response received";
     setMessages(prev => [...prev, { text: botResponse, isUser: false }]);
   } catch (error) {
     console.error('Error submitting question:', error);
     setMessages(prev => [...prev, { 
       text: "Sorry, I encountered an error while processing your question.", 
       isUser: false 
     }]);
   } finally {
     setIsLoading(false);
     setInput('');
   }
 };

 /**
  * Handles selection of a suggested follow-up question.
  * 
  * This is an alternative path to handleSubmit that's triggered
  * when a user clicks on one of the suggested questions rather
  * than typing their own.
  * 
  * @param question - The suggested question text
  */
 const handleSuggestedQuestion = (question: string) => {
   setInput(question);
   
   // Skip processing if there's already a request in progress
   if (isLoading) return;
   
   setMessages(prev => [...prev, { text: question, isUser: true }]);
   setIsLoading(true);
   
   // Try RAG backend first with timeout
   const controller = new AbortController();
   const timeoutId = setTimeout(() => controller.abort(), 5000);
   
   fetch('https://willhcurry-gotbot.hf.space/api/predict', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
     },
     body: JSON.stringify({
       data: [question]
     })
   })
   .then(response => {
     clearTimeout(timeoutId);
     if (response.ok) return response.json();
     throw new Error('RAG backend failed');
   })
   .then(data => {
     const botResponse = data.data?.[0]?.response || "No response received";
     setMessages(prev => [...prev, { text: botResponse, isUser: false }]);
   })
   .catch(error => {
     console.log("Falling back to local API", error);
     // Fall back to local implementation
     return fetch('/api/ask', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({ text: question }),
     })
     .then(response => {
       if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
       return response.json();
     })
     .then(data => {
       const botResponse = data.response || data.answer || "No response received";
       setMessages(prev => [...prev, { text: botResponse, isUser: false }]);
     });
   })
   .catch(error => {
     console.error('Error submitting question:', error);
     setMessages(prev => [...prev, { 
       text: "Sorry, I encountered an error while processing your question.", 
       isUser: false 
     }]);
   })
   .finally(() => {
     setIsLoading(false);
     setInput('');
   });
 };

 /**
  * Generates contextually relevant follow-up questions based on
  * the current question's content. Maps keywords in the question
  * to predefined sets of related questions.
  * 
  * @param currentQuestion - The current or most recent question
  * @returns An array of suggested follow-up questions
  */
 const getRelatedQuestions = (currentQuestion: string): string[] => {
   // Map of keywords to related questions
   const questionMap: {[key: string]: string[]} = {
     'jon snow': ['Who is Ned Stark?', 'What is the Night\'s Watch?', 'Who is Ygritte?'],
     'targaryen': ['Who is Daenerys?', 'What are dragons?', 'What is Valyria?'],
     'robert': ['Who is Robert Baratheon?', 'What is Storm\'s End?', 'Who is Cersei Lannister?'],
     'ned stark': ['Who is Jon Snow?', 'What is Winterfell?', 'What happened to Ned Stark?'],
     'lannister': ['Who is Tyrion?', 'What is Casterly Rock?', 'Who is Tywin Lannister?'],
   };
   
   // Find the first matching keyword
   const keywords = Object.keys(questionMap);
   const matchedKey = keywords.find(key => currentQuestion.toLowerCase().includes(key));
   return matchedKey ? questionMap[matchedKey] : [];
 };

 return (
   <main className="flex min-h-screen flex-col text-white">
     <div className="flex-1 p-4 max-w-4xl mx-auto">
       {/* Header with Game of Thrones-inspired styling */}
       <div className="mb-8 text-center">
         <h1 className="text-5xl font-bold text-red-600 mb-2">
           Game of Thrones Explorer
         </h1>
         <p className="text-amber-100">Ask anything about the books...</p>
       </div>
       
       {/* Chat container with more explicit visibility */}
       <div className="chat-container p-6 mb-20 min-h-[400px] w-full block">
         {/* Empty state message if no messages */}
         {messages.length === 0 && (
           <div className="text-center text-gray-400 py-10">
             <p className="mb-2 text-lg">Ask a question about Game of Thrones to get started</p>
             <div className="flex flex-wrap justify-center gap-2 mt-4">
               <button 
                 className="bg-gray-800 hover:bg-gray-700 text-amber-100 text-sm py-2 px-4 rounded-lg"
                 onClick={() => handleSuggestedQuestion("Who is Jon Snow?")}
               >
                 Who is Jon Snow?
               </button>
               <button 
                 className="bg-gray-800 hover:bg-gray-700 text-amber-100 text-sm py-2 px-4 rounded-lg"
                 onClick={() => handleSuggestedQuestion("What happened at the Red Wedding?")}
               >
                 What happened at the Red Wedding?
               </button>
               <button 
                 className="bg-gray-800 hover:bg-gray-700 text-amber-100 text-sm py-2 px-4 rounded-lg"
                 onClick={() => handleSuggestedQuestion("Tell me about House Stark")}
               >
                 Tell me about House Stark
               </button>
             </div>
           </div>
         )}
         
         {/* Message history */}
         <div className="space-y-4 mb-4">
           {messages.map((msg, idx) => (
             <ChatMessage key={idx} message={msg.text} isUser={msg.isUser} />
           ))}
           
           {/* Loading indicator */}
           {isLoading && (
             <div className="flex justify-start">
               <div className="bg-gray-800 text-amber-100 p-4 rounded-lg">
                 <div className="flex items-center space-x-2">
                   <span className="text-sm">The Maester is consulting the archives...</span>
                 </div>
               </div>
             </div>
           )}
         </div>

         {/* Suggested questions section - only shown after receiving a response */}
         {!isLoading && messages.length > 0 && messages[messages.length-1]?.isUser === false && (
           <div className="mt-6">
             <div className="text-sm text-amber-200 mb-2">You might also want to know:</div>
             <div className="flex flex-wrap gap-2">
               {getRelatedQuestions(messages[messages.length-2]?.text || '').map((q, i) => (
                 <button 
                   key={i} 
                   className="bg-gray-800 hover:bg-gray-700 text-amber-100 text-sm py-1 px-3 rounded-full"
                   onClick={() => handleSuggestedQuestion(q)}
                   aria-label={`Ask about ${q}`}
                 >
                   {q}
                 </button>
               ))}
             </div>
           </div>
         )}
       </div>

       {/* Input form - fixed at bottom */}
       <form onSubmit={handleSubmit} className="fixed bottom-4 left-4 right-4 max-w-4xl mx-auto">
         <div className="flex gap-2">
           <input
             type="text"
             value={input}
             onChange={(e) => setInput(e.target.value)}
             disabled={isLoading}
             className="flex-1 p-4 rounded-lg bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
             placeholder="Ask about Game of Thrones..."
             aria-label="Your question about Game of Thrones"
           />
           <button 
             type="submit"
             disabled={isLoading}
             className="px-6 py-4 bg-red-700 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50"
             aria-label="Send question"
           >
             Send
           </button>
         </div>
       </form>
     </div>
   </main>
 );
}