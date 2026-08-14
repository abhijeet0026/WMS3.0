import React, { useState, useEffect, useRef } from 'react';
import { sendVoiceQuery } from '../../api/client';
import { useAuth } from '../../hooks/useAuth';
import { Mic, MicOff, X, Send, Volume2, Bot, Sparkles, CheckCircle2 } from 'lucide-react';

export const AssistantWidget: React.FC = () => {
  const { currentUser } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'assistant'; text: string; actionExecuted?: boolean }>>([
    {
      sender: 'assistant',
      text: "Hello! I'm your Whitfield WMS Voice Assistant. You can speak or type commands like: 'How many units of SKU-101 do we have?' or 'Ship order ORD-101'.",
    },
  ]);

  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Initialize Web Speech API recognition if supported
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        handleSend(transcript);
        setIsListening(false);
      };

      recognition.onerror = () => {
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleListen = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser. Please use Chrome/Edge or type your question below!');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleSend = async (overrideText?: string) => {
    const textToSend = overrideText || inputText;
    if (!textToSend.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { sender: 'user', text: textToSend }]);
    setInputText('');

    try {
      const warehouse = currentUser?.facility_scope ?? undefined;
      const res = await sendVoiceQuery(textToSend, warehouse);
      setMessages(prev => [
        ...prev,
        { sender: 'assistant', text: res.spoken_response, actionExecuted: res.action_executed },
      ]);
      speakText(res.spoken_response);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { sender: 'assistant', text: 'Sorry, I had trouble reaching the assistant backend.' },
      ]);
    }
  };

  return (
    <div style={{ position: 'fixed', bottom: '1.5rem', right: '1.5rem', zIndex: 1000 }}>
      
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={{
            width: '56px',
            height: '56px',
            borderRadius: '50%',
            backgroundColor: 'var(--color-orange-primary)',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: 'none',
            boxShadow: '0 8px 24px rgba(255, 106, 19, 0.4)',
            cursor: 'pointer'
          }}
        >
          <Bot size={28} />
        </button>
      )}

      {/* Expanded Assistant Drawer */}
      {isOpen && (
        <div
          style={{
            width: '380px',
            height: '520px',
            backgroundColor: '#ffffff',
            borderRadius: '12px',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            boxShadow: '0 12px 40px rgba(0, 0, 0, 0.2)',
            border: '1px solid #e5e7eb',
          }}
        >
          {/* Drawer Header */}
          <div style={{ padding: '1rem', backgroundColor: '#1C1C1A', color: '#ffffff', borderBottom: '1px solid #374151', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <Bot size={22} color="var(--color-orange-primary)" />
              <div>
                <h4 style={{ fontSize: '0.95rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  WMS Hands-free Assistant <Sparkles size={12} color="#f59e0b" />
                </h4>
                <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Voice & Chat Operational Q&A</span>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} style={{ background: 'transparent', border: 'none', color: '#9ca3af', cursor: 'pointer' }}>
              <X size={20} />
            </button>
          </div>

          {/* Messages Body */}
          <div style={{ flex: 1, padding: '1rem', backgroundColor: '#f9fafb', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {messages.map((m, idx) => (
              <div
                key={idx}
                style={{
                  alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '85%',
                  backgroundColor: m.sender === 'user' ? 'var(--color-orange-primary)' : '#ffffff',
                  color: m.sender === 'user' ? '#ffffff' : '#1f2937',
                  padding: '0.7rem 0.9rem',
                  borderRadius: '12px',
                  fontSize: '0.85rem',
                  lineHeight: '1.4',
                  border: m.sender === 'user' ? 'none' : '1px solid #e5e7eb',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                }}
              >
                {m.text}
                {m.actionExecuted && (
                  <div style={{ fontSize: '0.72rem', color: '#10b981', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <CheckCircle2 size={12} /> Transaction Executed
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Status Indicator */}
          {(isListening || isSpeaking) && (
            <div style={{ backgroundColor: '#fffbeb', padding: '0.4rem 1rem', fontSize: '0.75rem', color: '#d97706', display: 'flex', alignItems: 'center', gap: '0.5rem', borderTop: '1px solid #e5e7eb' }}>
              <Volume2 size={14} className="spin" />
              <span>{isListening ? 'Listening to voice command...' : 'Speaking response...'}</span>
            </div>
          )}

          {/* Controls Footer */}
          <div style={{ padding: '0.75rem 1rem', backgroundColor: '#ffffff', borderTop: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            
            <button
              onClick={toggleListen}
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: isListening ? '#fee2e2' : '#f3f4f6',
                border: `1px solid ${isListening ? '#fca5a5' : '#e5e7eb'}`,
                color: isListening ? '#ef4444' : '#6b7280',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                cursor: 'pointer'
              }}
              title="Click to speak"
            >
              {isListening ? <MicOff size={20} /> : <Mic size={20} />}
            </button>

            <input
              type="text"
              placeholder="Ask stock count or ship order..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              className="app-input"
              style={{ flex: 1, padding: '0.5rem 0.75rem', fontSize: '0.85rem', marginTop: 0 }}
            />

            <button
              onClick={() => handleSend()}
              className="btn-primary"
              style={{ padding: '0.5rem 0.75rem' }}
            >
              <Send size={16} />
            </button>

          </div>

        </div>
      )}

    </div>
  );
};
