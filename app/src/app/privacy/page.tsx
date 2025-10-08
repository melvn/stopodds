'use client';

import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Divider,
  Alert,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { ArrowBack, ExpandMore, Security, Visibility, DataUsage } from '@mui/icons-material';
import Logo from '@/components/Logo';

export default function PrivacyPage() {
  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="md">
        {/* Header */}
        <Card sx={{ mb: 4 }}>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
              <Logo size="large" showText={true} />
            </Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Privacy Policy
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              How we collect, use, and protect your data
            </Typography>
            <Button
              href="/"
              startIcon={<ArrowBack />}
              variant="outlined"
              sx={{ mt: 3 }}
            >
              Back to Form
            </Button>
          </CardContent>
        </Card>

        {/* Overview */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              <Security sx={{ mr: 1, verticalAlign: 'middle' }} />
              Privacy-First Approach
            </Typography>
            <Alert severity="info" sx={{ mb: 3 }}>
              StopOdds is designed with privacy at its core. We collect only anonymous data and use statistical methods to protect individual privacy.
            </Alert>
            <Typography variant="body1" paragraph>
              StopOdds is a public-interest, non-profit project that helps understand fare inspection patterns on Melbourne public transport. We are committed to transparency and protecting your privacy through technical and procedural safeguards.
            </Typography>
          </CardContent>
        </Card>

        {/* What We Collect */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              <DataUsage sx={{ mr: 1, verticalAlign: 'middle' }} />
              What We Collect
            </Typography>
            <Typography variant="body1" paragraph>
              We collect only anonymous trip and demographic data:
            </Typography>
            
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Required Information:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText 
                  primary="Trip count" 
                  secondary="How many public transport trips you took in the specified period" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Stop count" 
                  secondary="How many times you were checked during those trips" 
                />
              </ListItem>
            </List>

            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Optional Demographic Information:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText primary="Age bracket (e.g., 18-24, 25-34)" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Gender identity" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Ethnicity" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Skin tone" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Height bracket" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Visible disability status" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Concession card status" />
              </ListItem>
            </List>

            <Alert severity="success" sx={{ mt: 3 }}>
              <Typography variant="body2">
                <strong>What we DON'T collect:</strong> No names, addresses, contact details, device identifiers, IP addresses, or any other personally identifiable information.
              </Typography>
            </Alert>
          </CardContent>
        </Card>

        {/* How We Use Data */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              How We Use Your Data
            </Typography>
            <Typography variant="body1" paragraph>
              Your anonymous data is used to:
            </Typography>
            <List>
              <ListItem>
                <ListItemText 
                  primary="Calculate stop rates by demographic group" 
                  secondary="We compute inspection rates per 100 trips for different demographic groups" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Generate statistical models" 
                  secondary="We use Poisson/Negative Binomial regression to identify patterns" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Provide personal risk estimates" 
                  secondary="You receive an estimate based on your demographic traits" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Publish aggregate statistics" 
                  secondary="Public results help inform transport equity discussions" 
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        {/* Privacy Protections */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              <Visibility sx={{ mr: 1, verticalAlign: 'middle' }} />
              Privacy Protections
            </Typography>
            
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">K-Anonymity Protection</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body1" paragraph>
                  Any demographic group with fewer than 50 respondents is automatically suppressed from public results. This prevents identification of individuals in small groups.
                </Typography>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">No Cross-tabulation</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body1" paragraph>
                  We don't publish detailed cross-tabulations that could reveal information about small subgroups, even if individual groups meet the 50-person threshold.
                </Typography>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">Data Retention</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body1" paragraph>
                  Raw submission data is retained for 12 months for model training and validation. After this period, only aggregated statistics are kept, with no way to trace back to individual submissions.
                </Typography>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">Security Measures</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body1" paragraph>
                  Data is stored securely with encryption in transit and at rest. Access is strictly limited to automated processing systems. We use industry-standard security practices and regular backups.
                </Typography>
              </AccordionDetails>
            </Accordion>
          </CardContent>
        </Card>

        {/* Legal Basis */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Legal Basis & Compliance
            </Typography>
            <Typography variant="body1" paragraph>
              This project operates under the Australian Privacy Principles (APP) with specific focus on:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText 
                  primary="APP 1: Open and transparent management" 
                  secondary="This privacy policy and our methodology are publicly available" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="APP 2: Anonymity and pseudonymity" 
                  secondary="All data collection is anonymous with no identifying information" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="APP 3: Collection of solicited personal information" 
                  secondary="We only collect information necessary for our stated statistical purposes" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="APP 4: Data quality" 
                  secondary="We implement validation and quality checks on submitted data" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="APP 5: Data security" 
                  secondary="Appropriate technical and organisational measures protect your data" 
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        {/* Your Rights */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Your Rights
            </Typography>
            <Typography variant="body1" paragraph>
              Since we collect only anonymous data, traditional data subject rights (like access or deletion requests) don't apply in the usual way. However:
            </Typography>
            <List>
              <ListItem>
                <ListItemText 
                  primary="Participation is voluntary" 
                  secondary="You can choose what information to provide" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="No tracking or profiling" 
                  secondary="We don't build individual profiles or track users across sessions" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Open methodology" 
                  secondary="Our statistical methods and code are transparent and auditable" 
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        {/* Contact */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Contact & Questions
            </Typography>
            <Typography variant="body1" paragraph>
              If you have questions about this privacy policy or our data practices:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText 
                  primary="Privacy concerns: privacy@stopodds.com.au" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="General questions: info@stopodds.com.au" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Technical issues: Submit on GitHub Issues" 
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        {/* Disclaimer */}
        <Alert severity="info">
          <Typography variant="body2">
            <strong>Important:</strong> StopOdds is a public-interest statistics project about fare inspections. Despite the name, it is not gambling-related and doesn't provide betting advice or services.
          </Typography>
        </Alert>

        <Box sx={{ textAlign: 'center', mt: 4, mb: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Last updated: August 2025 • This policy may be updated as the project evolves
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}