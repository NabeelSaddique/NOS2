# 📊 Newcastle-Ottawa Scale Assessment Tool

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Advanced Systematic Risk of Bias Assessment for Observational Studies**

A comprehensive, publication-ready Newcastle-Ottawa Scale (NOS) assessment tool designed for systematic reviews and meta-analyses. This tool provides an intuitive interface for assessing study quality with advanced analytics and visualization capabilities.

## 🌟 Features

### 📋 Core Assessment
- **Complete NOS Implementation**: Full support for Cohort, Case-Control, and Cross-Sectional studies
- **Interactive Assessment Forms**: Tab-based interface with real-time feedback
- **Progress Tracking**: Visual progress indicators during assessment
- **Star-based Scoring**: Automatic calculation with quality ratings

### 📊 Advanced Visualizations
- **Robvis-style Plots**: Publication-ready risk of bias summary charts
- **Domain Heatmaps**: Color-coded domain performance matrices
- **Quality Distributions**: Statistical charts and trend analysis
- **Traffic Light Plots**: Individual study risk assessment visualization

### 📈 Analytics & Reports
- **Publication Tables**: Ready-to-use summary tables for manuscripts
- **Statistical Analysis**: Comprehensive quality metrics and trends
- **Methodological Recommendations**: Automated quality improvement suggestions
- **Comparative Analysis**: Side-by-side study comparisons

### 💾 Data Management
- **Multiple Export Formats**: CSV (detailed/summary), JSON (complete)
- **Backup & Restore**: Full data backup capabilities
- **Search & Filter**: Advanced study portfolio management
- **Import/Export**: Seamless data transfer

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8 or higher
```

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/nos-assessment-tool.git
cd nos-assessment-tool

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run nos_app.py
```

### Requirements
```txt
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
```

## 📖 Usage Guide

### 1. Adding Studies
1. Navigate to **"📝 Add New Study"**
2. Fill in study information (name, authors, journal, etc.)
3. Complete the NOS assessment using the tabbed interface
4. Add notes and save the assessment

### 2. Viewing Assessments
- **Dashboard**: Overview of all assessments with summary statistics
- **Study Portfolio**: Detailed view with search, filter, and sort options
- **Individual Studies**: Expandable cards with domain breakdowns

### 3. Generating Reports
1. Go to **"📊 Generate Report"**
2. Select desired components:
   - Summary statistics
   - Risk of bias plots
   - Domain heatmaps
   - Publication tables
   - Methodological recommendations
3. Download publication-ready outputs

### 4. Advanced Analytics
- **Temporal Analysis**: Quality trends by publication year
- **Domain Performance**: Comparative domain analysis
- **Quality Metrics**: Advanced statistical measures
- **Improvement Analysis**: Identification of common issues

## 📊 Assessment Criteria

### Cohort Studies (Max 9 stars)
- **Selection** (4 stars): Representativeness, cohort selection, exposure ascertainment, outcome baseline
- **Comparability** (2 stars): Control for confounding factors
- **Outcome** (3 stars): Assessment quality, follow-up length, completeness

### Case-Control Studies (Max 9 stars)
- **Selection** (4 stars): Case definition, representativeness, control selection, control definition
- **Comparability** (2 stars): Control for confounding factors
- **Exposure** (3 stars): Ascertainment quality, method consistency, response rates

### Cross-Sectional Studies (Max 8 stars)
- **Selection** (4 stars): Representativeness, sample size, non-respondents, exposure measurement
- **Comparability** (2 stars): Control for confounding factors
- **Outcome** (2 stars): Assessment quality, statistical methods

## 🎯 Quality Interpretation

| Stars | Cohort/Case-Control | Cross-Sectional | Quality Rating |
|-------|-------------------|-----------------|----------------|
| 7-9   | Good Quality      | 6-8             | 🟢 Low Risk    |
| 5-6   | Fair Quality      | 4-5             | 🟡 Some Concerns |
| 0-4   | Poor Quality      | 0-3             | 🔴 High Risk   |

## 📁 File Structure

```
nos-assessment-tool/
├── nos_app.py              # Main application file
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── docs/                  # Documentation
│   ├── user-guide.md      # Detailed user guide
│   ├── api-reference.md   # Code documentation
│   └── examples/          # Example assessments
├── assets/                # Static assets
│   ├── images/           # Screenshots and logos
│   └── templates/        # Export templates
└── tests/                # Unit tests
    ├── test_calculations.py
    └── test_exports.py
```

## 🔧 Development

### Setting Up Development Environment
```bash
# Clone and setup
git clone https://github.com/your-username/nos-assessment-tool.git
cd nos-assessment-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run nos_app.py --server.runOnSave=true
```

### Code Structure
- **Part 1**: Core setup and configuration
- **Part 2**: Calculation functions and utilities
- **Part 3**: Assessment interface components
- **Part 4**: Main application interface
- **Part 5**: Reports and analytics
- **Part 6**: Assessment guide and footer

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Documentation

