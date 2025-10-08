import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Sanitize data: convert "PreferNot" to null for fields that don't support it
    // Based on database constraints, convert all "PreferNot" values to null
    const sanitizedBody = { ...body };
    
    // Convert all "PreferNot" values to null since database enums don't support them
    Object.keys(sanitizedBody).forEach(key => {
      if (sanitizedBody[key] === 'PreferNot') {
        sanitizedBody[key] = null;
      }
    });
    
    const response = await fetch(`${API_BASE_URL}/api/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': request.headers.get('user-agent') || 'StopOdds-Frontend',
      },
      body: JSON.stringify(sanitizedBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend API error:', response.status, errorText);
      return NextResponse.json(
        { error: 'Submission failed', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}