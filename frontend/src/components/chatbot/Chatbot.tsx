"use client";

import React, { useState, useEffect, useRef } from 'react';
import api from '@/lib/api';
import { Task } from '@/lib/types';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';

interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
}

interface ChatbotProps {
  userId: string;
  onTasksUpdate?: (tasks: any[]) => void;
}

interface ChatMessageInterface {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: Date;
}

export const Chatbot: React.FC<ChatbotProps> = ({ userId, onTasksUpdate }) => {
  const [messages, setMessages] = useState<ChatMessageInterface[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation history when component mounts
  useEffect(() => {
    loadConversationHistory();
  }, []);

  // Load conversations list when component mounts
  useEffect(() => {
    loadConversationsList();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversationsList = async () => {
    try {
      // Fetch the list of conversations from the backend
      const response = await api.get('/api/v1/conversations');
      const conversationsData = response.data;

      const formattedConversations: Conversation[] = conversationsData.map((conv: any) => ({
        id: conv.id,
        title: conv.title,
        createdAt: new Date(conv.created_at),
        updatedAt: new Date(conv.updated_at),
      }));

      setConversations(formattedConversations);
    } catch (err) {
      console.error('Error loading conversations list:', err);
    }
  };

  const loadConversationHistory = async () => {
    try {
      setError(null);
      // In a real implementation, we would fetch the conversation history
      // For now, we'll initialize with a welcome message
      const welcomeMessage: ChatMessageInterface = {
        id: 'welcome',
        role: 'assistant',
        content: 'Hello! I\'m your AI assistant. You can ask me to manage your tasks using natural language. Try saying "Add task: buy groceries" or "Show my tasks".',
        createdAt: new Date(),
      };
      setMessages([welcomeMessage]);
    } catch (err) {
      console.error('Error loading conversation history:', err);
      setError('Failed to load conversation history. Please try again later.');
      const errorMessage: ChatMessageInterface = {
        id: 'error-load',
        role: 'assistant',
        content: 'Sorry, I had trouble loading our conversation history. Please try refreshing the page.',
        createdAt: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const switchConversation = async (conversationId: string) => {
    try {
      setSelectedConversation(conversationId);
      setActiveConversationId(conversationId);

      // Fetch the specific conversation
      const response = await api.get(`/api/v1/conversations/${conversationId}`);
      const conversationData = response.data;

      // Format the messages
      const formattedMessages: ChatMessageInterface[] = conversationData.messages.map((msg: any) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        createdAt: new Date(msg.created_at),
      }));

      setMessages(formattedMessages);
    } catch (err) {
      console.error('Error switching conversation:', err);
      setError('Failed to switch conversation. Please try again.');
    }
  };

  const handleSendMessage = async (content: string) => {
    // Logging
    console.log(`[${new Date().toISOString()}] Sending message from user ${userId}: ${content}`);

    // Frontend validation to prevent unauthorized access attempts
    if (!userId || typeof userId !== 'string' || userId.trim() === '') {
      setError('Invalid user session. Please log in again.');
      console.error(`[${new Date().toISOString()}] Invalid user ID: ${userId}`);
      return;
    }

    // Validation
    if (!content.trim()) {
      setError('Message cannot be empty');
      console.warn(`[${new Date().toISOString()}] Empty message validation failed for user ${userId}`);
      return;
    }

    if (content.length > 1000) {
      setError('Message is too long (maximum 1000 characters)');
      console.warn(`[${new Date().toISOString()}] Message length validation failed for user ${userId}`);
      return;
    }

    if (isLoading) {
      setError('Please wait for the previous message to be processed');
      console.warn(`[${new Date().toISOString()}] Attempted to send message while loading for user ${userId}`);
      return;
    }

    // Additional validation for potentially harmful content
    const dangerousPatterns = [
      /(\.\.\/|\.\.\\)/, // Directory traversal
      /(<script|javascript:|vbscript:)/i, // Script injection
    ];

    for (const pattern of dangerousPatterns) {
      if (pattern.test(content)) {
        setError('Message contains potentially unsafe content and was rejected.');
        console.warn(`[${new Date().toISOString()}] Blocked potentially unsafe content from user ${userId}: ${content}`);
        return;
      }
    }

    setError(null);

    // Add user message to the chat
    const userMessage: ChatMessageInterface = {
      id: Date.now().toString(),
      role: 'user',
      content,
      createdAt: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Log the message addition
    console.log(`[${new Date().toISOString()}] Added message to UI for user ${userId}`);

    try {
      // Parse the user's intent and call appropriate backend APIs
      const lowerContent = content.toLowerCase().trim();

      // For all messages, send to the AI for general conversation
      // The backend will handle task operations based on the content
      // But first check if we have an active conversation
      let response;
      if (activeConversationId) {
        // Add user message to the conversation
        response = await api.post(`/api/v1/conversations/${activeConversationId}/messages`, {
          content: content
        });
      } else {
        // Initiate a new conversation
        response = await api.post('/api/v1/conversations/initiate', {
          content: content
        });

        // If this was a new conversation, update the active conversation
        if (response.data.conversation_id) {
          setActiveConversationId(response.data.conversation_id);
          setSelectedConversation(response.data.conversation_id);
        }
      }

      // Process the response
      const { user_message, ai_response, updated_tasks } = response.data;
      console.log('Chatbot response data:', response.data); // Debug log
      console.log('Updated tasks received:', updated_tasks); // Debug log

      // Add both user and AI messages to the chat
      setMessages(prev => [
        ...prev,
        {
          id: user_message.id,
          role: user_message.role,
          content: user_message.content,
          createdAt: new Date(user_message.created_at)
        },
        {
          id: ai_response.id,
          role: ai_response.role,
          content: ai_response.content,
          createdAt: new Date(ai_response.created_at)
        }
      ]);

      // Check if updated_tasks is available in the response and use it
      if (updated_tasks && Array.isArray(updated_tasks)) {
        console.log('Calling onTasksUpdate with', updated_tasks.length, 'tasks'); // Debug log
        // Call the callback function to update tasks in the parent component
        if (onTasksUpdate) {
          onTasksUpdate(updated_tasks);
        }
      } else {
        console.log('No updated_tasks in response, using fallback'); // Debug log
        // Fallback: Refresh the task list after a short delay to allow the backend to process
        setTimeout(async () => {
          try {
            const tasksResponse = await api.get('/api/v1/tasks');
            console.log('Fetched tasks after operation:', tasksResponse.data); // Debug log
            // Call the callback function to update tasks in the parent component
            if (onTasksUpdate) {
              onTasksUpdate(tasksResponse.data);
            }
          } catch (refreshError) {
            console.error('Error refreshing tasks after chatbot operation:', refreshError);
          }
        }, 1000); // 1 second delay to ensure the operation completes
      }

      console.log(`[${new Date().toISOString()}] Processed user intent for user ${userId}`);
    } catch (err: any) {
      console.error(`[${new Date().toISOString()}] Error processing message for user ${userId}:`, err);

      // Add error message to chat
      let errorMessageText = 'Sorry, I encountered an error processing your request. Please try again.';

      // Provide more specific error messages based on error type
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        errorMessageText = 'Request timed out. Please check if the backend server is running.';
      } else if (err.response?.status === 401 || err.response?.status === 403) {
        errorMessageText = 'Authentication error. Please log in again.';
      } else if (err.response?.status === 404) {
        errorMessageText = 'The requested resource was not found.';
      } else if (err.response?.status === 500) {
        errorMessageText = 'Server error. Please try again later.';
      } else if (!userId || userId === 'fallback-user-id') {
        errorMessageText = 'User not authenticated. Please log in first.';
      }

      const errorMessage: ChatMessageInterface = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: errorMessageText,
        createdAt: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      console.log(`[${new Date().toISOString()}] Finished processing message for user ${userId}`);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-xl overflow-hidden border border-gray-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-4">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-500 rounded-full p-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold">AI Todo Assistant</h2>
            <p className="text-blue-200 text-sm">Powered by Cohere AI</p>
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Conversation History Sidebar */}
        <div className="w-1/3 border-r bg-white p-3 overflow-y-auto hidden md:block shadow-inner">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-semibold text-gray-700">Recent Conversations</h3>
            <button
              className="text-blue-500 hover:text-blue-700"
              onClick={async () => {
                // Create a new conversation via the backend
                try {
                  const response = await api.post('/api/v1/conversations', {
                    title: 'New Conversation'
                  });

                  const newConv: Conversation = {
                    id: response.data.id,
                    title: response.data.title,
                    createdAt: new Date(response.data.created_at),
                    updatedAt: new Date(response.data.updated_at)
                  };

                  setConversations([newConv, ...conversations]);
                  setActiveConversationId(newConv.id);
                  setSelectedConversation(newConv.id);

                  // Reset messages for the new conversation
                  const welcomeMessage: ChatMessageInterface = {
                    id: 'welcome',
                    role: 'assistant',
                    content: 'Hello! I\'m your AI assistant. You can ask me to manage your tasks using natural language. Try saying "Add task: buy groceries" or "Show my tasks".',
                    createdAt: new Date(),
                  };
                  setMessages([welcomeMessage]);
                } catch (error) {
                  console.error('Error creating new conversation:', error);
                }
              }}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className={`p-3 mb-2 rounded-lg cursor-pointer transition-all duration-200 ${
                selectedConversation === conv.id
                  ? 'bg-blue-100 border border-blue-300 shadow-sm'
                  : 'bg-gray-100 hover:bg-gray-200'
              }`}
              onClick={() => switchConversation(conv.id)}
            >
              <div className="font-medium text-gray-800 truncate">{conv.title || 'Untitled Conversation'}</div>
              <div className="text-xs text-gray-500 mt-1">
                {conv.updatedAt.toLocaleDateString()} • {conv.updatedAt.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
              </div>
            </div>
          ))}
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-blue-50 to-indigo-50">
            {error && (
              <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded shadow" role="alert">
                <p className="font-bold">Error</p>
                <p>{error}</p>
              </div>
            )}
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                role={message.role}
                content={message.content}
                timestamp={message.createdAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              />
            ))}
            {isLoading && (
              <div className="flex items-center space-x-3 p-4">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
                <span className="text-gray-600 italic">AI is thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t bg-white p-4 shadow-inner">
            <ChatInput onSend={handleSendMessage} disabled={isLoading} />
            <p className="text-xs text-gray-500 mt-2 text-center">
              AI Assistant can help you manage tasks using natural language
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

