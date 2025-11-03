# 📋 Claims Description Normalizer

An AI-powered tool that transforms unstructured insurance claim descriptions into structured, actionable data using **Google Gemini 2.0 Flash API** and **Streamlit**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39.0-red)
![Gemini](https://img.shields.io/badge/Gemini-2.0--Flash-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 What This Project Does

Insurance companies receive hundreds of **unstructured claim descriptions** daily. Claims adjusters and customers write them freely, making them inconsistent and hard to process. This tool automatically extracts structured data from these descriptions using AI.

### Input Example:
```
Customer reported minor accident on rear bumper, scratches only, no injuries, 
estimated cost ₹7,000. Incident happened yesterday at parking lot near office.
```

### Output Example:
```json
{
  "loss_type": "Accident",
  "severity": "Low",
  "affected_assets": "Rear bumper (scratches)",
  "estimated_loss": "₹7,000",
  "incident_date": "Yesterday",
  "location": "Parking lot near office",
  "confidence": "High",
  "extraction_explanation": "Classified as 'Accident' with 'Low' severity..."
}
```

---

## ✨ Key Features

- **🤖 AI-Powered Extraction**: Uses Google Gemini 2.0 Flash for intelligent data extraction
- **📊 Structured Output**: Converts free text into clean JSON with 8 key fields
- **💡 Explainability**: AI explains *why* it made each classification decision
- **🔍 Keyword Highlighting**: Highlights important phrases that influenced the AI's decision
- **📈 Confidence Scoring**: Visual confidence meter with percentage indicators
- **🔄 Comparison Mode**: Side-by-side before/after view with quality metrics
- **🤖 AI Recommendations**: Intelligent action suggestions based on claim severity, confidence, and type
- **📜 History Tracking**: SQLite database stores all processed claims with search & filters
- **📈 Analytics Dashboard**: Interactive Plotly visualizations showing trends and insights
- **🎨 Professional UI**: Clean, intuitive Streamlit interface with color-coded severity levels
- **📥 Export Results**: Download extracted data as JSON
- **📚 Sample Library**: 12 pre-loaded realistic claim examples organized by category

---

## 🏗️ Project Structure

```
Claims_Description_Normalizer/
├── app.py                    # Main Streamlit application
├── database.py               # SQLite database operations for history
├── prompts.py                # Gemini prompt engineering & few-shot examples
├── utils.py                  # Helper functions (parsing, highlighting, validation)
├── pages/                    # Streamlit multi-page app
│   ├── 1_📜_History.py      # View and search claim history
│   ├── 2_ℹ️_About.py        # About page
│   └── 3_📈_Analytics.py    # Analytics dashboard with visualizations
├── requirements.txt          # Python dependencies
├── claims_history.db         # SQLite database file (auto-generated)
├── .env                      # Environment variables (API key)
├── .env.example              # Template for environment setup
├── .gitignore                # Git ignore rules
├── sample_claims.txt         # 12 realistic sample claims for testing
└── README.md                 # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/akashshah3/Claims-Description-Normalizer.git
   cd Claims-Description-Normalizer
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   
   The app will automatically open at `http://localhost:8501`

---

## 📖 How to Use

1. **Enter a Claim Description**
   - Type or paste a claim description in the text area
   - Or click one of the 12 sample claims in the sidebar

2. **Click "Normalize Claim"**
   - The AI processes the text and extracts structured data

3. **View Results in Multiple Tabs**
   - **Summary**: Quick overview with key metrics and confidence score
   - **Detailed View**: All extracted fields in an organized layout
   - **Explanation**: AI's reasoning with highlighted keywords
   - **JSON Output**: Structured data ready for export
   - **Comparison**: Side-by-side before/after view showing data transformation quality
   - **Recommendations**: AI-powered action suggestions for claim processing

4. **Review AI Recommendations**
   - See intelligent next-step suggestions based on claim analysis
   - Actions prioritized by urgency (Critical, High, Medium, Low)
   - Context-aware recommendations based on severity, loss type, and confidence
   - Clear reasoning for each recommended action

5. **Explore Comparison Mode**
   - See original messy text vs. clean structured output
   - View quality metrics (Token Count, Structure Quality, Completeness, Confidence)
   - Visual indicators show transformation improvements

6. **Download Results** (Optional)
   - Click "Download JSON" to save the extracted data

7. **Review History & Analytics**
   - Navigate to "📜 History" page to view all processed claims
   - Use "📈 Analytics" page for trends and insights

---

## 🧠 How It Works

### 1. **Prompt Engineering**
The system uses **few-shot prompting** to teach Gemini what to extract:
- System prompt defines the AI's role as an insurance analyst
- 4 example claim → output pairs demonstrate the desired format
- Clear instructions for JSON structure with 8 specific fields

### 2. **AI Processing**
When you submit a claim:
- Text is sent to Gemini 2.0 Flash with the engineered prompt
- AI analyzes keywords, context, and patterns
- Returns structured JSON with confidence levels

### 3. **Post-Processing**
The app enhances the output:
- Extracts keywords from the AI's explanation
- Highlights those keywords in the original text
- Validates all required fields are present
- Formats data for visual display

### 4. **Comparison & Quality Metrics**
The comparison mode visualizes the transformation:
- **Before**: Original unstructured text with warning indicators
- **After**: Clean structured table or JSON format
- **Quality Metrics**:
  - Token Count (words & characters)
  - Structure Quality (visual indicator)
  - Completeness Score (percentage of fields filled)
  - Confidence Level (AI's certainty)
- Side-by-side layout with color coding (yellow → green)

### 5. **AI-Powered Recommendations**
Intelligent action suggestions for claims adjusters:
- **Rule-Based Logic**: Analyzes severity, confidence, loss type, and estimated cost
- **Priority Levels**: Critical, High, Medium, Low
- **Action Categories**: Processing, Verification, Documentation, Administrative, Communication
- **Context-Aware**: Different recommendations based on specific claim characteristics
- **Examples**:
  - Low severity + high confidence → Fast-track approval
  - High severity → Detailed investigation, senior adjuster assignment
  - Theft claims → Verify police report
  - High-value claims (>$50k) → Supervisor approval required
  - Missing info → Request additional documentation

### 6. **Visualization**
Results are presented in an intuitive UI:
- Color-coded severity levels (green/orange/red/purple)
- Confidence meters and progress bars
- Tabbed interface for different views
- Professional card-based layout
- Interactive comparison mode with toggles
- Action cards with priority-based color coding

---

## 📊 Extracted Data Fields

| Field | Description | Example Values |
|-------|-------------|----------------|
| `loss_type` | Type of loss/incident | Accident, Fire, Flood, Theft, Water Damage, Storm, Vandalism |
| `severity` | Damage severity level | Low, Medium, High, Critical |
| `affected_assets` | What was damaged | "Car bumper", "Kitchen cabinets", "Vehicle engine" |
| `estimated_loss` | Monetary loss estimate | "₹7,000", "$5000", "Not specified" |
| `incident_date` | When it occurred | "Yesterday", "Oct 15, 2:00 AM", "Last week" |
| `location` | Where it happened | "Parking lot", "Kitchen", "Highway 101" |
| `confidence` | AI's confidence level | Low, Medium, High |
| `extraction_explanation` | AI's reasoning | "Classified as 'Fire' due to keywords..." |

---

## 🎨 UI Features

### Visual Indicators
- **Severity Colors**: 
  - 🟢 Low (Green)
  - 🟠 Medium (Orange)
  - 🔴 High (Red)
  - 🟣 Critical (Purple)

- **Confidence Colors**:
  - 🔴 Low (Red)
  - 🟠 Medium (Orange)
  - 🟢 High (Green)

### Interactive Elements
- Click sample claims in sidebar for instant testing
- Progress bar showing confidence percentage
- Expandable sections for detailed information
- One-click JSON download
- **Comparison Mode Features**:
  - Side-by-side before/after view
  - Toggle between Table and JSON output
  - Real-time quality metrics
  - Visual transformation indicators

### Comparison Mode Highlights
The **🔄 Comparison** tab provides:
- **Quality Metrics Dashboard**: 4 key metrics showing transformation quality
- **Before Panel**: Original text with unstructured data warning (yellow/orange theme)
- **After Panel**: Structured output with success indicators (green theme)
- **Transformation Summary**: Visual cards showing format, structure, and confidence improvements
- **Flexible Views**: Switch between table and JSON formats

---

## 🔧 Configuration

### Gemini API Settings
Adjust in `prompts.py`:
```python
GEMINI_CONFIG = {
    "temperature": 0.3,  # Lower = more consistent
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 1024,
}
```

### Custom Fields
To add/modify extracted fields:
1. Update `prompts.py` - add to system prompt and examples
2. Update `utils.py` - add to `required_fields` list
3. Update `app.py` - add display logic

---

## 🚢 Deployment on Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Set main file: `app.py`
   - Add secret: `GEMINI_API_KEY` in Advanced settings

3. **Your app will be live!**
   - URL: `https://your-app-name.streamlit.app`

---

## 📝 Sample Claims Included

The project includes 12 diverse sample claims:
1. Minor Car Accident
2. Flood Damage
3. Kitchen Fire
4. Water Leakage
5. Car Theft
6. Storm Damage
7. Vandalism
8. House Fire (Critical)
9. Slip and Fall
10. Hail Damage
11. Pipe Burst
12. Multi-Vehicle Collision

---

## 🛠️ Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Interactive web interface |
| **AI/LLM** | Google Gemini 2.0 Flash | Natural language understanding |
| **Language** | Python 3.8+ | Backend logic |
| **Data Format** | JSON | Structured output |
| **Styling** | Custom CSS | Professional UI |

---

## 💡 Future Enhancements

- [ ] Batch processing (upload CSV with multiple claims)
- [ ] Fraud risk detection (suspicious pattern analysis)
- [ ] Claim history tracking with local database
- [ ] Multi-language support
- [ ] Voice input for claim descriptions
- [ ] PDF/Image claim upload with OCR
- [ ] Comparison mode (before/after normalization)
- [ ] Export to Excel/CSV
- [ ] Real-time validation against policy rules

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## � Changelog

### Version 1.1 (October 31, 2025)
- **🐛 Bug Fix**: Fixed dark mode visibility issue in keyword highlighting
  - Added explicit black text color (`#000000`) to highlighted keywords
  - Added explicit black text color to highlight-box container
  - Improved line-height for better readability
  - Ensures proper contrast in both light and dark themes

### Version 1.0 (October 31, 2025)
- Initial release with core features
- Gemini 2.0 Flash integration
- 8-field structured extraction
- Keyword highlighting and explainability
- Confidence scoring
- Sample claims library

---

## �📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini API** for powerful language understanding
- **Streamlit** for the amazing web framework
- **Insurance Industry** for the real-world problem inspiration

---

## 📞 Contact

**Akash Shah**
- GitHub: [@akashshah3](https://github.com/akashshah3)
- Project Link: [Claims-Description-Normalizer](https://github.com/akashshah3/Claims-Description-Normalizer)

---

<div align="center">

**Made with ❤️ and AI**

⭐ Star this repo if you find it helpful!

</div>
