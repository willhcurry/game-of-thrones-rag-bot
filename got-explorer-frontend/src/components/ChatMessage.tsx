export default function ChatMessage({ 
  message, 
  isUser 
}: { 
  message: string, 
  isUser: boolean 
}) {
  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] p-4 rounded-lg mb-4 ${
        isUser 
          ? 'bg-got-primary text-got-text' 
          : 'bg-got-secondary text-got-text'
      }`}>
        {message}
      </div>
    </div>
  );
}