"use client";

import React, { useState } from "react";
import { Chatbot } from "./chatbot/Chatbot";

interface FloatingChatWidgetProps {
  onTasksUpdate?: (tasks: any[]) => void;
}

const FloatingChatWidget: React.FC<FloatingChatWidgetProps> = ({
  onTasksUpdate,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  // 🔐 USER ID GETTER (same logic, cleaned)
  const getUserId = () => {
    if (typeof window === "undefined") return null;

    try {
      const userStr = localStorage.getItem("better-auth-user");
      if (userStr) {
        const user = JSON.parse(userStr);
        if (user?.id) return user.id;
      }

      const token = localStorage.getItem("better-auth-token");
      if (token) {
        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload?.sub ?? null;
      }
    } catch (err) {
      console.error("User ID error:", err);
    }

    return null;
  };

  const userId = getUserId();

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* 🔵 CHAT WINDOW */}
      {isOpen && (
        <div className="w-96 h-[520px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden animate-fadeIn">
          {/* HEADER */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-white/20 rounded-full p-1">
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold">AI Todo Assistant</h3>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-white/20 rounded-full p-1 transition"
            >
              ✕
            </button>
          </div>

          {/* BODY */}
          <div className="flex-1 overflow-y-auto p-2 bg-gray-50">
            {userId ? (
              <Chatbot userId={userId} onTasksUpdate={onTasksUpdate} />
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500 text-sm text-center px-6">
                Please login to use the AI Todo Assistant.
              </div>
            )}
          </div>
        </div>
      )}

      {/* 🟢 FLOATING BUTTON */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-4 rounded-full shadow-xl hover:scale-105 transition-all"
        >
          <svg
            className="h-6 w-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
        </button>
      )}
    </div>
  );
};

export default FloatingChatWidget;
