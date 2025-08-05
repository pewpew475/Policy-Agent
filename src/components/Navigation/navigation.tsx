"use client"
import { useRef, useEffect } from 'react';
import { SquareArrowRight, MessageSquare, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';


interface Message {
  text: string;
  isAi: boolean;
}

interface ChatHistory {
  id: string;
  title: string;
  messages: Message[];
  timestamp: Date;
}

interface NavigationProps {
  isOpen: boolean;
  onToggle: () => void;
  onNewChat: () => void;
  onLoadChat: (chat: ChatHistory) => void;
  onDeleteChat: (chatId: string) => void;
  chatHistory: ChatHistory[];
  currentChatId: string | null;
}

export default function SidebarNavigation({
  isOpen,
  onToggle,
  onNewChat,
  onLoadChat,
  onDeleteChat,
  chatHistory,
  currentChatId
}: NavigationProps) {
    const sidebarRef = useRef<HTMLDivElement>(null);

    const startNewChat = () => {
        onNewChat();
        onToggle(); // Close sidebar after creating new chat
    };

    const formatTimestamp = (timestamp: Date) => {
        const now = new Date();
        const diff = now.getTime() - timestamp.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) {
            return 'Today';
        } else if (days === 1) {
            return 'Yesterday';
        } else if (days < 7) {
            return `${days} days ago`;
        } else {
            return timestamp.toLocaleDateString();
        }
    };


    // Close on outside click
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (
                sidebarRef.current &&
                !sidebarRef.current.contains(event.target as Node)
            ) {
                onToggle();
            }
        }

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        } else {
            document.removeEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen, onToggle]);

    return (
        <div className="h-screen bg-white border-r border-gray-200">
            <div
                ref={sidebarRef}
                className="h-full w-64 flex flex-col"
            >
                <div className="p-4 h-full flex flex-col">
                    <div className="flex items-center justify-between mb-4">
                        <h1 className="text-xl font-bold">Navigation</h1>
                        <button onClick={onToggle}>
                            <SquareArrowRight className="w-6 h-6 cursor-pointer" />
                        </button>
                    </div>

                    <Button variant="default" className="w-full cursor-pointer mb-4" onClick={startNewChat}>
                        + New Chat
                    </Button>

                    {/* Chat History */}
                    <div className="flex-1 overflow-y-auto">
                        <h2 className="text-sm font-semibold text-gray-600 mb-2">Previous Chats</h2>
                        <div className="space-y-2">
                            {chatHistory.map((chat) => (
                                <div
                                    key={chat.id}
                                    className={`group p-3 rounded-lg cursor-pointer transition-colors hover:bg-gray-100 ${
                                        currentChatId === chat.id ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50'
                                    }`}
                                >
                                    <div className="flex items-start gap-2">
                                        <MessageSquare className="w-4 h-4 mt-0.5 text-gray-500 flex-shrink-0" />
                                        <div
                                            className="flex-1 min-w-0"
                                            onClick={() => {
                                                onLoadChat(chat);
                                                onToggle();
                                            }}
                                        >
                                            <p className="text-sm font-medium text-gray-900 truncate">
                                                {chat.title}
                                            </p>
                                            <p className="text-xs text-gray-500 mt-1">
                                                {formatTimestamp(chat.timestamp)}
                                            </p>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onDeleteChat(chat.id);
                                            }}
                                            className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-100 rounded"
                                        >
                                            <Trash2 className="w-4 h-4 text-red-500" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                            {chatHistory.length === 0 && (
                                <p className="text-sm text-gray-500 text-center py-4">
                                    No previous chats
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
