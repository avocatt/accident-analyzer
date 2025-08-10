# LexIntake - AI-Powered Traffic Accident Analysis

LexIntake is a web application that automates the analysis of Turkish traffic accident reports (Kaza Tespit Tutanağı) using OpenAI's GPT-4o multimodal AI. It provides structured attorney briefings to streamline the legal intake process.

## Features

- **Document Upload**: Upload Kaza Tespit Tutanağı (PDF or images) and accident photos
- **AI Analysis**: GPT-4o analyzes documents to extract key information
- **Structured Output**: Generates comprehensive attorney briefings
- **Fault Assessment**: Preliminary fault analysis based on accident scenarios
- **Professional UI**: Clean, branded interface following legal industry standards
- **Data Security**: Automatic deletion of uploaded documents after processing

## Technology Stack

### Backend
- FastAPI (Python 3.11)
- OpenAI GPT-4o API
- PyMuPDF for PDF processing
- Pillow for image handling
- ReportLab for PDF generation

### Frontend
- React 18 with Vite
- Tailwind CSS for styling
- React Dropzone for file uploads
- Axios for API communication

### Deployment
- Docker & Docker Compose
- Coolify for automated deployment
- Nginx for serving frontend

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key with GPT-4o access
- Coolify instance (for deployment)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lexintake.git
cd lexintake
```

### 2. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Frontend URL (for CORS configuration)
FRONTEND_URL=https://lexintake.emreterzi.com

# Backend URL (for frontend API calls)
BACKEND_URL=https://lexintake-api.emreterzi.com
```

### 3. Local Development

#### Backend Development

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The backend will be available at `http://localhost:8000`

#### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Docker Deployment

Build and run with Docker Compose:

```bash
docker-compose up --build
```

Services will be available at:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## Coolify Deployment

1. **Create New Application** in Coolify
2. **Connect Git Repository**
3. **Set Build Pack** to Docker Compose
4. **Configure Environment Variables** in Coolify:
   - `OPENAI_API_KEY`
   - `FRONTEND_URL`
   - `BACKEND_URL`
5. **Deploy** - Coolify will handle SSL certificates and routing

## Usage

1. **Access the Application**: Navigate to your configured URL
2. **Upload Documents**: 
   - Upload the Kaza Tespit Tutanağı (required)
   - Add accident photos (optional, max 5)
   - Enter client information (optional)
3. **Analyze**: Click "Analyze My Case" to process documents
4. **Review Results**: 
   - View structured analysis in tabs
   - Download HTML or PDF briefing
5. **New Analysis**: Click "Analyze Another Case" to start over

## API Documentation

When running locally, API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
lexintake/
├── backend/
│   ├── api/              # API endpoints
│   ├── services/         # Business logic
│   │   ├── ai_service.py
│   │   ├── document_processor.py
│   │   └── briefing_generator.py
│   ├── models/           # Data models
│   ├── prompts/          # AI prompt templates
│   └── main.py           # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── styles/       # CSS files
│   │   └── App.jsx       # Main application
│   └── public/           # Static assets
├── docker-compose.yml    # Docker orchestration
├── .env.example          # Environment template
└── README.md
```

## Security Considerations

- All uploaded files are automatically deleted after processing
- CORS is configured to accept requests only from specified frontend URL
- API keys are stored as environment variables, never in code
- File size limits: 10MB per file
- Maximum 5 photos per submission

## Legal Notice

This tool provides automated analysis for attorney review purposes only. It does not constitute legal advice. Using this service does not create an attorney-client relationship.

## Development Guidelines

### Branding
- **Primary Color**: #0A2240 (Deep Sapphire Blue)
- **Accent Color**: #2ECC71 (Signal Green)
- **Typography**: Montserrat (headings), Lato (body)

### Code Style
- Python: Follow PEP 8
- JavaScript: ESLint configuration included
- Git: Conventional commits recommended

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Verify API key is correct
   - Check API quota and limits
   - Ensure GPT-4o access is enabled

2. **File Upload Failures**
   - Check file size (max 10MB)
   - Verify file format (PDF, PNG, JPG, etc.)
   - Ensure proper CORS configuration

3. **Docker Issues**
   - Clear Docker cache: `docker system prune`
   - Rebuild containers: `docker-compose build --no-cache`

## Performance Optimization

- Images are automatically resized to max 2000px
- PDF pages are limited to first 2 pages for analysis
- API calls include retry logic with exponential backoff
- Frontend uses lazy loading and code splitting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is proprietary software. All rights reserved.

## Support

For issues and questions, please contact the development team.

## Roadmap

### Version 2.0 (Planned)
- Law firm dashboard
- Embeddable widget version
- Custom branding options
- Voice memo support
- Integration with Turkish legal databases

### Future Enhancements
- Multi-language support
- CMS integrations
- Advanced analytics dashboard
- Batch processing capabilities