### For Users
- [User Guide](docs/user-guide.md) - Comprehensive usage instructions
- [Assessment Best Practices](docs/best-practices.md) - Quality assessment guidelines
- [Export Formats](docs/export-formats.md) - Data export documentation

### For Developers
- [API Reference](docs/api-reference.md) - Code documentation
- [Development Guide](docs/development.md) - Setup and contribution guidelines
- [Testing](docs/testing.md) - Testing procedures

## 🎓 About the Developer

**Muhammad Nabeel Saddique**
- 4th Year MBBS Student, King Edward Medical University, Lahore, Pakistan
- Research Focus: Systematic Review, Meta-Analysis, Evidence-Based Medicine
- Founder: Nibras Research Academy

### Research Tools Expertise
- Literature Management: Rayyan, Zotero, EndNote
- Data Extraction: WebPlotDigitizer, Meta-Converter
- Statistical Analysis: RevMan, MetaXL, Jamovi, CMA, OpenMeta, R Studio

## 📊 Use Cases

### Academic Research
- Systematic reviews and meta-analyses
- Quality assessment for literature reviews
- Research methodology courses
- Evidence-based medicine training

### Clinical Practice
- Clinical guideline development
- Quality improvement projects
- Evidence synthesis for practice recommendations
- Research proposal evaluation

### Publication Support
- Journal manuscript preparation
- Peer review processes
- Grant application support
- Conference presentations

## 🔬 Scientific Validation

This tool implements the original Newcastle-Ottawa Scale criteria as published by:
- Wells GA, Shea B, O'Connell D, et al. The Newcastle-Ottawa Scale (NOS) for assessing the quality of nonrandomised studies in meta-analyses.

### Compliance
- ✅ Original NOS criteria implementation
- ✅ PRISMA guidelines compatibility
- ✅ Cochrane Handbook recommendations
- ✅ GRADE approach integration

## 📈 Performance

### System Requirements
- **Minimum**: 2GB RAM, Python 3.8+
- **Recommended**: 4GB RAM, Python 3.9+
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)

### Scalability
- Supports 1000+ studies per session
- Real-time calculations for up to 100 studies
- Efficient memory usage with large datasets
- Optimized for publication-size systematic reviews

## 🛡️ Data Privacy

- **Local Processing**: All data processed locally, no server uploads
- **Session Storage**: Data stored in browser session only
- **Export Control**: Users control all data exports
- **No Tracking**: No analytics or tracking implemented

## 📞 Support

### Getting Help
- 📧 Email: [your-email@domain.com]
- 💬 Issues: [GitHub Issues](https://github.com/your-username/nos-assessment-tool/issues)
- 📖 Documentation: [Wiki](https://github.com/your-username/nos-assessment-tool/wiki)
- 🎥 Video Tutorials: [YouTube Channel](https://youtube.com/your-channel)

### Reporting Bugs
Please include:
- Operating system and version
- Python version
- Browser information
- Steps to reproduce
- Screenshots (if applicable)

## 🗺️ Roadmap

### Version 2.1 (Planned)
- [ ] Multi-language support
- [ ] Template management system
- [ ] Advanced statistical tests
- [ ] Custom quality thresholds

### Version 3.0 (Future)
- [ ] Collaborative assessment features
- [ ] API integration capabilities
- [ ] Machine learning quality prediction
- [ ] Advanced reporting formats

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Newcastle-Ottawa Scale developers
- Streamlit development team
- Open source community contributors
- Systematic review methodology experts
- Beta testers and early adopters

## 📚 Citation

If you use this tool in your research, please cite:

```bibtex
@software{saddique2024nos,
  title={Newcastle-Ottawa Scale Assessment Tool: Advanced Systematic Risk of Bias Assessment},
  author={Saddique, Muhammad Nabeel},
  year={2024},
  url={https://github.com/your-username/nos-assessment-tool},
  version={2.0}
}
```

## 🔗 Related Projects

- [Robvis](https://github.com/mcguinlu/robvis) - Risk of bias visualization
- [RevMan](https://training.cochrane.org/online-learning/core-software-cochrane-reviews/revman) - Cochrane systematic review software
- [GRADE](https://www.gradeworkinggroup.org/) - Evidence quality assessment

---

<div align="center">

**📊 Newcastle-Ottawa Scale Assessment Tool v2.0**

*Developed for systematic review and meta-analysis research*

© 2024 Muhammad Nabeel Saddique | Nibras Research Academy

*Advanced bias assessment for evidence-based medicine*

[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red?style=flat-square&logo=streamlit)](https://streamlit.io)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue?style=flat-square&logo=python)](https://python.org)
[![For Research](https://img.shields.io/badge/For-Research-green?style=flat-square&logo=academia)](https://github.com/your-username/nos-assessment-tool)

</div>