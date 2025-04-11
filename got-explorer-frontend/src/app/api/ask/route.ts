import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log("Received request body:", body);
    
    // Extract question - handle both your frontend format and direct API calls
    const question = body.text || (body.data && body.data[0]) || "";
    console.log("Extracted question:", question);
    
    // Make request to Hugging Face in the proper format
    const response = await fetch('https://willhcurry-gotbot.hf.space/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        data: [question] 
      })
    });
    
    if (!response.ok) {
      throw new Error(`Hugging Face API returned ${response.status}`);
    }
    
    const data = await response.json();
    console.log("Response from HF:", data);
    
    // The Hugging Face API returns in this format: { data: [{ response: "..." }] }
    // Extract the response text
    let answer = "No response received";
    if (data.data && Array.isArray(data.data) && data.data[0]) {
      answer = data.data[0].response || data.data[0];
    }
    
    return NextResponse.json({
      status: 'success',
      response: answer
    });
  } catch (error) {
    console.error('Error connecting to Hugging Face:', error);
    
    // Fall back to local API
    try {
      const body = await request.json();
      const fallbackResponse = await fetch(new URL('/api/ask', request.url), {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ text: body.text || (body.data && body.data[0]) || "" }),
      });
      
      return fallbackResponse;
    } catch (fallbackError) {
      console.error('Even fallback failed:', fallbackError);
      return NextResponse.json({
        status: 'error',
        response: "I'm having trouble connecting to my knowledge base. Please try again later."
      });
    }
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}
