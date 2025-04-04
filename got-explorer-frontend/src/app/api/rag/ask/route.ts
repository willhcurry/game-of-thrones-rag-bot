import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    console.log("Request received at /api/rag/ask:", body.text);
    
    const response = await fetch('https://willhcurry-gotbot.hf.space/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.HF_TOKEN}`
      },
      body: JSON.stringify({ 
        data: [body.text] 
      })
    });
    
    console.log("Sending request to HF:", JSON.stringify({ data: [body.text] }));
    
    if (!response.ok) {
      console.error('HF API error:', response.status, await response.text());
      return NextResponse.json(
        { error: 'Failed to fetch from Hugging Face' }, 
        { status: response.status }
      );
    }
    
    const rawData = await response.json();
    console.log("Raw response from Hugging Face:", JSON.stringify(rawData));
    
    const answer = 
      rawData.data?.[0]?.response || 
      rawData.data?.[0] || 
      (typeof rawData.data === 'string' ? rawData.data : null) ||
      "No response received";
    
    console.log("Extracted answer:", answer);
    
    return NextResponse.json({
      status: 'success',
      response: answer
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
