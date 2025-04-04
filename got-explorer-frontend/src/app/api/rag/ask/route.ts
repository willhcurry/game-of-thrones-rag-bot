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
        data: [body.text || "Tell me about Game of Thrones"] 
      })
    });
    
    console.log("Sending request to HF:", JSON.stringify({ data: [body.text || "Tell me about Game of Thrones"] }));
    
    if (!response.ok) {
      console.error('HF API error:', response.status, await response.text());
      return NextResponse.json(
        { error: 'Failed to fetch from Hugging Face' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log("Raw response:", data);
    
    let answer;
    if (data.error) {
      answer = `Error: ${data.error}`;
    } else if (data.data && Array.isArray(data.data) && data.data[0]) {
      answer = data.data[0].response || data.data[0];
    } else {
      answer = "Received unexpected response format from knowledge base";
    }
    
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
