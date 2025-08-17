'use client';

import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Alert,
  Divider,
  Paper,
  Grid,
} from '@mui/material';
import {
  ArrowBack,
  ExpandMore,
  Analytics,
  Timeline,
  Security,
  Assessment,
  Science,
  TrendingUp,
} from '@mui/icons-material';
import Logo from '@/components/Logo';

export default function MethodologyPage() {
  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="lg">
        {/* Header */}
        <Card sx={{ mb: 4 }}>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
              <Logo size="large" showText={true} />
            </Box>
            <Typography variant="h3" component="h1" gutterBottom>
              Methodology
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
              How we analyze fare inspection patterns on Melbourne public transport
            </Typography>
            <Button
              href="/"
              startIcon={<ArrowBack />}
              variant="outlined"
              sx={{ mr: 2 }}
            >
              Back to Form
            </Button>
            <Button
              href="/results"
              startIcon={<Analytics />}
              variant="contained"
            >
              View Results
            </Button>
          </CardContent>
        </Card>

        {/* Overview */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h4" gutterBottom>
              <Science sx={{ mr: 1, verticalAlign: 'middle' }} />
              Statistical Approach
            </Typography>
            <Alert severity="info" sx={{ mb: 3 }}>
              StopOdds uses rigorous statistical methods to identify patterns in fare inspection data while protecting individual privacy.
            </Alert>
            <Typography variant="body1" paragraph>
              Our analysis employs <strong>Poisson regression with exposure offsets</strong> to model stop counts while accounting for different trip frequencies across demographic groups. This approach allows us to calculate meaningful inspection rates and identify statistically significant differences between groups.
            </Typography>
          </CardContent>
        </Card>

        {/* Grid Layout for Key Concepts */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Timeline sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Exposure Modeling
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  We use trip counts as exposure variables to calculate rates per 100 trips, accounting for varying travel patterns.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Assessment sx={{ fontSize: 40, color: 'secondary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Incidence Rate Ratios
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  We report IRRs with 95% confidence intervals to show relative inspection rates between demographic groups.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Security sx={{ fontSize: 40, color: 'success.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Privacy Protection
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  K-anonymity ensures groups with fewer than 50 respondents are suppressed from public results.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Detailed Methodology */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h4" gutterBottom>
              Detailed Methods
            </Typography>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">1. Data Collection</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body1" paragraph>
                  We collect anonymous self-reported data including:
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Trip counts" 
                      secondary="Number of public transport journeys in the last 30 days" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Stop counts" 
                      secondary="Number of times fare inspectors checked tickets during those trips" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Demographic information" 
                      secondary="Optional characteristics including age, gender, ethnicity, height, etc." 
                    />
                  </ListItem>
                </List>
                <Alert severity="warning" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    <strong>Important:</strong> All data is self-reported and voluntary. Results represent patterns in reported experiences, not necessarily complete inspection practices.
                  </Typography>
                </Alert>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">2. Statistical Modeling</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body1" paragraph>
                  We use <strong>Poisson regression</strong> to model the relationship between demographic characteristics and inspection frequency:
                </Typography>
                <Paper sx={{ p: 2, bgcolor: 'grey.50', mb: 2 }}>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    log(E[stops_i]) = log(trips_i) + β₀ + β₁×age_i + β₂×gender_i + ... + βₖ×trait_k
                  </Typography>
                </Paper>
                <Typography variant="body1" paragraph>
                  Where:
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="E[stops_i]" 
                      secondary="Expected number of stops for person i" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="log(trips_i)" 
                      secondary="Natural log of trips as exposure offset" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="β coefficients" 
                      secondary="Effect of each demographic characteristic" 
                    />
                  </ListItem>
                </List>
                <Typography variant="body1" paragraph sx={{ mt: 2 }}>
                  If overdispersion is detected (variance &gt; mean), we switch to a <strong>Negative Binomial model</strong> for more robust estimates.
                </Typography>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">3. Interpreting Results</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body1" paragraph>
                  Model coefficients are converted to <strong>Incidence Rate Ratios (IRRs)</strong> for easier interpretation:
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="IRR = 1.0" 
                      secondary="No difference from reference group" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="IRR > 1.0" 
                      secondary="Higher inspection rate than reference group" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="IRR < 1.0" 
                      secondary="Lower inspection rate than reference group" 
                    />
                  </ListItem>
                </List>
                <Typography variant="body1" paragraph sx={{ mt: 2 }}>
                  All results include <strong>95% confidence intervals</strong>. If the confidence interval includes 1.0, the difference is not statistically significant.
                </Typography>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">4. Privacy & Ethics</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body1" paragraph>
                  We implement multiple privacy protections:
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="K-anonymity" 
                      secondary="Groups with <50 respondents are suppressed from results" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="No cross-tabulation" 
                      secondary="We don't publish detailed breakdowns that could identify small subgroups" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Data retention limits" 
                      secondary="Raw data deleted after 12 months, only aggregates retained" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Anonymous collection" 
                      secondary="No personally identifiable information collected" 
                    />
                  </ListItem>
                </List>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">5. Model Validation</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body1" paragraph>
                  We validate our models through:
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Goodness-of-fit tests" 
                      secondary="Chi-square tests to check model appropriateness" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Overdispersion testing" 
                      secondary="Checking if Negative Binomial model is needed" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Residual analysis" 
                      secondary="Examining patterns in model residuals" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Sensitivity analysis" 
                      secondary="Testing robustness to different model specifications" 
                    />
                  </ListItem>
                </List>
              </AccordionDetails>
            </Accordion>
          </CardContent>
        </Card>

        {/* Model Information */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h4" gutterBottom>
              <TrendingUp sx={{ mr: 1, verticalAlign: 'middle' }} />
              Current Model Status
            </Typography>
            <Alert severity="info" sx={{ mb: 3 }}>
              The model is continuously updated as new data arrives. Minimum thresholds ensure statistical reliability.
            </Alert>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Activation Requirements
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="≥500 valid submissions" 
                      secondary="Ensures sufficient sample size for reliable estimates" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="≥100 total stops" 
                      secondary="Adequate events for Poisson modeling" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Multiple demographic groups" 
                      secondary="Enables meaningful comparisons" 
                    />
                  </ListItem>
                </List>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Quality Assurance
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Anomaly detection" 
                      secondary="Automatic flagging of unusual patterns (e.g., >100 trips/month)" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Data validation" 
                      secondary="Consistency checks and range validation" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Regular retraining" 
                      secondary="Model updated weekly with new data" 
                    />
                  </ListItem>
                </List>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Limitations */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h4" gutterBottom>
              Limitations & Considerations
            </Typography>
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="body2">
                This analysis has important limitations that users should understand when interpreting results.
              </Typography>
            </Alert>
            
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Data Limitations
            </Typography>
            <List>
              <ListItem>
                <ListItemText 
                  primary="Self-reported data" 
                  secondary="Results depend on voluntary responses which may not represent all transport users" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Recall bias" 
                  secondary="People may not perfectly remember inspection frequencies over 30 days" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Selection bias" 
                  secondary="Survey respondents may differ systematically from non-respondents" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Geographic coverage" 
                  secondary="Results may not be representative of all Melbourne transport routes/times" 
                />
              </ListItem>
            </List>

            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Statistical Considerations
            </Typography>
            <List>
              <ListItem>
                <ListItemText 
                  primary="Multiple comparisons" 
                  secondary="Testing many demographic groups increases chance of false discoveries" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Confounding variables" 
                  secondary="Unmeasured factors (route, time, behavior) may influence results" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Sample size variations" 
                  secondary="Some demographic groups may have limited representation" 
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        {/* Footer */}
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="body2" color="text.secondary" paragraph>
            For technical questions about our methodology, please contact us at methods@stopodds.com.au
          </Typography>
          <Typography variant="caption" color="text.secondary">
            This methodology is open source and available for review on GitHub
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}