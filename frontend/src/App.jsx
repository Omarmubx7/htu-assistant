import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import './App.css'

// Configure API base URL based on environment
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://omarmubaidin.pythonanywhere.com' 
  : '';

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL;
axios.defaults.timeout = 10000; // 10 second timeout

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm Athar Assistant, your university chatbot. I can help you find information about professors, courses, and more. How can I assist you today?",
      sender: 'bot',
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [isConnected, setIsConnected] = useState(true)
  const messagesEndRef = useRef(null)
  const [currentProfessor, setCurrentProfessor] = useState(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Check API health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await axios.get('/health')
        console.log('✅ API Health Check:', response.data)
        setIsConnected(true)
      } catch (error) {
        console.error('❌ API Health Check Failed:', error)
        setIsConnected(false)
        setMessages(prev => [...prev, {
          id: Date.now(),
          text: "⚠️ Warning: I'm having trouble connecting to the server. Some features may not work properly.",
          sender: 'bot',
          timestamp: new Date()
        }])
      }
    }
    
    checkHealth()
  }, [])

  const normalizeName = (name) => {
    return name.toLowerCase().replace(/\s+/g, ' ').trim()
  }

  const sendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await axios.post('/api/chat', {
        message: inputMessage,
        current_professor: currentProfessor
      })

      const botMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
      
      // Update current professor if found
      if (response.data.professor) {
        setCurrentProfessor(response.data.professor)
      }
      
      // Handle buttons if provided
      if (response.data.buttons && response.data.buttons.length > 0) {
        const buttonsMessage = {
          id: Date.now() + 2,
          text: "Please select one of the following options:",
          sender: 'bot',
          timestamp: new Date(),
          buttons: response.data.buttons
        }
        setMessages(prev => [...prev, buttonsMessage])
      }
      
    } catch (error) {
      console.error('Error sending message:', error)
      let errorMessage = "I'm sorry, I'm having trouble connecting to the server right now. Please try again later."
      
      if (error.response) {
        // Server responded with error status
        if (error.response.status === 400) {
          errorMessage = "I couldn't understand your request. Please try rephrasing your question."
        } else if (error.response.status === 500) {
          errorMessage = "I encountered an internal error. Please try again in a moment."
        } else if (error.response.data && error.response.data.error) {
          errorMessage = `Error: ${error.response.data.error}`
        }
      } else if (error.request) {
        // Network error
        errorMessage = "I can't reach the server right now. Please check your internet connection and try again."
        setIsConnected(false)
      }
      
      const errorBotMessage = {
        id: Date.now() + 1,
        text: errorMessage,
        sender: 'bot',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorBotMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode)
  }

  const renderMessageText = (text) => {
    // This function finds text surrounded by ** and makes it bold
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={i}>{part.slice(2, -2)}</strong>;
        }
        return part;
    });
  };

  return (
    <div className={`app ${isDarkMode ? 'dark' : 'light'}`}>
      <div className="chat-container">
        {/* Header */}
        <motion.div 
          className="chat-header"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="header-content">
            <div className="logo-section">
              <div className="logo">🎓</div>
              <div className="title-section">
                <h1>Athar Assistant</h1>
                <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
                  {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
                </div>
              </div>
            </div>
            <button 
              className="theme-toggle"
              onClick={toggleDarkMode}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              {isDarkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </motion.div>

        {/* Messages */}
        <div className="messages-container">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                className={`message ${message.sender}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <div className="message-content">
                  <div className="message-text">{renderMessageText(message.text)}</div>
                  <div className="message-time">
                    {message.timestamp.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {isLoading && (
            <motion.div
              className="message bot"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <motion.div 
          className="input-container"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="input-wrapper">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              rows="1"
              className="message-input"
            />
            <motion.button
              className="send-button"
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22,2 15,22 11,13 2,9"></polygon>
              </svg>
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default App
