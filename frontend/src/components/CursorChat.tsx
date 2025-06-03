'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { InitialAnalysisData, ChatMessagePayload, sendChatMessage, ChatApiResponse } from '@/lib/api';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai' | 'system';
}

interface CursorChatProps {
  initialAnalysisData?: InitialAnalysisData | null;
  isVisible: boolean;
}

export default function CursorChat({ initialAnalysisData, isVisible }: CursorChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // Initial suggestions from analysis data
  useEffect(() => {
    if (initialAnalysisData) {
      const initialMsgs: Message[] = [];
      if (initialAnalysisData.insights_summary && initialAnalysisData.insights_summary.length > 0) {
        initialMsgs.push({
          id: `suggestion-insight-${Date.now()}`,
          text: "Why did my agent fail?", // Default initial question
          sender: 'system'
        });
         initialAnalysisData.insights_summary.slice(0, 2).forEach((insight, index) => {
           initialMsgs.push({id: `insight-${index}`, text: insight, sender: 'system'});
         });
      } else if (initialAnalysisData.next_steps && initialAnalysisData.next_steps.length > 0) {
         initialMsgs.push({
          id: `suggestion-nextstep-${Date.now()}`,
          text: "What should I do next?",
          sender: 'system'
        });
        initialAnalysisData.next_steps.slice(0, 2).forEach((step, index) => {
           initialMsgs.push({id: `nextstep-${index}`, text: step, sender: 'system'});
         });
      }
      if(initialMsgs.length > 0) {
        setMessages(initialMsgs);
      }
    }
  }, [initialAnalysisData]);

  const handleSendMessage = useCallback(async (messageText?: string) => {
    const textToSend = messageText || inputValue;
    if (!textToSend.trim()) return;

    const newUserMessage: Message = { id: `user-${Date.now()}`, text: textToSend, sender: 'user' };
    setMessages((prev) => [...prev, newUserMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const payload: ChatMessagePayload = {
        message: textToSend,
        analysis_context: initialAnalysisData ? { // Send relevant parts of analysis data
            detected_framework: initialAnalysisData.reliability_prediction?.risk_level, // Example, adjust as needed
            insights_summary: initialAnalysisData.insights_summary,
            reliability_prediction: initialAnalysisData.reliability_prediction,
            // Add other parts of InitialAnalysisData that backend /api/chat might use for context
        } : undefined,
      };
      const response: ChatApiResponse = await sendChatMessage(payload);
      const newAiMessage: Message = { id: `ai-${Date.now()}`, text: response.response, sender: 'ai' };
      setMessages((prev) => [...prev, newAiMessage]);
    } catch (e: any) {
      const errorMessage = e.message || 'Failed to get response from AI.';
      setError(errorMessage);
      setMessages((prev) => [...prev, {id: `error-${Date.now()}`, text: errorMessage, sender: 'system'}]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }, [inputValue, initialAnalysisData]);

  // Keyboard shortcut (Ctrl+K or Cmd+K)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (!isVisible) {
    return null;
  }

  return (
    <div className="fixed top-16 right-0 bottom-0 w-full md:w-96 bg-white shadow-2xl border-l border-arc-gray-light flex flex-col h-[calc(100vh-4rem)] transition-transform duration-300 ease-in-out transform translate-x-0">
      {/* Header */}
      <div className="p-4 border-b border-arc-gray-extralight">
        <h3 className="text-lg font-semibold text-arc-blue-dark">Arc Assistant</h3>
      </div>

      {/* Messages Area */}
      <div className="flex-grow p-4 overflow-y-auto space-y-3 bg-arc-gray-extralight/30">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] p-3 rounded-xl shadow ${
                msg.sender === 'user' ? 'bg-arc-blue text-white rounded-br-none' :
                msg.sender === 'ai' ? 'bg-arc-gray-extralight text-arc-gray-dark rounded-bl-none' :
                'bg-yellow-100 text-yellow-700 border border-yellow-300 text-sm' // System / Error messages
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} /> {/* For auto-scrolling */}
      </div>

      {/* Input Area */}
      {error && <div className="p-2 text-center text-sm text-red-600 bg-red-100 border-t border-red-200">{error}</div>}
      <div className="p-3 border-t border-arc-gray-light bg-white">
        {/* Quick suggestion buttons from system messages */}
        {messages.filter(m => m.sender === 'system' && !m.text.toLowerCase().includes('error')).slice(0,2).map(suggestion => (
            <button
                key={suggestion.id}
                onClick={() => handleSendMessage(suggestion.text)}
                disabled={isLoading}
                className="text-xs bg-arc-blue-light hover:bg-arc-blue text-white py-1 px-2 rounded-full mr-1 mb-1 transition-colors disabled:opacity-50"
            >
                {suggestion.text.length > 30 ? suggestion.text.substring(0,27) + "..." : suggestion.text}
            </button>
        ))}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center space-x-2"
        >
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={isLoading ? "Waiting for response..." : "Ask a question or type / for commands..."}
            className="flex-grow p-2 border border-arc-gray-light rounded-lg focus:ring-2 focus:ring-arc-blue focus:border-transparent outline-none transition-shadow"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="p-2 bg-arc-blue hover:bg-arc-blue-dark text-white rounded-lg disabled:opacity-50 transition-colors"
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
              </svg>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
