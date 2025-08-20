# StopOdds Privacy Policy

**Last Updated:** [Date]

## Overview

StopOdds is committed to protecting your privacy. We collect minimal, anonymous data to estimate fare inspection rates on Melbourne public transport. This policy explains what we collect, how we use it, and how we protect it.

## What We Collect

### Mandatory Data
- **Trip count**: Number of public transport trips in the last 30 days (1-200)
- **Stop count**: Number of times you were checked by fare inspectors (0 to trip count)

### Optional Demographic Data
- Age bracket (18-24, 25-34, 35-44, 45+)
- Gender (Male, Female, Nonbinary, Prefer not to say)
- Ethnicity (predefined categories relevant to Australia)
- Skin tone (Light, Medium, Dark, Prefer not to say)
- Height bracket (<160cm, 160-175cm, 175-190cm, >190cm)
- Visible disability (Yes/No/Prefer not to say)
- Concession/MIPE status (Yes/No/Prefer not to say)

### Technical Data
- **User agent hash**: Daily-rotated, salted hash for basic fraud detection
- **Submission timestamp**: When you submitted your data

## What We Do NOT Collect

- Names, emails, or any personal identifiers
- IP addresses (stripped by our CDN)
- Location data or GPS coordinates
- Station names or specific routes
- Free-text responses
- Cookies that track individuals
- Browser fingerprints beyond user agent

## How We Use Your Data

### Statistical Analysis
- Calculate stop rates per 100 trips by demographic group
- Compute Incidence Rate Ratios (IRR) with confidence intervals
- Train statistical models (Poisson, Negative Binomial, optional LightGBM)
- Generate personal risk estimates

### Public Reporting
- Publish aggregated statistics with groups ≥50 people (k-anonymity)
- Share methodology and model performance metrics
- Provide open access to aggregated data meeting privacy thresholds

### Quality Assurance
- Detect anomalous submissions (e.g., extreme values)
- Prevent spam and fraudulent data
- Validate data integrity

## Privacy Protection Measures

### k-Anonymity
- Groups with <50 respondents are suppressed from public display
- No cross-tabulations that could identify individuals
- Conservative binning of continuous variables

### Data Minimization
- Collect only essential data for statistical analysis
- No storage of unnecessary metadata
- Automatic data expiry

### Technical Safeguards
- Database encryption at rest and in transit
- Access controls and audit logging
- Regular security updates and monitoring
- No tracking cookies or analytics that identify users

## Data Retention

### Raw Submissions
- Stored for maximum 12 months
- Used for model retraining and validation
- Automatically deleted after retention period

### Aggregated Data
- Retained indefinitely for research value
- Contains no individually identifiable information
- Published openly when meeting k-anonymity thresholds

## Data Sharing

### What We Share
- Aggregated statistics meeting privacy thresholds
- Methodology and code (open source)
- Academic research findings

### What We Never Share
- Individual submission data
- Raw demographic information
- Any data that could identify individuals
- Data with commercial partners

## Your Rights

### Australian Privacy Principles (APP)
StopOdds complies with the Privacy Act 1988 and Australian Privacy Principles:

- **APP 1**: Open and transparent management
- **APP 2**: Anonymity and pseudonymity options
- **APP 3**: Collection of solicited personal information
- **APP 4**: Dealing with unsolicited personal information
- **APP 5**: Notification of collection

### Your Choices
- All demographic data is optional
- No account creation required
- No email signup or contact details needed
- Data cannot be linked back to you after submission

### Contact
Since we collect anonymous data, we cannot identify or modify individual submissions. If you have concerns about our privacy practices, contact: [privacy@stopodds.com.au]

## Security

### Technical Measures
- HTTPS encryption for all communications
- Database access controls and monitoring
- Regular security audits and updates
- Incident response procedures

### Organizational Measures
- Privacy by design principles
- Regular staff training
- Data minimization policies
- Third-party security assessments

## Changes to This Policy

We may update this privacy policy to reflect changes in our practices or legal requirements. We will:
- Post updated policies on our website
- Highlight material changes
- Maintain version history

## Compliance

### Relevant Laws
- Privacy Act 1988 (Commonwealth)
- Australian Privacy Principles
- General Data Protection Regulation (GDPR) for EU visitors

### Data Impact Assessment
A comprehensive Privacy Impact Assessment (PIA) is available in our public repository, detailing:
- Risk identification and mitigation
- Privacy engineering measures
- Compliance verification
- Ongoing monitoring procedures

## Contact Information

**Privacy Officer**: [Name]  
**Email**: privacy@stopodds.com.au  
**Address**: [If required]

For general inquiries: info@stopodds.com.au

---

**Note**: StopOdds is a public-interest project focused on transport equity research. We are not affiliated with gambling or betting services despite our name.