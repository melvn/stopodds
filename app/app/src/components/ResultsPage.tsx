'use client';

import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Grid,
  Alert,
  Chip,
  Divider,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  Button,
} from '@mui/material';
import {
  BarChart,
  Analytics,
  Groups,
  TrendingUp,
  Info,
  Home,
} from '@mui/icons-material';
import Logo from './Logo';

interface GroupData {
  group_key: string;
  n_people: number;
  n_trips: number;
  n_stops: number;
  rate_per_100: number;
  irr_vs_ref?: number;
  confidence_interval?: [number, number];
}

interface OverviewData {
  total_submissions: number;
  total_trips: number;
  total_stops: number;
  groups: GroupData[];
}

interface MethodsData {
  model_type: string;
  last_trained: string;
  sample_size: number;
  metrics: Record<string, any>;
}

export default function ResultsPage() {
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [methods, setMethods] = useState<MethodsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [overviewRes, methodsRes] = await Promise.all([
          fetch('/api/overview'),
          fetch('/api/methods')
        ]);

        if (!overviewRes.ok || !methodsRes.ok) {
          throw new Error('Failed to fetch data');
        }

        const overviewData = await overviewRes.json();
        const methodsData = await methodsRes.json();

        setOverview(overviewData);
        setMethods(methodsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatGroupKey = (key: string) => {
    const [field, value] = key.split('=');
    const fieldNames: Record<string, string> = {
      'age_bracket': 'Age',
      'ethnicity': 'Ethnicity',
      'gender': 'Gender',
      'concession': 'Concession Status',
      'skin_tone': 'Skin Tone',
      'height_bracket': 'Height'
    };
    return `${fieldNames[field] || field}: ${value}`;
  };

  const getRiskLevel = (rate: number) => {
    if (rate < 5) return { label: 'Low', color: 'success' as const };
    if (rate < 10) return { label: 'Moderate', color: 'warning' as const };
    return { label: 'High', color: 'error' as const };
  };

  if (loading) {
    return (
      <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
        <Container maxWidth="lg">
          <Typography variant="h4" align="center" gutterBottom>
            Loading Results...
          </Typography>
          <LinearProgress />
        </Container>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
        <Container maxWidth="lg">
          <Alert severity="error">
            Error loading results: {error}
          </Alert>
        </Container>
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="lg">
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
            <Logo size="large" showText={true} />
          </Box>
          <Typography variant="h4" component="h1" gutterBottom sx={{ mt: 2 }}>
            Results Dashboard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            Melbourne Public Transport Fare Inspection Analysis
          </Typography>
          <Button
            href="/"
            startIcon={<Home />}
            variant="outlined"
            sx={{ mt: 2 }}
          >
            Submit Your Data
          </Button>
        </Box>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Groups sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                <Typography variant="h4" component="div">
                  {overview?.total_submissions || 0}
                </Typography>
                <Typography color="text.secondary">
                  Total Submissions
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <TrendingUp sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                <Typography variant="h4" component="div">
                  {overview?.total_trips.toLocaleString() || 0}
                </Typography>
                <Typography color="text.secondary">
                  Total Trips Recorded
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Analytics sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                <Typography variant="h4" component="div">
                  {overview?.total_stops.toLocaleString() || 0}
                </Typography>
                <Typography color="text.secondary">
                  Total Inspections
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {methods && (
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                <BarChart sx={{ mr: 1, verticalAlign: 'middle' }} />
                Current Model
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Model Type
                  </Typography>
                  <Typography variant="h6">
                    {methods.model_type.charAt(0).toUpperCase() + methods.model_type.slice(1)}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Sample Size
                  </Typography>
                  <Typography variant="h6">
                    {methods.sample_size.toLocaleString()} submissions
                  </Typography>
                </Grid>
                {methods.last_trained && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Last Trained
                    </Typography>
                    <Typography variant="body1">
                      {new Date(methods.last_trained).toLocaleDateString()}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        )}

        {overview && overview.groups.length > 0 ? (
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Stop Rates by Demographic Group
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Rate per 100 trips with 95% confidence intervals. Groups with fewer than 50 respondents are suppressed for privacy.
              </Typography>
              
              <List>
                {overview.groups
                  .sort((a, b) => b.rate_per_100 - a.rate_per_100)
                  .map((group, index) => {
                    const risk = getRiskLevel(group.rate_per_100);
                    return (
                      <Box key={group.group_key}>
                        <ListItem sx={{ py: 2 }}>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Typography variant="subtitle1">
                                  {formatGroupKey(group.group_key)}
                                </Typography>
                                <Chip 
                                  label={risk.label} 
                                  color={risk.color} 
                                  size="small" 
                                />
                              </Box>
                            }
                            secondary={
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="h6" color="primary">
                                  {group.rate_per_100.toFixed(1)}% 
                                  {group.confidence_interval && (
                                    <Typography variant="body2" component="span" color="text.secondary">
                                      {' '}(CI: {group.confidence_interval[0]?.toFixed(1)}% - {group.confidence_interval[1]?.toFixed(1)}%)
                                    </Typography>
                                  )}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {group.n_people} people, {group.n_trips.toLocaleString()} trips, {group.n_stops} stops
                                  {group.irr_vs_ref && (
                                    <> • IRR: {group.irr_vs_ref.toFixed(2)}x</>
                                  )}
                                </Typography>
                                <LinearProgress 
                                  variant="determinate" 
                                  value={Math.min(group.rate_per_100 * 5, 100)} 
                                  sx={{ mt: 1, height: 6, borderRadius: 3 }}
                                />
                              </Box>
                            }
                          />
                        </ListItem>
                        {index < overview.groups.length - 1 && <Divider />}
                      </Box>
                    );
                  })}
              </List>
            </CardContent>
          </Card>
        ) : (
          <Alert severity="info" sx={{ mb: 4 }}>
            No group statistics available yet. More data is needed to generate reliable demographic breakdowns.
          </Alert>
        )}

        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              <Info sx={{ mr: 1, verticalAlign: 'middle' }} />
              Methodology
            </Typography>
            <Typography variant="body1" paragraph>
              StopOdds uses Poisson regression with exposure offsets to model stop counts while accounting for different trip frequencies. 
              Coefficients are reported as Incidence Rate Ratios (IRR) with 95% confidence intervals.
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              • Groups with fewer than 50 respondents are suppressed for privacy<br/>
              • IRR = 1.0 indicates no effect relative to reference group<br/>
              • IRR &gt; 1.0 indicates higher inspection rates<br/>
              • IRR &lt; 1.0 indicates lower inspection rates
            </Typography>
            <Alert severity="warning">
              <Typography variant="body2">
                This data represents self-reported experiences and may not reflect the complete picture of fare inspection practices. 
                Results should be interpreted with caution and in context of broader transport equity discussions.
              </Typography>
            </Alert>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
}