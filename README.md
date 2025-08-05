# Insurance AI Assistant

A comprehensive AI-powered insurance document processing and chat assistant with FastAPI backend and Next.js frontend.

## 🚀 Features

### Core Functionality
- **Document Processing**: Upload and process insurance documents (PDF, images, DOCX, TXT) up to 50-100 pages
- **OCR Integration**: Advanced text extraction using Tesseract OCR
- **AI Chat Assistant**: Powered by Groq API and GLM-4.5-FLASH model
- **Automatic Summarization**: Generate detailed summaries of uploaded documents
- **Real-time Streaming**: 30ms response time optimization with streaming support

### API Management
- **Public API Generation**: Create and manage API keys for external users
- **Rate Limiting**: Configurable rate limits per API key
- **Usage Analytics**: Comprehensive analytics dashboard
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### Frontend Integration
- **Seamless Integration**: Original design preserved with backend connectivity
- **File Upload Support**: Drag-and-drop document upload (PDF, images, DOCX, TXT)
- **Real-time AI Chat**: Streaming responses with document context
- **Analytics Dashboard**: Accessible via arrow button (→) in top right
- **Connection Status**: Live backend connectivity indicator
- **Responsive Design**: Mobile-friendly interface maintained

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM with SQLite
- **Groq SDK**: AI model integration
- **Tesseract**: OCR processing
- **PyPDF2**: PDF text extraction
- **Pillow**: Image processing

### Frontend
- **Next.js 15**: React framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **Lucide React**: Beautiful icons

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Single Command Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd hackathon-project
```

2. **Configure environment**
```bash
# Edit python-backend/.env with your API keys
# The GROQ_API_KEY is already configured
```

3. **Start everything with one command**
```bash
# Windows (Recommended)
start-simple.bat

# Or manually start both services:
# Terminal 1 - Backend
cd python-backend
python main.py

# Terminal 2 - Frontend
npm run dev
```

This will:
- Start the FastAPI backend on http://localhost:8000
- Start the Next.js frontend on http://localhost:3000
- Connect frontend to backend automatically
- Enable real-time AI chat with document processing

### Manual Setup

If you prefer to start services manually:

#### Backend Setup
```bash
cd python-backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
npm install
npm run dev
```

## 📋 Configuration

### Environment Variables

Create `python-backend/.env` with the following:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
GLM_API_KEY=your_glm_api_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=True
MAX_FILE_SIZE=52428800
```

### API Keys

1. **Groq API Key**: Get from [Groq Console](https://console.groq.com/)
2. **GLM API Key**: Get from [GLM Platform](https://open.bigmodel.cn/) (optional)

## 📖 API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Document Processing
- `POST /api/documents/upload` - Upload and process documents
- `GET /api/documents/{id}` - Get document details
- `GET /api/documents` - List all documents

#### AI Chat
- `POST /api/chat` - Chat with AI assistant
- `POST /api/frontend/message` - Frontend integration endpoint

#### API Management
- `POST /api/keys/generate` - Generate API key
- `GET /api/keys` - List API keys
- `GET /api/keys/{id}/stats` - Get usage statistics

#### Analytics
- `GET /api/analytics/dashboard` - Dashboard data
- `GET /api/analytics/health` - System health

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd python-backend
python test_api.py
```

This will test:
- Health checks
- Document upload and processing
- AI chat functionality
- API key generation
- Analytics endpoints
- Frontend integration

## 🎯 Using the Insurance AI Assistant

### **💬 Chat Interface**
1. **Upload documents first** by clicking the paperclip icon (📎)
2. Supported formats: PDF, images (JPG, PNG, etc.), DOCX, TXT
3. **Then type your insurance-related questions** in the floating input field
4. Get real-time AI responses based on your uploaded documents using GLM-4.5-FLASH

### **📄 Document Processing**
- **Upload**: Click paperclip (📎) to upload insurance documents
- **Processing**: Automatic OCR and text extraction (no AI processing yet)
- **Storage**: Document text is stored and ready for AI analysis
- **Context**: Documents are remembered for all future questions in the session

### **📊 Analytics Dashboard**

Access the analytics dashboard by clicking the arrow button (→) in the top right of the website. Features include:

- **Usage Statistics**: Request counts, response times, success rates
- **API Key Management**: Create, deactivate, and monitor API keys
- **Document Analytics**: Processing statistics and document types
- **System Health**: Real-time system status and performance metrics

### **🔌 Connection Status**
- **Green indicator**: Backend connected and ready
- **Red indicator**: Backend disconnected (demo mode)
- **Auto-reconnection**: Checks connectivity every 30 seconds

## 🔧 Development

### Project Structure
```
hackathon-project/
├── python-backend/          # FastAPI backend
│   ├── main.py             # Main application
│   ├── services/           # Business logic
│   ├── models/             # Database models
│   ├── utils/              # Utilities
│   └── requirements.txt    # Python dependencies
├── src/                    # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   └── lib/               # Utilities
├── start.py               # Single-command startup
└── README.md              # This file
```

### Adding New Features

1. **Backend**: Add new endpoints in `main.py` or create new service modules
2. **Frontend**: Add new components in `src/components/`
3. **Database**: Add new models in `models/database.py`

## 🚨 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check if port 8000 is available
   - Verify GROQ_API_KEY is set in .env
   - Install missing dependencies: `pip install -r requirements.txt`

2. **Frontend won't start**
   - Check if port 3000 is available
   - Install dependencies: `npm install`
   - Clear Next.js cache: `rm -rf .next`

3. **Document processing fails**
   - Ensure Tesseract is installed on your system
   - Check file size limits (default 50MB)
   - Verify supported file formats

4. **AI responses are slow**
   - Check your internet connection
   - Verify API keys are valid
   - Monitor rate limits

### Logs

- **Backend logs**: Check `python-backend/logs/app.log`
- **Frontend logs**: Check browser console
- **Startup logs**: Check terminal output

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the troubleshooting section
- Review API documentation
- Run the test suite to identify issues

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
