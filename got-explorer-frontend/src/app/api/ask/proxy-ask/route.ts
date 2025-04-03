import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await fetch('https://willhcurry-gotbot.hf.space/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.HF_TOKEN}`
      },
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      console.error('HF API error:', response.status, await response.text());
      return NextResponse.json(
        { error: 'Failed to fetch from Hugging Face' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
