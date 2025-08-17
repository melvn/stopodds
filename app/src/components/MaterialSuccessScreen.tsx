'use client';

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
}

export default function MaterialSuccessScreen({ onReset }: MaterialSuccessScreenProps) {
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