'use client';
import { useState } from 'react';
import ChatMessage from '@/components/ChatMessage';

export default function Home() {
 const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean }>>([]);
 const [input, setInput] = useState('');
 const [isLoading, setIsLoading] = useState(false);

 const handleSubmit = async (e: React.FormEvent) => {
   e.preventDefault();
   if (!input.trim() || isLoading) return;
   
   // Add user message
   setMessages(prev => [...prev, { text: input, isUser: true }]);
   setIsLoading(true);
   
   try {
     const response = await fetch('http://localhost:8000/ask', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
         'Accept': 'application/json',
       },
       body: JSON.stringify({ text: input }),
     });
     
     if (!response.ok) {
       throw new Error(`HTTP error! status: ${response.status}`);
     }

     const data = await response.json();
     setMessages(prev => [...prev, { text: data.response, isUser: false }]);
   } catch (error) {
     console.error('Error:', error);
     setMessages(prev => [...prev, { 
       text: "Sorry, I'm having trouble connecting to the knowledge base.", 
       isUser: false 
     }]);
   } finally {
     setIsLoading(false);
     setInput('');
   }
 };

 return (
   <main className="flex min-h-screen flex-col bg-got-dark">
     <div className="flex-1 p-4 max-w-4xl mx-auto w-full">
       <div className="mb-4">
         <h1 className="text-4xl font-bold text-got-text mb-2">
           Game of Thrones Explorer
         </h1>
         <p className="text-got-light">Ask anything about the books...</p>
       </div>
       
       <div className="space-y-4 mb-4">
         {messages.map((msg, idx) => (
           <ChatMessage key={idx} message={msg.text} isUser={msg.isUser} />
         ))}
         {isLoading && (
           <div className="flex justify-start">
             <div className="bg-got-secondary text-got-text p-4 rounded-lg">
               Thinking...
             </div>
           </div>
         )}
       </div>

       <form onSubmit={handleSubmit} className="fixed bottom-4 left-4 right-4 max-w-4xl mx-auto">
         <div className="flex gap-2">
           <input
             type="text"
             value={input}
             onChange={(e) => setInput(e.target.value)}
             disabled={isLoading}
             className="flex-1 p-4 rounded-lg bg-gray-800 text-got-text focus:outline-none focus:ring-2 focus:ring-got-primary disabled:opacity-50"
             placeholder="Ask about Game of Thrones..."
           />
           <button 
             type="submit"
             disabled={isLoading}
             className="px-6 py-4 bg-got-primary text-got-text rounded-lg hover:bg-red-800 transition-colors disabled:opacity-50"
           >
             Send
           </button>
         </div>
       </form>
     </div>
   </main>
 );
}