import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log("Request to Hugging Face:", body);
    
    // Extract the question from whatever format it comes in
    const question = body.text || (body.data && body.data[0]) || "";
    
    if (!question) {
      return NextResponse.json({
        status: 'error',
        response: "I didn't receive a question. Please try again."
      });
    }
    
    // Make the request to Hugging Face
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
      throw new Error(`Hugging Face API returned status ${response.status}`);
    }
    
    const data = await response.json();
    console.log("Response from Hugging Face:", data);
    
    // Extract the response text properly
    let answer = "No response received";
    if (data.data && Array.isArray(data.data) && data.data[0]) {
      answer = data.data[0].response || data.data[0];
    }
    
    return NextResponse.json({
      status: 'success',
      response: answer
    });
  } catch (error) {
    console.error('Error connecting to Hugging Face API:', error);
    return NextResponse.json({
      status: 'error',
      response: "I'm having trouble connecting to my knowledge base."
    }, { status: 502 });
  }
}
