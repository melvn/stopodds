'use client';

import { useState, useEffect } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Alert,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
} from '@mui/material';
import {
  CheckCircle,
  Analytics,
  Security,
  Public,
  Code,
  Refresh,
} from '@mui/icons-material';

interface MaterialSuccessScreenProps {
  onReset: () => void;
  personalEstimate?: any;
}

interface OverviewData {
  total_submissions: number;
  total_trips: number;
  total_stops: number;
}

export default function MaterialSuccessScreen({ onReset, personalEstimate }: MaterialSuccessScreenProps) {
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);

  useEffect(() => {
    // Fetch population statistics for comparison
    fetch('/api/overview')
      .then(res => res.json())
      .then(data => setOverviewData(data))
      .catch(err => console.error('Failed to fetch overview data:', err));
  }, []);
  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="sm">
        <Card elevation={3}>
          <CardContent sx={{ p: 4, textAlign: 'center' }}>
            {/* Success Icon */}
            <Box sx={{ mb: 3 }}>
              <CheckCircle sx={{ fontSize: 80, color: 'success.main' }} />
            </Box>
            
            <Typography variant="h4" component="h1" gutterBottom>
              Thank You! 🎉
            </Typography>
            
            <Typography variant="subtitle1" color="text.secondary" gutterBottom>
              Your data has been successfully submitted to StopOdds
            </Typography>

            {/* Personal Estimate Card */}
            {personalEstimate && (
              <Paper elevation={2} sx={{ p: 3, mt: 3, mb: 3, bgcolor: 'primary.50', border: '2px solid', borderColor: 'primary.200' }}>
                <Typography variant="h6" gutterBottom color="primary.main">
                  Your Personal Risk Estimate
                </Typography>
                <Typography variant="h4" color="primary.dark" gutterBottom>
                  {personalEstimate.probability.toFixed(1)}%
                </Typography>
                
                {overviewData && (() => {
                  const userRate = personalEstimate.probability;
                  const populationRate = (overviewData.total_stops / overviewData.total_trips) * 100;
                  const multiplier = userRate / populationRate;
                  
                  let comparisonText = '';
                  let comparisonColor = 'text.secondary';
                  
                  if (multiplier > 1.5) {
                    comparisonText = `You're ${multiplier.toFixed(1)}x more likely to be stopped than the average person`;
                    comparisonColor = 'error.main';
                  } else if (multiplier > 1.1) {
                    comparisonText = `You're ${multiplier.toFixed(1)}x more likely to be stopped than average`;
                    comparisonColor = 'warning.main';
                  } else if (multiplier < 0.9) {
                    comparisonText = `You're ${(1/multiplier).toFixed(1)}x less likely to be stopped than average`;
                    comparisonColor = 'success.main';
                  } else {
                    comparisonText = "Your risk is close to the population average";
                    comparisonColor = 'text.primary';
                  }
                  
                  return (
                    <Typography variant="body1" color={comparisonColor} gutterBottom sx={{ fontWeight: 'medium', mb: 1 }}>
                      {comparisonText}
                    </Typography>
                  );
                })()}
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Per 100 trips
                  {overviewData && (
                    <> • Population average: {((overviewData.total_stops / overviewData.total_trips) * 100).toFixed(1)}%</>
                  )}
                  {personalEstimate.confidence_interval && (
                    <> • Range: {personalEstimate.confidence_interval[0].toFixed(1)}%-{personalEstimate.confidence_interval[1].toFixed(1)}%</>
                  )}
                </Typography>
                {personalEstimate.explanation && personalEstimate.explanation.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Key Factors:
                    </Typography>
                    <List dense>
                      {personalEstimate.explanation.map((factor: string, index: number) => (
                        <ListItem key={index} sx={{ py: 0 }}>
                          <ListItemText 
                            primary={`• ${factor}`}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
                {personalEstimate.is_baseline && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <Typography variant="caption">
                      This is a baseline estimate. Accuracy will improve as more data is collected.
                    </Typography>
                  </Alert>
                )}
              </Paper>
            )}

            {/* What happens next */}
            <Paper elevation={1} sx={{ p: 3, mt: 3, mb: 3, bgcolor: 'primary.50' }}>
              <Typography variant="h6" gutterBottom>
                What happens next?
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Analytics color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Your anonymous data joins our growing dataset"
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Analytics color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="We'll analyze patterns to calculate stop rates by demographic group"
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Public color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Results will be published transparently with confidence intervals"
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Code color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="All methodology and code will be made publicly available"
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              </List>
            </Paper>

            {/* Action Buttons */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6}>
                <Button
                  href="/results"
                  variant="contained"
                  color="primary"
                  fullWidth
                  startIcon={<Analytics />}
                >
                  View Results
                </Button>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Button
                  href="/methodology"
                  variant="outlined"
                  color="primary"
                  fullWidth
                  startIcon={<Code />}
                >
                  Our Methodology
                </Button>
              </Grid>
            </Grid>

            <Button
              onClick={onReset}
              color="secondary"
              startIcon={<Refresh />}
            >
              Submit another response
            </Button>
          </CardContent>
        </Card>

        {/* Privacy Reminder */}
        <Box sx={{ mt: 3 }}>
          <Alert severity="success" icon={<Security />}>
            <Typography variant="subtitle2" gutterBottom>
              Privacy Protected
            </Typography>
            <Typography variant="caption">
              Your submission contains no personally identifiable information and cannot be traced back to you. 
              Groups with fewer than 50 respondents will be suppressed from public results to ensure privacy.
            </Typography>
          </Alert>
        </Box>
      </Container>
    </Box>
  );
}